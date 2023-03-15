import casanova
from itertools import islice
from ebbe import format_int
from textual.app import App, ComposeResult, RenderResult
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import DataTable
from textual.widgets._header import Header, HeaderTitle


class ViewHeader(Header):
    def compose(self):
        yield HeaderTitle()


class TableFooter(Widget):
    DEFAULT_CSS = """
    TableFooter {
        background: $accent;
        color: $text;
        dock: bottom;
        height: 1;
    }
    """

    fieldnames = Reactive([])

    def render(self) -> RenderResult:
        return "columns: %s" % format_int(len(self.fieldnames))


def highlight_value(value: str) -> str:
    try:
        int(value)
        return "[red]%s" % value
    except ValueError:
        try:
            float(value)
            return "[#FFA500]%s" % value
        except ValueError:

            if value.startswith("http://") or value.startswith("https://"):
                return "[green][link=%s]%s[/link]" % (value, value)

            return "[green]%s" % value


def higlighted_row(row):
    return (highlight_value(value) for value in row)


def action(cli_args):
    filename = getattr(cli_args.file, "name", None)

    reader = casanova.reader(cli_args.file)

    class ViewApp(App):
        TITLE = filename

        def compose(self) -> ComposeResult:
            if filename is not None:
                yield ViewHeader()

            yield DataTable(zebra_stripes=True)

            footer = TableFooter()
            footer.fieldnames = reader.fieldnames

            yield footer

        def on_mount(self) -> None:
            table = self.query_one(DataTable)

            for column in reader.fieldnames or []:
                table.add_column(column)

            for row in islice(reader, 50):
                table.add_row(*higlighted_row(row))

            self.set_focus(table)

    app = ViewApp()

    app.run()
