from doctag import TagIndex
import pytest


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


def test_tag(simple_ti: TagIndex):
    simple_ti.tag(docs="doc_9", tags="tag_x")
    assert simple_ti.doc_to_tags["doc_9"] == {"tag_x"}
    assert simple_ti.tag_to_docs["tag_x"] == {"doc_9"}
    simple_ti.tag(docs=["doc_9", "doc_10"], tags=["tag_y", "tag_z"])
    assert simple_ti.doc_to_tags["doc_9"] == {"tag_x", "tag_y", "tag_z"}
    assert simple_ti.doc_to_tags["doc_10"] == {"tag_y", "tag_z"}
    assert simple_ti.tag_to_docs["tag_y"] == {"doc_9", "doc_10"}
    assert simple_ti.tag_to_docs["tag_z"] == {"doc_9", "doc_10"}


def test_untag_a(simple_ti: TagIndex):
    simple_ti.untag(docs="doc_2", tags="tag_b")
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_a", "tag_c"}
    assert simple_ti.tag_to_docs["tag_b"] == {"doc_1"}
    simple_ti.untag(docs="doc_2", tags=["tag_a", "tag_c"])
    assert "doc_2" not in simple_ti.doc_to_tags
    assert "doc_2" not in simple_ti.docs
    assert "tag_c" not in simple_ti.tag_to_docs
    assert "tag_c" not in simple_ti.tags
    assert simple_ti.tag_to_docs["tag_a"] == {"doc_1"}


def test_untag_b(simple_ti: TagIndex):
    simple_ti.untag(docs=["doc_1", "doc_2"], tags=["tag_a", "tag_b"])
    assert simple_ti.doc_to_tags["doc_1"] == set()
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_c"}
    assert simple_ti.tag_to_docs["tag_a"] == set()
    assert simple_ti.tag_to_docs["tag_b"] == set()


def test_remove_tag(simple_ti: TagIndex):
    simple_ti.remove_tag(tag="tag_d")
    assert "tag_d" not in simple_ti.tag_to_docs
    assert "tag_d" not in simple_ti.tags
    assert "doc_3" not in simple_ti.doc_to_tags
    assert "doc_3" not in simple_ti.docs
    simple_ti.remove_tag(tag="tag_a")
    assert "tag_a" not in simple_ti.tag_to_docs
    assert "tag_a" not in simple_ti.tags
    assert simple_ti.doc_to_tags["doc_1"] == {"tag_b"}
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_b", "tag_c"}


def test_merge_tags_a(simple_ti: TagIndex):
    simple_ti.merge_tags(old_tags="tag_c", new_tag="tag_b")
    assert "tag_c" not in simple_ti.tag_to_docs
    assert "tag_c" not in simple_ti.tags
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_a", "tag_b"}
    simple_ti.merge_tags(old_tags=["tag_a", "tag_b"], new_tag="tag_d")
    for doc in ["doc_1", "doc_2"]:
        assert simple_ti.doc_to_tags[doc] == {"tag_d"}
    for tag in ["tag_a", "tag_b"]:
        assert tag not in simple_ti.tag_to_docs
        assert tag not in simple_ti.tags


def test_merge_tags_b(simple_ti: TagIndex):
    simple_ti.merge_tags(old_tags=["tag_a", "tag_c"], new_tag="tag_e")
    for tag in ["tag_a", "tag_c"]:
        assert tag not in simple_ti.tag_to_docs
        assert tag not in simple_ti.tags
    assert "tag_e" in simple_ti.tag_to_docs
    assert "tag_e" in simple_ti.tags
    assert simple_ti.doc_to_tags["doc_1"] == {"tag_e", "tag_b"}
    assert simple_ti.doc_to_tags["doc_2"] == {"tag_b", "tag_e"}


def test_rename_doc(simple_ti: TagIndex):
    simple_ti.rename_doc(old_doc_name="doc_2", new_doc_name="doc_4")
    assert simple_ti.doc_to_tags["doc_4"] == {"tag_a", "tag_b", "tag_c"}
    assert "doc_2" not in simple_ti.doc_to_tags
    assert "doc_2" not in simple_ti.docs
    with pytest.raises(ValueError):
        simple_ti.rename_doc(old_doc_name="doc_99", new_doc_name="doc_4")
    with pytest.raises(ValueError):
        simple_ti.rename_doc(old_doc_name="doc_2", new_doc_name="doc_3")

def test_remove_doc(simple_ti: TagIndex):
    simple_ti.remove_doc(doc_name="doc_3")
    assert "doc_3" not in simple_ti.doc_to_tags
    assert "doc_3" not in simple_ti.docs
    assert "tag_d" not in simple_ti.tag_to_docs
    assert "tag_d" not in simple_ti.tags
    with pytest.raises(ValueError):
        simple_ti.remove_doc("doc_3")
    simple_ti.remove_doc(doc_name="doc_1")
    assert "doc_1" not in simple_ti.doc_to_tags
    assert "doc_1" not in simple_ti.docs
    assert simple_ti.tag_to_docs["tag_a"] == {"doc_2"}
    assert simple_ti.tag_to_docs["tag_b"] == {"doc_2"}
