from pytest import raises

from minet.sqlar import SQLiteArchive, SQLiteArchiveRecord, sqlar_compress


class TestSQLiteArchive:
    def test_basics(self):
        hello = b"Hello World!"

        archive = SQLiteArchive()

        assert archive.in_memory
        assert len(archive) == 0

        archive.write("test.txt", hello, mtime=10)

        assert len(archive) == 1

        record = archive.read("test.txt")

        assert record == SQLiteArchiveRecord(
            name="test.txt",
            mode=0o664,
            mtime=10,
            size=len(hello),
            data=sqlar_compress(hello),
        )

        assert record.is_file
        assert not record.is_dir
        assert not record.is_symlink
        assert not record.is_compressed
        assert record.uncompressed_data == hello

        with raises(KeyError):
            archive.read("not-found.txt")

        archive.write("test/other.txt", b"another test")

        records = list(archive)

        assert [record.name for record in records] == ["test.txt", "test/other.txt"]
