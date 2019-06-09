from doctag import TagIndex
from doctag.tagindex import parse_tag


def test_parse_tag():
    t, v = parse_tag(tag="abc")
    assert t == "abc"
    assert v is None

    t, v = parse_tag(tag="abc:hello")
    assert t == "abc"
    assert v == "hello"

    t, v = parse_tag(tag="abc:")
    assert t == "abc"
    assert v is None

    t, v = parse_tag(tag="abc:abcd:1234")
    assert t == "abc"
    assert v == "abcd:1234"


def test_tags(simple_ti: TagIndex):
    assert simple_ti.tags == {"tag_a", "tag_b", "tag_c"}


def test_docs(simple_ti: TagIndex):
    assert simple_ti.docs == {"doc_1", "doc_2"}


def test_get_docs(simple_ti: TagIndex):
    assert simple_ti.get_docs(tag="tag_a") == {"doc_1"}
    assert simple_ti.get_docs(tag="tag_b") == {"doc_1", "doc_2"}
    assert simple_ti.get_docs(tag="tag_c") == {"doc_2"}
    assert simple_ti.get_docs(tag="tag_d") == set()
