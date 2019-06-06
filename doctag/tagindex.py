import boolean
import ujson
from typing import DefaultDict, Union, List, Iterable, Dict, Any, Tuple, Optional
from collections import defaultdict


def parse_tag(tag: str) -> Tuple[str, Optional[str]]:
    value: Optional[str]  # appease mypy
    if ":" in tag:
        try:
            value = tag.split(":")[1]
        except IndexError:
            value = None
        tag = tag.split(":")[0]
    else:
        value = None
    return (tag, value)


class TagIndex:
    def __init__(self):
        self.tag_to_docs: DefaultDict[str, set] = DefaultDict(set)
        self.doc_to_tags: DefaultDict[str, set] = DefaultDict(set)
        self.doc_tag_values: Dict[Tuple[str, str], Any] = {}
        self.algebra = boolean.BooleanAlgebra()

    @property
    def tags(self):
        return set(self.tag_to_docs.keys())

    @property
    def docs(self):
        return set(self.doc_to_tags.keys())

    def get_docs(self, tag: str):
        tag, value = parse_tag(tag)
        if value is not None:
            docs = {
                doc
                for doc in self.tag_to_docs[tag]
                if self.doc_tag_values.get((doc, tag), None) == value
            }
        else:
            docs = {doc for doc in self.tag_to_docs[tag]}
        return docs

    def tag(self, docs: Union[str, Iterable[str]], tags: Union[str, Iterable[str]]):
        docs_ = docs if isinstance(docs, Iterable) and not isinstance(docs,str) else [docs]
        tags_ = tags if isinstance(tags, Iterable) and not isinstance(tags,str) else [tags]
        product = ((doc, tag) for doc in docs_ for tag in tags_)
        for doc, tag in product:
            self._tag(doc=doc, tag=tag)

    def untag(self, docs: Union[str, Iterable[str]], tags: Union[str, Iterable[str]]):
        docs_ = docs if isinstance(docs, Iterable) and not isinstance(docs,str) else [docs]
        tags_ = tags if isinstance(tags, Iterable) and not isinstance(tags,str) else [tags]
        product = ((doc, tag) for doc in docs_ for tag in tags_)
        for doc, tag in product:
            self._untag(doc=doc, tag=tag)

    def merge(self, old_tags: Union[str, Iterable[str]], new_tag: str):
        old_tags_ = old_tags if isinstance(old_tags, list) else [old_tags]
        for old_tag in old_tags_:
            self._merge(old_tag=old_tag, new_tag=new_tag)

    def _merge(self, old_tag: str, new_tag: str):
        self.tag_to_docs[new_tag].add(self.tag_to_docs[old_tag])
        self.untag(docs=self.tag_to_docs[old_tag],tags=old_tag)

    def to_json(self, file_name: str, compact: bool = False):
        serial = {
            "doc_to_tags": self.doc_to_tags,
            "doc_tag_values": self.doc_tag_values,
        }
        if not compact:
            serial["tag_to_docs"] = self.tag_to_docs
        with open(file_name, "w") as to_file:
            ujson.dump(serial, to_file)

    @classmethod
    def from_json(cls, file_name: str) -> "TagIndex":
        with open(file_name, "r") as from_file:
            serial = ujson.load(from_file)
            ti = TagIndex()
            ti.doc_to_tags.update(
                {str(tag): set(docs) for tag, docs in serial["doc_to_tags"].items()}
            )
            ti.doc_tag_values = serial["doc_tag_values"]
            try:
                ti.tag_to_docs.update(
                    {str(doc): set(tags) for doc, tags in serial["tag_to_docs"].items()}
                )
            except KeyError:
                for doc, tags in ti.tag_to_docs.items():
                    for tag in tags:
                        ti.tag_to_docs[tag].add(doc)
        return ti

    def _tag(self, doc: str, tag: str):
        value: Optional[str] = None
        tag, value = parse_tag(tag)
        self.doc_to_tags[doc].add(tag)
        self.tag_to_docs[tag].add(doc)
        if value is not None:
            self.doc_tag_values[(doc, tag)] = value

    def _untag(self, doc: str, tag: str):
        tag, value = parse_tag(tag)
        self.doc_to_tags[doc].remove(tag)
        self.tag_to_docs[tag].remove(doc)
        if not self.tag_to_docs[tag]:
            del self.tag_to_docs[tag]
        if value is not None:
            del self.doc_tag_values[(doc, tag)]

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
        all_docs = set(self.doc_to_tags.keys())
        if isinstance(arg, boolean.Symbol):
            docs_with_tag = self.get_docs(arg.obj)
        else:
            docs_with_tag = self._parse_expression(operator=arg.operator, args=arg.args)
        return all_docs - docs_with_tag
