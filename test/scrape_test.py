# =============================================================================
# Minet Scrape Unit Tests
# =============================================================================
import pytest
from bs4 import BeautifulSoup, Tag, SoupStrainer
from textwrap import dedent

from minet.scrape import scrape, Scraper
from minet.scrape.analysis import (
    fieldnames_from_definition,
    validate,
    analyse,
    ScraperAnalysis,
)
from minet.scrape.interpreter import tabulate
from minet.scrape.std import get_display_text
from minet.scrape.straining import strainer_from_css
from minet.scrape.exceptions import (
    ScraperEvalSyntaxError,
    ScraperValidationConflictError,
    ScraperEvalError,
    ScraperEvalTypeError,
    ScraperEvalNoneError,
    NotATableError,
    CSSSelectorTooComplex,
    InvalidCSSSelectorError,
    InvalidScraperError,
    ScraperValidationIrrelevantPluralModifierError,
    ScraperValidationInvalidPluralModifierError,
    ScraperValidationInvalidExtractorError,
    ScraperValidationMixedConcernError,
    ScraperValidationUnknownKeyError,
    ScraperNotTabularError,
)

BASIC_HTML = """
    <ul>
        <li id="li1">One</li>
        <li id="li2">Two</li>
    </ul>
"""

HOLEY_HTML = """
    <ul>
        <li id="li1">One</li>
        <li>Two</li>
        <li id="li3">Three</li>
    </ul>
"""

REPETITIVE_HTML = """
    <ul>
        <li id="li1">One</li>
        <li id="li1">Two</li>
        <li id="li3">Three</li>
    </ul>
"""


NESTED_HTML = """
    <ul>
        <li id="li1" class="li"><span class="first">One</span> <span class="second">1</span></li>
        <li id="li2" class="li"><span class="first">Two</span> <span class="second">2</span></li>
    </ul>
"""

META_HTML = """
    Exemple
    <div id="ok">
        <ul>
            <li id="li1">One</li>
            <li id="li2">Two</li>
        </ul>
    </div>
"""

TABLE_TH_HTML = """
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Surname</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>John</td>
                <td>Mayall</td>
            </tr>
            <tr>
                <td>Mary</td>
                <td>Susan</td>
            </tr>
        </tbody>
    </table>
"""

THE_WORST_HTML = """
    <div>Some text isn't
    it?
        <div>
            Hello <strong>Mr. Bond</strong>, How
            are you?

            This is
            <em>italic</em>
            isn't it?
            <h2>This is a title</h2>
            <p>
                This is a good question
            </p>
            <p>
                Isn't it?
            </p><p>Bingo</p>
            <span> Whatever   </span> it is&nbsp;incredible!
            <br>
            Hello!<br>Good morning!
            <hr>
            Is this another line?
            <pre>This is it!
                    So many tabs
                Very pretty?
            Indeed.
            Catastrophe!</pre>
            <ul>
                <li>Hello</li>
                <li>Whatever</li>
            </ul>




            <ol>
                <li>Other</li>
                <li>Again</li>
            </ol>
            <p>
            <![CDATA[some very interesting stuff]]></p>
            <p>
                This is      <span>a large span  </span>
                    with something else over <strong>here</strong>.
            </p>
        </div>
        <p>
            Hello <span>gorgeous!</span></p>
        <p>
            This will be in<em>credible</em>
            <p>No? <p>Yes!</p></p>
        </p>
        <div>
            <span>This should be</span>
            <span>on the same line!</span><blockquote>
    Inspiring citation.
    </blockquote>
        </div>
        <p>
            <span>Same
                line!</span>
        </p>
    </div>
"""


class TestScrape(object):
    def test_basics(self):
        result = scrape({"iterator": "li"}, BASIC_HTML)

        assert result == ["One", "Two"]

        result = scrape({"iterator": "li", "item": "id"}, BASIC_HTML)

        assert result == ["li1", "li2"]

        result = scrape({"iterator": "li", "item": {"attr": "id"}}, BASIC_HTML)

        assert result == ["li1", "li2"]

        result = scrape({"sel": "#ok", "item": "id"}, META_HTML)

        assert result == "ok"

        result = scrape({"sel": "#ok", "iterator": "li", "item": "id"}, META_HTML)

        assert result == ["li1", "li2"]

        result = scrape(
            {"iterator": "li", "item": {"eval": 'element.get("id") + "-ok"'}},
            BASIC_HTML,
        )

        assert result == ["li1-ok", "li2-ok"]

        result = scrape(
            {"iterator": "li", "item": {"attr": "id", "eval": 'value + "-test"'}},
            BASIC_HTML,
        )

        result == ["li1-test", "li2-test"]

        result = scrape(
            {"iterator": "li", "fields": {"id": "id", "text": "text"}}, BASIC_HTML
        )

        assert result == [{"id": "li1", "text": "One"}, {"id": "li2", "text": "Two"}]

        result = scrape(
            {
                "iterator": "li",
                "fields": {"label": {"sel": ".first"}, "number": {"sel": ".second"}},
            },
            NESTED_HTML,
        )

        assert result == [
            {"number": "1", "label": "One"},
            {"number": "2", "label": "Two"},
        ]

        result = scrape(
            {
                "iterator": "li",
                "fields": {
                    "inner": {"extract": "inner_html"},
                    "outer": {"extract": "outer_html"},
                },
            },
            NESTED_HTML,
        )

        assert result == [
            {
                "inner": '<span class="first">One</span> <span class="second">1</span>',
                "outer": '<li class="li" id="li1"><span class="first">One</span> <span class="second">1</span></li>',
            },
            {
                "inner": '<span class="first">Two</span> <span class="second">2</span>',
                "outer": '<li class="li" id="li2"><span class="first">Two</span> <span class="second">2</span></li>',
            },
        ]
        result = scrape(
            {"item": {"extract": "display_text"}}, "<p>Hello</p><p>World</p>"
        )

        assert result == "Hello\n\nWorld"

        result = scrape(
            {
                "iterator": "li",
                "fields": {"value": "text", "constant": {"default": "Same"}},
            },
            BASIC_HTML,
        )

        assert result == [
            {"value": "One", "constant": "Same"},
            {"value": "Two", "constant": "Same"},
        ]

        result = scrape(
            {"iterator": "li", "item": {"attr": "class", "default": "no-class"}},
            BASIC_HTML,
        )

        assert result == ["no-class", "no-class"]

    def test_stripped_extraction(self):
        text = scrape({"sel": "div"}, "<div>    Hello world        </div>")

        assert text == "Hello world"

    def test_filter(self):
        result = scrape({"iterator": "li", "item": "id"}, HOLEY_HTML)

        assert result == ["li1", None, "li3"]

        result = scrape(
            {"iterator": "li", "item": "id", "filter_eval": "bool(value)"}, HOLEY_HTML
        )

        assert result == ["li1", "li3"]

        result = scrape({"iterator": "li", "item": "id", "filter": True}, HOLEY_HTML)

        assert result == ["li1", "li3"]

        result = scrape(
            {"$$": "li", "fields": {"id": "id"}, "filter": True}, HOLEY_HTML
        )

        assert result == [{"id": "li1"}, {"id": None}, {"id": "li3"}]

        result = scrape(
            {"iterator": "li", "fields": {"id": "id"}, "filter": "id"}, HOLEY_HTML
        )

        assert result == [{"id": "li1"}, {"id": "li3"}]

        target_html = """
            <ul>
                <li color="blue" age="34">John</li>
                <li age="45">Mary</li>
                <li color="purple" age="23">Susan    </li>
            </ul>
        """

        result = scrape(
            {
                "iterator": "li",
                "fields": {
                    "name": "text",
                    "attributes": {"fields": {"color": "color", "age": "age"}},
                },
                "filter": "attributes.color",
            },
            target_html,
        )

        assert result == [
            {"name": "John", "attributes": {"color": "blue", "age": "34"}},
            {"name": "Susan", "attributes": {"color": "purple", "age": "23"}},
        ]

    def test_uniq(self):
        result = scrape({"iterator": "li", "item": "id", "uniq": True}, REPETITIVE_HTML)

        assert result == ["li1", "li3"]

        result = scrape(
            {"iterator": "li", "fields": {"id": "id"}, "uniq": "id"}, REPETITIVE_HTML
        )

        assert result == [{"id": "li1"}, {"id": "li3"}]

    def test_recursive(self):
        result = scrape({"iterator": "li", "item": {"iterator": "span"}}, NESTED_HTML)

        assert result == [["One", "1"], ["Two", "2"]]

    def test_selection_eval(self):

        result = scrape(
            {"iterator": "li", "item": {"sel_eval": 'element.select_one("span")'}},
            NESTED_HTML,
        )

        assert result == ["One", "Two"]

        result = scrape(
            {
                "iterator_eval": 'element.select("li") + element.select("span")',
                "item": {"attr": "class"},
            },
            NESTED_HTML,
        )

        assert result == [["li"], ["li"], ["first"], ["second"], ["first"], ["second"]]

        result = scrape({"iterator": "li", "item": {"sel_eval": '"span"'}}, NESTED_HTML)

        assert result == ["One", "Two"]

        result = scrape(
            {"iterator_eval": '"li, span"', "item": {"attr": "class"}}, NESTED_HTML
        )

        assert result == [["li"], ["first"], ["second"], ["li"], ["first"], ["second"]]

    def test_eval(self):
        result = scrape(
            {
                "iterator": "li",
                "fields": {"root_id": {"eval": 'root.select_one("#ok").get("id")'}},
            },
            META_HTML,
        )

        assert result == [{"root_id": "ok"}, {"root_id": "ok"}]

        result = scrape(
            {"sel": "li", "item": {"eval": "a = 45\nreturn a + 10"}}, BASIC_HTML
        )

        assert result == 55

        result = scrape(
            {
                "item": {
                    "eval": 'el = element.select_one("li")\nreturn el.get_text().strip()'
                }
            },
            BASIC_HTML,
        )

        assert result == "One"

    def test_callable_eval(self):
        def process(value, **kwargs):
            return value.upper()

        result = scrape({"iterator": "li", "item": {"eval": process}}, BASIC_HTML)

        assert result == ["ONE", "TWO"]

    def test_context(self):
        result = scrape(
            {
                "iterator": "li",
                "fields": {
                    "text": {"method": "text"},
                    "context": {"eval": 'context["value"]'},
                },
            },
            BASIC_HTML,
            context={"value": 1},
        )

        assert list(result) == [
            {"text": "One", "context": 1},
            {"text": "Two", "context": 1},
        ]

        result = scrape(
            {
                "iterator": "li",
                "fields": {
                    "text": {"method": "text"},
                    "context": {"get_context": "value"},
                },
            },
            BASIC_HTML,
            context={"value": 1},
        )

        assert list(result) == [
            {"text": "One", "context": 1},
            {"text": "Two", "context": 1},
        ]

        result = scrape(
            {
                "set_context": {"divid": {"$": "#ok", "attr": "id"}},
                "iterator": "li",
                "fields": {"context": {"get_context": "divid"}, "value": "text"},
            },
            META_HTML,
        )

        assert result == [
            {"context": "ok", "value": "One"},
            {"context": "ok", "value": "Two"},
        ]

        result = scrape(
            {
                "set_context": {"title": {"default": "Scrape"}},
                "iterator": "li",
                "fields": {
                    "local": {
                        "set_context": {
                            "divid": {"eval": 'root.select_one("#ok").get("id")'}
                        },
                        "get_context": "divid",
                    },
                    "global": {"get_context": "divid"},
                    "title": {"get_context": "title"},
                },
            },
            META_HTML,
            context={"divid": "notok"},
        )

        assert result == [
            {"local": "ok", "global": "notok", "title": "Scrape"},
            {"local": "ok", "global": "notok", "title": "Scrape"},
        ]

    def test_tabulate(self):
        soup = BeautifulSoup(TABLE_TH_HTML, "lxml")
        table = soup.select_one("table")

        result = list(tabulate(table))

        assert result == [
            {"Name": "John", "Surname": "Mayall"},
            {"Name": "Mary", "Surname": "Susan"},
        ]

        result = list(tabulate(table, headers=["name", "surname"]))

        assert result == [
            {"name": "John", "surname": "Mayall"},
            {"name": "Mary", "surname": "Susan"},
        ]

        result = list(tabulate(table, headers_inference=None))

        assert result == [["John", "Mayall"], ["Mary", "Susan"]]

        with pytest.raises(NotATableError):
            tabulate(soup.select_one("tr"))

    def test_fieldnames(self):
        fieldnames = fieldnames_from_definition({"iterator": "li"})

        assert fieldnames == ["value"]

        fieldnames = fieldnames_from_definition({"iterator": "li", "item": "id"})

        assert fieldnames == ["value"]

        fieldnames = fieldnames_from_definition(
            {"iterator": "li", "fields": {"id": "id"}}
        )

        assert fieldnames == ["id"]

        fieldnames = fieldnames_from_definition(
            {"sel": "table", "tabulate": {"headers": ["id"]}}
        )

        assert fieldnames == ["id"]

        fieldnames = fieldnames_from_definition({"sel": "table", "tabulate": True})

        scraper = Scraper({"iterator": "li", "fields": {"id": "id"}})

        assert scraper.fieldnames == ["id"]

    def test_analysis(self):
        analysis = analyse({"item": "href"})

        assert analysis == ScraperAnalysis(
            plural=False, fieldnames=["value"], output_type="scalar"
        )

        analysis = analyse({"fields": {"url": "href", "title": "text"}})

        assert analysis == ScraperAnalysis(
            plural=False, fieldnames=["url", "title"], output_type="dict"
        )

        analysis = analyse(
            {"iterator": "li", "fields": {"url": "href", "title": "text"}}
        )

        assert analysis == ScraperAnalysis(
            plural=True, fieldnames=["url", "title"], output_type="collection"
        )

    def test_absent_tail_call(self):
        item = scrape({"sel": "quote", "fields": {"url": "href"}}, BASIC_HTML)

        assert item is None

    def test_inexistent_selection(self):
        expected = [{"id": "li1", "empty": None}, {"id": "li2", "empty": None}]

        items = scrape(
            {"iterator": "li", "fields": {"id": "id", "empty": {"sel": "blockquote"}}},
            BASIC_HTML,
        )

        assert items == expected

        items = scrape(
            {
                "iterator": "li",
                "fields": {"id": "id", "empty": {"sel": "blockquote", "item": "text"}},
            },
            BASIC_HTML,
        )

        assert items == expected

        item = scrape(
            {
                "sel": "li",
                "fields": {"id": "id", "empty": {"sel": "blockquote", "item": "text"}},
            },
            BASIC_HTML,
        )

        assert item == expected[0]

    def test_leaf(self):
        item = scrape({"sel": "li"}, BASIC_HTML)

        assert item == "One"

        item = scrape({}, BASIC_HTML)

        assert item == "One\nTwo"

    def test_dumb_recursive(self):
        item = scrape(
            {"sel": "ul", "item": {"sel": "li", "item": {"sel": "span"}}}, NESTED_HTML
        )

        assert item == "One"

    def test_conditional_eval(self):
        html = """
            <main>
                <div id="colors">
                    <p>Red</p>
                    <p>Blue</p>
                </div>
                <div id="animals">
                    <ul>
                        <li>Tiger</li>
                        <li>Dog</li>
                    </ul>
                </div>
            </main>
        """

        result = scrape(
            {
                "iterator": "div",
                "fields": {
                    "kind": "id",
                    "items": {
                        "iterator_eval": 'element.select("p") if element.get("id") == "colors" else element.select("li")'
                    },
                },
            },
            html,
        )

        assert result == [
            {"kind": "colors", "items": ["Red", "Blue"]},
            {"kind": "animals", "items": ["Tiger", "Dog"]},
        ]

    def test_nested_local_context(self):
        html = """
            <div data-topic="science">
                <ul>
                    <li>
                        <p>
                            Post n°<strong>1</strong> by <em>Allan</em>
                        </p>
                    </li>
                    <li>
                        <p>
                            Post n°<strong>2</strong> by <em>Susan</em>
                        </p>
                    </li>
                </ul>
            </div>
            <div data-topic="arts">
                <ul>
                    <li>
                        <p>
                            Post n°<strong>3</strong> by <em>Josephine</em>
                        </p>
                    </li>
                    <li>
                        <p>
                            Post n°<strong>4</strong> by <em>Peter</em>
                        </p>
                    </li>
                </ul>
            </div>
        """

        result = scrape(
            {
                "iterator": "div",
                "item": {
                    "set_context": {"topic": "data-topic"},
                    "iterator": "li > p",
                    "fields": {
                        "topic": {"get_context": "topic"},
                        "post": {"sel": "strong"},
                        "author": {"sel": "em"},
                    },
                },
            },
            html,
        )

        assert result == [
            [
                {"topic": "science", "post": "1", "author": "Allan"},
                {"topic": "science", "post": "2", "author": "Susan"},
            ],
            [
                {"topic": "arts", "post": "3", "author": "Josephine"},
                {"topic": "arts", "post": "4", "author": "Peter"},
            ],
        ]

        result = scrape(
            {
                "iterator": "li",
                "fields": {
                    "topic": {
                        "sel_eval": 'element.find_parent("div")',
                        "attr": "data-topic",
                    },
                    "post": {"sel": "strong"},
                    "author": {"sel": "em"},
                },
            },
            html,
        )

        assert result == [
            {"topic": "science", "post": "1", "author": "Allan"},
            {"topic": "science", "post": "2", "author": "Susan"},
            {"topic": "arts", "post": "3", "author": "Josephine"},
            {"topic": "arts", "post": "4", "author": "Peter"},
        ]

    def test_scope(self):
        result = scrape(
            {
                "iterator": "li",
                "item": {"eval": "x = scope.x or 0\nscope.x = x + 1\nreturn scope.x"},
            },
            REPETITIVE_HTML,
        )

        assert result == [1, 2, 3]

    def test_validate(self):
        bad_definition = {
            "sel": "li",
            "item": {"sel": "a[", "eval": '"ok'},
            "filter": True,
            "fields": {
                "url": {"iterator": ":first", "iterator_eval": '"span"'},
                "name": {"attr": "id", "extract": "text"},
                "extractor": {"extract": "blabla"},
                "id": {"attr": "id", "item": "href"},
                "invalid_filter1": {"iterator": "div", "filter": "guacamole"},
                "invalid_filter2": {
                    "iterator": "div",
                    "filter": True,
                    "fields": {"id": "text"},
                },
                "unknown_key": {"idontknowyou": True},
            },
        }

        errors = validate(bad_definition)

        def key(t):
            return (".".join(t[0]), t[1].__name__)

        errors = sorted([(e.path, type(e)) for e in errors], key=key)

        expecting = sorted(
            [
                ([], ScraperValidationConflictError),
                ([], ScraperValidationInvalidPluralModifierError),
                (["item", "sel"], InvalidCSSSelectorError),
                (["item", "eval"], ScraperEvalSyntaxError),
                (["fields", "url", "iterator"], InvalidCSSSelectorError),
                ([], ScraperValidationIrrelevantPluralModifierError),
                (["fields", "url"], ScraperValidationConflictError),
                (["fields", "name"], ScraperValidationConflictError),
                (["fields", "id"], ScraperValidationMixedConcernError),
                (
                    ["fields", "invalid_filter1"],
                    ScraperValidationInvalidPluralModifierError,
                ),
                (
                    ["fields", "invalid_filter2"],
                    ScraperValidationInvalidPluralModifierError,
                ),
                (["fields", "extractor"], ScraperValidationInvalidExtractorError),
                (["fields", "unknown_key"], ScraperValidationUnknownKeyError),
            ],
            key=key,
        )

        assert errors == expecting

        with pytest.raises(InvalidScraperError) as info:
            Scraper(bad_definition)

        errors = sorted(
            [(e.path, type(e)) for e in info.value.validation_errors], key=key
        )

        assert errors == expecting

    def test_eval_errors(self):
        with pytest.raises(ScraperEvalError) as info:
            scrape({"iterator": "li", "item": {"eval": "item.split()"}}, BASIC_HTML)

        assert isinstance(info.value.reason, NameError)
        assert info.value.path == ["item", "eval"]

        with pytest.raises(ScraperEvalError) as info:

            def hellraiser(**kwargs):
                raise RuntimeError

            scrape({"iterator": "li", "item": {"eval": hellraiser}}, BASIC_HTML)

        assert isinstance(info.value.reason, RuntimeError)
        assert info.value.path == ["item", "eval"]

        with pytest.raises(ScraperEvalTypeError) as info:
            scrape({"sel_eval": "45"}, BASIC_HTML)

        assert info.value.expected == (Tag, str)
        assert info.value.got == 45
        assert info.value.path == ["sel_eval"]

        with pytest.raises(ScraperEvalNoneError) as info:
            scrape({"iterator_eval": "None"}, BASIC_HTML)

        assert info.value.path == ["iterator_eval"]

        with pytest.raises(ScraperEvalTypeError) as info:

            def iterator(element, **kwargs):
                return [element.select_one("li"), 45]

            scrape({"iterator_eval": iterator}, BASIC_HTML)

        assert info.value.path == ["iterator_eval"]

    def test_straining(self):
        too_complex = [
            "ul > li",
            "ul>li",
            "ul li",
            "ul ~ li",
            ":is(span, div)",
            "div:nth-child(4n)",
        ]

        for css in too_complex:
            with pytest.raises(CSSSelectorTooComplex):
                strainer_from_css(css)

        with pytest.raises(InvalidCSSSelectorError):
            strainer_from_css("")

        with pytest.raises(InvalidCSSSelectorError):
            strainer_from_css("a[")

        strainer = strainer_from_css("td")

        assert isinstance(strainer, SoupStrainer)

        def test_strainer(css, input_html, output_html, **kwargs):
            parse_only = strainer_from_css(css, **kwargs)
            input_soup = BeautifulSoup(
                "<main>%s</main>" % input_html, "lxml", parse_only=parse_only
            )

            assert input_soup.decode_contents().strip() == output_html

        test_strainer(
            "td",
            TABLE_TH_HTML,
            "<td>John</td><td>Mayall</td><td>Mary</td><td>Susan</td>",
        )

        test_strainer(
            "#important",
            '<div><p>ok</p><p id="important">whatever</p></div><div>Hello</div>',
            '<p id="important">whatever</p>',
        )

        test_strainer(
            "em, strong",
            "<div>Hello this is <em>horse</em> and <strong>chicken</strong></div><div>Hello</div>",
            "<em>horse</em><strong>chicken</strong>",
        )

        test_strainer(
            "*",
            '<div><p>ok</p><p id="important">whatever</p></div><div>Hello</div>',
            '<html><body><main><div><p>ok</p><p id="important">whatever</p></div><div>Hello</div></main></body></html>',
        )

        test_strainer(
            "li > span",
            "<ul><li>1. <span>One</span></li><li>2. Two</li></ul><div>Hello</div>",
            "<li>1. <span>One</span></li><li>2. Two</li>",
            ignore_relations=True,
        )

        test_strainer(
            "ul span",
            "<ul><li>1. <span>One</span></li><li>2. Two</li></ul><div>Hello</div>",
            "<ul><li>1. <span>One</span></li><li>2. Two</li></ul>",
            ignore_relations=True,
        )

        test_strainer(
            ".number",
            '<ul><li>1. <span class="number">One</span></li><li>2. Two</li></ul><div class="  yellow  number">Hello</div>',
            '<span class="number">One</span><div class="yellow number">Hello</div>',
        )

        test_strainer(
            "span.number",
            '<ul><li>1. <span class="number">One</span></li><li>2. Two</li></ul><div class="  yellow  number">Hello</div>',
            '<span class="number">One</span>',
        )

        test_strainer(
            "[color]",
            '<ul><li>1. <span color="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        test_strainer(
            "span[color]",
            '<ul color="red"><li>1. <span color="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        test_strainer(
            "[color=blue]",
            '<ul color="red"><li>1. <span color="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        test_strainer(
            "[color*=u]",
            '<ul color="red"><li>1. <span color="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        test_strainer(
            "[color^=bl]",
            '<ul color="red"><li>1. <span color="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        test_strainer(
            "[color$=ue]",
            '<ul color="red"><li>1. <span color="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        test_strainer(
            "[color=blue]",
            '<ul color="red"><li>1. <span COLOR="blue">One</span></li><li>2. Two</li></ul><div>Hello</div>',
            '<span color="blue">One</span>',
        )

        scraper = Scraper({"iterator": "li"}, strain="div")

        html = "<div>Hello</div><ul><li>ok</li>"

        assert scraper(html) == []

    def test_as_csv_row(self):
        with pytest.raises(ScraperNotTabularError):
            scraper = Scraper(
                {"iterator": "li", "fields": {"nested": {"fields": {"text": "text"}}}}
            )

            scraper.as_csv_dict_rows(BASIC_HTML)

        scraper = Scraper({"iterator": "li"})

        assert list(scraper.as_csv_dict_rows(BASIC_HTML)) == [
            {"value": "One"},
            {"value": "Two"},
        ]
        assert list(scraper.as_csv_rows(BASIC_HTML)) == [["One"], ["Two"]]

        scraper = Scraper(
            {
                "iterator": "li",
                "fields": {
                    "text": "text",
                    "list": {"default": [1, 2]},
                    "false": {"default": False},
                    "true": {"default": True},
                },
            }
        )

        assert list(scraper.as_csv_dict_rows(BASIC_HTML)) == [
            {"text": "One", "list": "1|2", "false": "false", "true": "true"},
            {"text": "Two", "list": "1|2", "false": "false", "true": "true"},
        ]
        assert list(scraper.as_csv_rows(BASIC_HTML)) == [
            ["One", "1|2", "false", "true"],
            ["Two", "1|2", "false", "true"],
        ]

        assert list(scraper.as_csv_dict_rows(BASIC_HTML, plural_separator="§")) == [
            {"text": "One", "list": "1§2", "false": "false", "true": "true"},
            {"text": "Two", "list": "1§2", "false": "false", "true": "true"},
        ]
        assert list(scraper.as_csv_rows(BASIC_HTML, plural_separator="§")) == [
            ["One", "1§2", "false", "true"],
            ["Two", "1§2", "false", "true"],
        ]

    def test_get_display_test(self):
        soup = BeautifulSoup(THE_WORST_HTML, "lxml")

        text = get_display_text(soup)

        def clean(t):
            return dedent(t).strip()

        assert text == clean(
            """
            Some text isn't it?
            Hello Mr. Bond, How are you? This is italic isn't it?

            This is a title

            This is a good question

            Isn't it?

            Bingo

            Whatever it is incredible!
            Hello!
            Good morning!

            Is this another line?

            This is it!
            So many tabs
            Very pretty?
            Indeed.
            Catastrophe!

            Hello
            Whatever

            Other
            Again

            some very interesting stuff

            This is a large span with something else over here.

            Hello gorgeous!

            This will be incredible

            No?

            Yes!

            This should be on the same line!

            Inspiring citation.

            Same line!
        """
        )

        text = get_display_text(BeautifulSoup(TABLE_TH_HTML, "lxml"))

        assert text == clean(
            """
            Name Surname
            John Mayall
            Mary Susan
        """
        )

        piecewise_html = clean(
            """
            <main>
                <div></div>
                <div>

                </div>
                <div>Hello</div>
                <div>   </div>

                <div>World!</div>
            </main>
        """
        )

        soup = BeautifulSoup(piecewise_html, "lxml")
        elements = soup.select("div")

        text = get_display_text(elements)

        assert text == "Hello\n\nWorld!"

        soup = BeautifulSoup(
            '<div><span>L\'international</span><wbr/><span class="word_break"></span>e.</div>',
            "lxml",
        )
        elements = soup.select("div")

        text = get_display_text(elements)

        assert text == "L'internationale."
