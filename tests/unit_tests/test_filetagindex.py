import pytest
from doctag import FileTagIndex


def test_init():
    with pytest.raises(NotADirectoryError):
        fti = FileTagIndex(root_dir="~/asdfghjkl")


def test_get_files_a():
    fti = FileTagIndex(root_dir="./tests/test_data")
    fti.get_files()
    assert set(str(path) for path in fti.file_list) == {
        "tests/test_data/file1.txt",
        "tests/test_data/file2.md",
        "tests/test_data/more/file3.txt",
        "tests/test_data/more/file4.md",
    }


def test_get_files_b():
    fti = FileTagIndex(root_dir="./tests/test_data", file_types=["md"])
    fti.get_files()
    assert set(str(path) for path in fti.file_list) == {
        "tests/test_data/file2.md",
        "tests/test_data/more/file4.md",
    }


def test_get_files_c():
    fti = FileTagIndex(root_dir="./tests/test_data", file_types=["txt"])
    fti.get_files()
    assert set(str(path) for path in fti.file_list) == {
        "tests/test_data/file1.txt",
        "tests/test_data/more/file3.txt",
    }


def test_get_files_d():
    fti = FileTagIndex(root_dir="./tests/test_data", file_types=["txt", "md"])
    fti.get_files()
    assert set(str(path) for path in fti.file_list) == {
        "tests/test_data/file1.txt",
        "tests/test_data/file2.md",
        "tests/test_data/more/file3.txt",
        "tests/test_data/more/file4.md",
    }


def test_get_files_d():
    fti = FileTagIndex(root_dir="./tests/test_data", file_types=["txt", "md"])
    fti.get_files(file_types=["md"])
    assert set(str(path) for path in fti.file_list) == {
        "tests/test_data/file2.md",
        "tests/test_data/more/file4.md",
    }
