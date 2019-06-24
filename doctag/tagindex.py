import os
import sys
from collections import defaultdict
from itertools import product
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, List, Optional, Set, Tuple, Union

import boolean
import ujson
from doctag_cli.metamarkdown import MetaMarkdown


class TagIndex:
    def __init__(self, at: Optional[str] = None):
        self.tag_to_docs: DefaultDict[str, Set[str]] = DefaultDict(set)
        self.doc_to_tags: DefaultDict[str, Set[str]] = DefaultDict(set)
        self.algebra = boolean.BooleanAlgebra()
        self.at = at

    @property
    def tags(self):
        return set(self.tag_to_docs.keys())

    @property
    def docs(self):
        return set(self.doc_to_tags.keys())

    @property
    def conflicts(self) -> Set[str]:
        conflicts = set()
        for tag, docs in self.tag_to_docs.items():
            for doc in docs:
                if tag not in self.doc_to_tags[doc]:
                    conflicts.add(
                        f"'{doc}' in tag_to_docs['{tag}'] but '{tag}' not in doc_to_tags['{doc}']"
                    )
        for doc, tags in self.doc_to_tags.items():
            for tag in tags:
                if doc not in self.tag_to_docs[tag]:
                    conflicts.add(
                        f"'{tag}' in doc_to_tags['{doc}'] but '{doc}' not in tag_to_docs['{tag}']"
                    )
        return conflicts

    def get_docs(self, tag: str):
        if tag in self.tags:
            docs = {doc for doc in self.tag_to_docs[tag]}
        else:
            docs = set()
        return docs

    def tag(self, docs: Union[str, Iterable[str]], tags: Union[str, Iterable[str]]):
        docs_ = (
            docs if isinstance(docs, Iterable) and not isinstance(docs, str) else [docs]
        )
        tags_ = (
            tags if isinstance(tags, Iterable) and not isinstance(tags, str) else [tags]
        )
        if {"false", "true", "0", "1"} & {tag.lower() for tag in tags_}:
            raise ValueError(
                "'true', 'false', '0', and '1' are reserved names and cannot be used as tags."
            )
        tags_ = self._tag_validator(tags_)
        self._tag(docs=docs_, tags=tags_)
        self._tag_callback(docs=docs_, tags=tags_)

    def _tag(self, docs: Iterable[str], tags: Iterable[str]):
        for doc, tag in product(docs, tags):
            self.doc_to_tags[doc].add(tag)
            self.tag_to_docs[tag].add(doc)

    def untag(self, docs: Union[str, Iterable[str]], tags: Union[str, Iterable[str]]):
        docs_ = (
            docs if isinstance(docs, Iterable) and not isinstance(docs, str) else [docs]
        )
        tags_ = (
            tags if isinstance(tags, Iterable) and not isinstance(tags, str) else [tags]
        )
        for doc, tag in product(docs_, tags_):
            try:
                self.doc_to_tags[doc].remove(tag)
            except KeyError:
                pass
            try:
                self.tag_to_docs[tag].remove(doc)
            except KeyError:
                pass
            if not self.tag_to_docs[tag]:
                del self.tag_to_docs[tag]
            if not self.doc_to_tags[doc]:
                del self.doc_to_tags[doc]
        self._untag_callback(docs=docs_, tags=tags_)

    def remove_tag(self, tag: str):
        if tag not in self.tags:
            raise ValueError(f"Tag '{tag}' not found.")
        else:
            self.untag(docs=self.tag_to_docs[tag], tags=tag)

    def merge_tags(self, old_tags: Union[str, Iterable[str]], new_tag: str):
        old_tags_ = old_tags if isinstance(old_tags, list) else [old_tags]
        for old_tag in old_tags_:
            self.tag(docs=self.tag_to_docs[old_tag], tags=new_tag)
            self.remove_tag(old_tag)

    def rename_doc(self, old_doc_name: str, new_doc_name: str):
        if new_doc_name in self.docs:
            raise ValueError(f"Document named '{new_doc_name}' already exists.")
        elif old_doc_name not in self.docs:
            raise ValueError(f"Document named '{old_doc_name}' not found.")
        else:
            self.tag(docs=new_doc_name, tags=self.doc_to_tags[old_doc_name])
            self.untag(docs=old_doc_name, tags=self.doc_to_tags[old_doc_name])

    def remove_doc(self, doc_name: str):
        if doc_name not in self.docs:
            raise ValueError(f"Document '{doc_name}' not found.")
        else:
            self.untag(docs=doc_name, tags=self.doc_to_tags[doc_name])

    def to_json(self, at: Optional[str] = None):
        if at is None and self.at is not None:
            at = self.at
        elif self.at is None and self.at is not None:
            self.at = at
        serial = dict()
        dtt_size = sys.getsizeof(self.doc_to_tags)
        ttd_size = sys.getsizeof(self.tag_to_docs)
        ttd_bigger = ttd_size >= dtt_size
        if ttd_bigger:
            serial["doc_to_tags"] = self.doc_to_tags
        else:
            serial["tag_to_docs"] = self.tag_to_docs
        with open(str(at), "w") as to_file:
            ujson.dump(serial, to_file)

    @classmethod
    def from_json(cls, at: str) -> "TagIndex":
        with open(at, "r") as from_file:
            serial = ujson.load(from_file)
            ti = TagIndex(at=at)
            if "doc_to_tags" in serial.keys():
                ti.doc_to_tags.update(
                    {str(doc): set(tags) for doc, tags in serial["doc_to_tags"].items()}
                )
                for doc, tags in ti.doc_to_tags.items():
                    for tag in tags:
                        ti.tag_to_docs[str(tag)].add(doc)
            elif "tag_to_docs" in serial.keys():
                ti.tag_to_docs.update(
                    {str(tag): set(docs) for tag, docs in serial["tag_to_docs"].items()}
                )
                for tag, docs in ti.tag_to_docs.items():
                    for doc in docs:
                        ti.doc_to_tags[str(doc)].add(tag)
            else:
                raise ValueError(
                    "File does not contain 'tag_to_docs' or 'doc_to_tags' index."
                )
        return ti

    def query(self, query=str) -> set:
        return self._parse_query(query)

    def _parse_query(self, query: str) -> set:
        expression = self.algebra.parse(query).simplify()
        try:
            args = expression.args
            operator = expression.operator
        except AttributeError:
            return self.get_docs(expression.obj)
        return self._parse_expression(operator=operator, args=args)

    def _parse_expression(self, operator: str, args: list) -> set:
        if operator == "&":
            result = self._parse_expression_and(args)
        elif operator == "|":
            result = self._parse_expression_or(args)
        elif operator == "~":
            result = self._parse_expression_not(args[0])
        return result

    def _parse_expression_and(self, args: list) -> set:
        sub_results = []
        for arg in args:
            if isinstance(arg, boolean.Symbol):
                sub_result = self.get_docs(arg.obj)
            else:
                sub_result = self._parse_expression(
                    operator=arg.operator, args=arg.args
                )
            if len(sub_result) == 0:
                return set()
            else:
                sub_results.append(sub_result)
        return set.intersection(*sub_results)

    def _parse_expression_or(self, args: list) -> set:
        sub_results = []
        for arg in args:
            if isinstance(arg, boolean.Symbol):
                sub_result = self.get_docs(arg.obj)
            else:
                sub_result = self._parse_expression(
                    operator=arg.operator, args=arg.args
                )
            sub_results.append(sub_result)
        return set.union(*sub_results)

    def _parse_expression_not(self, arg) -> set:
        if isinstance(arg, boolean.Symbol):
            docs_with_tag = self.get_docs(arg.obj)
        else:
            docs_with_tag = self._parse_expression(operator=arg.operator, args=arg.args)
        return self.docs - docs_with_tag

    def _tag_callback(self, docs, tags):
        pass

    def _untag_callback(self, docs, tags):
        pass

    def _tag_validator(self, tags: Iterable[str]) -> Iterable[str]:
        return tags

    def __enter__(self):
        if not self.at:
            raise FileNotFoundError(
                f"{type(self).__name__} missing a read/write location 'at'"
            )
        return self

    def __exit__(self, etype, evalue, traceback):
        if not etype:
            self.to_json()
