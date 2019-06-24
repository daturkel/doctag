import pytest
from doctag import FileTagIndex, TagIndex


@pytest.fixture
def simple_ti():
    ti = TagIndex()
    ti.doc_to_tags["doc_1"] = {"tag_a", "tag_b"}
    ti.doc_to_tags["doc_2"] = {"tag_a", "tag_b", "tag_c"}
    ti.doc_to_tags["doc_3"] = {"tag_d"}
    ti.tag_to_docs["tag_a"] = {"doc_1", "doc_2"}
    ti.tag_to_docs["tag_b"] = {"doc_1", "doc_2"}
    ti.tag_to_docs["tag_c"] = {"doc_2"}
    ti.tag_to_docs["tag_d"] = {"doc_3"}
    return ti


@pytest.fixture
def simple_fti():
    ti = FileTagIndex(root_dir="~/")
    ti.doc_to_tags["doc_1"] = {"tag_a", "tag_b"}
    ti.doc_to_tags["doc_2"] = {"tag_a", "tag_b", "tag_c"}
    ti.doc_to_tags["doc_3"] = {"tag_d"}
    ti.tag_to_docs["tag_a"] = {"doc_1", "doc_2"}
    ti.tag_to_docs["tag_b"] = {"doc_1", "doc_2"}
    ti.tag_to_docs["tag_c"] = {"doc_2"}
    ti.tag_to_docs["tag_d"] = {"doc_3"}
    return ti
