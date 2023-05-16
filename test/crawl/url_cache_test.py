from minet.crawl.types import CrawlJob
from minet.crawl.url_cache import AtomicSet, SQLiteStringSet, URLCache


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

        assert s.add_many_and_keep_new(["one", "three", "four"]) == ["four"]

        assert len(s) == 4

        assert s.add_many_and_keep_new(
            [(0, "one"), (2, "five")], key=lambda t: t[1]
        ) == [(2, "five")]

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

        assert s.add_many_and_keep_new(["one", "three", "six", "seven"]) == [
            "six",
            "seven",
        ]

        assert len(s) == 7

        assert s.add_many_and_keep_new(
            [(0, "one"), (2, "eight")], key=lambda t: t[1]
        ) == [(2, "eight")]

    def test_url_cache(self):
        c = URLCache()

        def jobs_as_urls(jobs):
            return [job.url for job in jobs]

        assert not c.persistent

        assert jobs_as_urls(c.register([CrawlJob(url="one"), CrawlJob(url="two")])) == [
            "one",
            "two",
        ]

        assert c.register([CrawlJob(url="one"), CrawlJob(url="two")]) == []

        assert len(c) == 2

        assert jobs_as_urls(
            c.register([CrawlJob(url="two"), CrawlJob(url="three")])
        ) == ["three"]
        assert len(c) == 3
