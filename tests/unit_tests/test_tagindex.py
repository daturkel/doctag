from doctag import TagIndex
from boolean.boolean import ParseError
import pytest

## test utilities


def no_tag(ti: TagIndex, tag: str):
    assert tag not in ti.tag_to_docs
    assert tag not in ti.tags


def yes_tag(ti: TagIndex, tag: str):
    assert tag in ti.tag_to_docs
    assert tag in ti.tags


def no_doc(ti: TagIndex, doc: str):
    assert doc not in ti.doc_to_tags
    assert doc not in ti.docs


def no_conflicts(ti: TagIndex):
    assert not ti.conflicts


## tests


def test_simple_ti(simple_ti: TagIndex):
    no_conflicts(ti=simple_ti)


def test_tags(simple_ti: TagIndex):
    assert simple_ti.tags == {"tag_a", "tag_b", "tag_c", "tag_d"}


def test_docs(simple_ti: TagIndex):
    assert simple_ti.docs == {"doc_1", "doc_2", "doc_3"}


def test_get_docs(simple_ti: TagIndex):
    assert simple_ti.get_docs(tag="tag_a") == {"doc_1", "doc_2"}
    assert simple_ti.get_docs(tag="tag_b") == {"doc_1", "doc_2"}
    assert simple_ti.get_docs(tag="tag_c") == {"doc_2"}
    assert simple_ti.get_docs(tag="tag_d") == {"doc_3"}
    assert simple_ti.get_docs(tag="tag_e") == set()
    no_tag(ti=simple_ti, tag="tag_e")
    no_conflicts(ti=simple_ti)


def test_tag(simple_ti: TagIndex):
    simple_ti.tag(docs="doc_9", tags="tag_x")
    assert simple_ti.doc_to_tags["doc_9"] == {"tag_x"}
    assert simple_ti.tag_to_docs["tag_x"] == {"doc_9"}
    simple_ti.tag(docs=["doc_9", "doc_10"], tags=["tag_y", "tag_z"])
    assert simple_ti.doc_to_tags["doc_9"] == {"tag_x", "tag_y", "tag_z"}
    assert simple_ti.doc_to_tags["doc_10"] == {"tag_y", "tag_z"}
    assert simple_ti.tag_to_docs["tag_y"] == {"doc_9", "doc_10"}
    assert simple_ti.tag_to_docs["tag_z"] == {"doc_9", "doc_10"}
    with pytest.raises(ValueError):
        simple_ti.tag(docs="doc_1", tags="tRuE")
    with pytest.raises(ValueError):
        simple_ti.tag(docs="doc_1", tags="fALSE")
    with pytest.raises(ValueError):
        simple_ti.tag(docs="doc_1", tags="0")
    with pytest.raises(ValueError):
        simple_ti.tag(docs="doc_1", tags="1")
    no_conflicts(ti=simple_ti)


def test_untag_a(simple_ti: TagIndex):
    simple_ti.untag(docs="doc_2", tags="tag_b")
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_a", "tag_c"}
    assert simple_ti.tag_to_docs["tag_b"] == {"doc_1"}
    simple_ti.untag(docs="doc_2", tags=["tag_a", "tag_c"])
    no_doc(ti=simple_ti, doc="doc_2")
    no_tag(ti=simple_ti, tag="tag_c")
    assert simple_ti.tag_to_docs["tag_a"] == {"doc_1"}
    no_conflicts(ti=simple_ti)


def test_untag_b(simple_ti: TagIndex):
    simple_ti.untag(docs=["doc_1", "doc_2"], tags=["tag_a", "tag_b"])
    no_doc(ti=simple_ti, doc="doc_1")
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_c"}
    for tag in ["tag_a", "tag_b"]:
        no_tag(ti=simple_ti, tag=tag)
    no_conflicts(ti=simple_ti)


def test_remove_tag(simple_ti: TagIndex):
    simple_ti.remove_tag(tag="tag_d")
    no_tag(ti=simple_ti, tag="tag_d")
    no_doc(ti=simple_ti, doc="doc_3")
    simple_ti.remove_tag(tag="tag_a")
    no_tag(ti=simple_ti, tag="tag_a")
    assert simple_ti.doc_to_tags["doc_1"] == {"tag_b"}
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_b", "tag_c"}
    no_conflicts(ti=simple_ti)


def test_merge_tags_a(simple_ti: TagIndex):
    simple_ti.merge_tags(old_tags="tag_c", new_tag="tag_b")
    no_tag(ti=simple_ti, tag="tag_c")
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_a", "tag_b"}
    simple_ti.merge_tags(old_tags=["tag_a", "tag_b"], new_tag="tag_d")
    for doc in ["doc_1", "doc_2"]:
        assert simple_ti.doc_to_tags[doc] == {"tag_d"}
    for tag in ["tag_a", "tag_b"]:
        no_tag(ti=simple_ti, tag=tag)
    no_conflicts(ti=simple_ti)


def test_merge_tags_b(simple_ti: TagIndex):
    simple_ti.merge_tags(old_tags=["tag_a", "tag_c"], new_tag="tag_e")
    for tag in ["tag_a", "tag_c"]:
        no_tag(ti=simple_ti, tag=tag)
    yes_tag(ti=simple_ti, tag="tag_e")
    assert simple_ti.tag_to_docs["tag_e"] == {"doc_1", "doc_2"}
    assert simple_ti.doc_to_tags["doc_1"] == {"tag_e", "tag_b"}
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_b", "tag_e"}
    no_conflicts(ti=simple_ti)


def test_rename_doc(simple_ti: TagIndex):
    simple_ti.rename_doc(old_doc_name="doc_2", new_doc_name="doc_4")
    assert simple_ti.doc_to_tags["doc_4"] == {"tag_a", "tag_b", "tag_c"}
    no_doc(ti=simple_ti, doc="doc_2")
    with pytest.raises(ValueError):
        simple_ti.rename_doc(old_doc_name="doc_99", new_doc_name="doc_4")
    with pytest.raises(ValueError):
        simple_ti.rename_doc(old_doc_name="doc_2", new_doc_name="doc_3")
    no_conflicts(ti=simple_ti)


def test_remove_doc(simple_ti: TagIndex):
    simple_ti.remove_doc(doc_name="doc_3")
    no_doc(ti=simple_ti, doc="doc_3")
    no_tag(ti=simple_ti, tag="tag_d")
    with pytest.raises(ValueError):
        simple_ti.remove_doc("doc_3")
    simple_ti.remove_doc(doc_name="doc_1")
    no_doc(ti=simple_ti, doc="doc_1")
    assert simple_ti.tag_to_docs["tag_a"] == {"doc_2"}
    assert simple_ti.tag_to_docs["tag_b"] == {"doc_2"}
    no_conflicts(ti=simple_ti)


def test_query_invalid(simple_ti: TagIndex):
    with pytest.raises(ParseError):
        simple_ti.query("tag_a or (")
    no_conflicts(ti=simple_ti)


def test_query_symbol(simple_ti: TagIndex):
    assert simple_ti.query("tag_a") == {"doc_1", "doc_2"}
    assert simple_ti.query("tag_d") == {"doc_3"}
    assert simple_ti.query("tag_e") == set()
    no_tag(ti=simple_ti, tag="tag_e")
    no_conflicts(ti=simple_ti)


def test_query_not_symbol(simple_ti: TagIndex):
    assert simple_ti.query("not tag_d") == {"doc_1", "doc_2"}
    assert simple_ti.query("not tag_c") == {"doc_1", "doc_3"}
    assert simple_ti.query("not tag_e") == {"doc_1", "doc_2", "doc_3"}
    no_tag(ti=simple_ti, tag="tag_e")
    no_conflicts(ti=simple_ti)


def test_query_or_symbols(simple_ti: TagIndex):
    assert simple_ti.query("tag_c or tag_d") == {"doc_2", "doc_3"}
    assert simple_ti.query("tag_a or tag_c") == {"doc_1", "doc_2"}
    no_conflicts(ti=simple_ti)


def test_query_or_not(simple_ti: TagIndex):
    assert simple_ti.query("tag_c or not tag_b") == {"doc_2", "doc_3"}
    assert simple_ti.query("not tag_b or tag_c") == {"doc_2", "doc_3"}
    assert simple_ti.query("not (tag_b or tag_c)") == {"doc_3"}
    no_conflicts(ti=simple_ti)


def test_query_and_symbols(simple_ti: TagIndex):
    assert simple_ti.query("tag_a and tag_b") == {"doc_1", "doc_2"}
    assert simple_ti.query("tag_a and tag_c") == {"doc_2"}
    assert simple_ti.query("tag_a and tag_d") == set()
    assert simple_ti.query("tag_a and tag_e") == set()
    no_tag(ti=simple_ti, tag="tag_e")
    no_conflicts(ti=simple_ti)


def test_query_and_not(simple_ti: TagIndex):
    assert simple_ti.query("tag_a and not tag_c") == {"doc_1"}
    assert simple_ti.query("not tag_c and tag_a") == {"doc_1"}
    assert simple_ti.query("not (tag_a and tag_c)") == {"doc_1", "doc_3"}
    no_conflicts(ti=simple_ti)


def test_query_complex(simple_ti: TagIndex):
    assert simple_ti.query("not (tag_a and tag_c) and (not tag_b)") == {"doc_3"}
    assert simple_ti.query("tag_c or not (tag_a and tag_b)") == {"doc_2", "doc_3"}
    assert simple_ti.query("tag_c or not tag_a and tag_b") == {"doc_2"}
    no_conflicts(ti=simple_ti)
