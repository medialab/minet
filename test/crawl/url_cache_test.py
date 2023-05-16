from minet.crawl.url_cache import AtomicSet, SQLiteStringSet


class TestUrlCache:
    def test_atomic_set(self):
        s = AtomicSet()

        assert len(s) == 0

        assert s.add("one")
        assert not s.add("one")

        assert len(s) == 1
        assert "one" in s
        assert "two" not in s

        assert s.add_many(["one", "two", "three"]) == 2

        assert len(s) == 3
        assert "two" in s

        assert set(s) == {"one", "two", "three"}

    def test_sqlite_string_set(self, tmp_path):
        p = tmp_path / "set.db"

        s = SQLiteStringSet(p)

        assert len(s) == 0

        assert s.add("one")
        assert not s.add("one")

        assert len(s) == 1

        assert "one" in s
        assert "two" not in s

        # Testing persistence
        del s

        s = SQLiteStringSet(p)

        assert len(s) == 1
        assert "one" in s
        assert "two" not in s

        assert s.add_many(["one", "two", "three"]) == 2
        assert s.add_many(["one", "two", "three"]) == 0
        assert s.add_many(["four", "five"]) == 2

        assert len(s) == 5

        s.vacuum()

        assert len(s) == 5

        assert set(s) == {"one", "two", "three", "four", "five"}

        del s

        s = SQLiteStringSet(p)

        assert len(s) == 5

        # s.add_and_keep_new(["three", "one"])
