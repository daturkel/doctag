import sys
from pathlib import Path
from typing import Iterable, List, Optional

import ujson
from doctag_cli.metamarkdown import MetaMarkdown

from . import TagIndex


class FileTagIndex(TagIndex):
    def __init__(
        self,
        root_dir,
        at: Optional[str] = None,
        file_types: Optional[Iterable[str]] = None,
    ):
        if not Path(root_dir).expanduser().is_dir():
            raise NotADirectoryError
        else:
            self.root_dir = Path(root_dir).expanduser()
            self.file_types = file_types if file_types else []
            self.file_list: List[str] = []
            super().__init__(at=at)

    @classmethod
    def from_json(cls, at: str) -> "FileTagIndex":
        with open(at, "r") as from_file:
            serial = ujson.load(from_file)
            ti = FileTagIndex(
                root_dir=serial["root_dir"], at=at, file_types=serial["file_types"]
            )
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

    def to_json(self, at: Optional[str] = None):
        if at is None and self.at is not None:
            at = self.at
        elif self.at is None and self.at is not None:
            self.at = at
        serial: dict = dict()
        dtt_size = sys.getsizeof(self.doc_to_tags)
        ttd_size = sys.getsizeof(self.tag_to_docs)
        ttd_bigger = ttd_size >= dtt_size
        if ttd_bigger:
            serial["doc_to_tags"] = self.doc_to_tags
        else:
            serial["tag_to_docs"] = self.tag_to_docs
        serial["root_dir"] = str(self.root_dir)
        serial["file_types"] = self.file_types
        serial["file_list"] = self.file_list
        with open(str(at), "w") as to_file:
            ujson.dump(serial, to_file)

    def get_files(self, file_types=None):
        if file_types:
            ft_filter = file_types
        elif self.file_types:
            ft_filter = self.file_types
        else:
            ft_filter = []
        file_list = []
        if ft_filter:
            for ft in ft_filter:
                file_list.extend(self.root_dir.rglob(f"*.{ft}"))
        else:
            file_list.extend(self.root_dir.rglob("*.*"))
        self.file_list.extend(file_list)

    def _tag_callback(self, docs: Iterable[str], tags: Iterable[str]):
        for doc in docs:
            with open(doc, "r+") as doc_:
                mm = MetaMarkdown.loads(doc_.read())
                try:
                    mm.metadata["Tags"].extend(
                        [
                            "#" + tag
                            for tag in tags
                            if f"#{tag}" not in mm.metadata["Tags"]
                        ]
                    )
                    doc_.seek(0)
                    doc_.write(mm.dumps())
                    doc_.truncate()
                except (KeyError, TypeError):
                    mm.metadata["Tags"] = ["#" + tag for tag in tags]
                    doc_.seek(0)
                    doc_.write(mm.dumps())
                    doc_.truncate()

    def _untag_callback(self, docs: Iterable[str], tags: Iterable[str]):
        tags_ = [f"#{tag}" for tag in tags]
        print(tags_)
        for doc in docs:
            with open(doc, "r+") as doc_:
                mm = MetaMarkdown.loads(doc_.read())
                try:
                    mm.metadata["Tags"] = [
                        tag for tag in mm.metadata["Tags"] if tag not in tags_
                    ]
                    print(mm.metadata)
                    doc_.seek(0)
                    doc_.write(mm.dumps())
                    doc_.truncate()
                except (KeyError, TypeError):
                    pass
