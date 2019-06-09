import pytest

from doctag import TagIndex

@pytest.fixture
def empty_ti():
    ti = TagIndex()
    return ti

@pytest.fixture
def simple_ti():
    ti = TagIndex()
    ti.doc_to_tags["doc_1"] = {"tag_a","tag_b"}
    ti.doc_to_tags["doc_2"] = {"tag_b","tag_c"}
    ti.tag_to_docs["tag_a"] = {"doc_1"}
    ti.tag_to_docs["tag_b"] = {"doc_1","doc_2"}
    ti.tag_to_docs["tag_c"] = {"doc_2"}
    return ti
    
