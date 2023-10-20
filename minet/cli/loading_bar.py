# =============================================================================
# Minet Loading Bars
# =============================================================================
#
# Various loading bar utilities used by minet CLI.
#
from typing import Optional, Iterable
from minet.types import TypedDict, NotRequired

from contextlib import contextmanager
from collections import OrderedDict, namedtuple
from rich.live import Live
from rich.text import Text
from rich.table import Table, Column
from rich.progress import (
    Progress,
    ProgressColumn,
    TextColumn,
    BarColumn,
    SpinnerColumn,
    Task,
)
from about_time import HumanDuration, HumanThroughput
from ebbe import format_int

from minet.utils import message_flatmap
from minet.cli.console import console


class CautiousBarColumn(BarColumn):
    def render(self, task: Task):
        if task.total is None:
            self.bar_width = 15
        else:
            self.bar_width = min(40, 10 + task.total)

        if task.total is not None and task.completed > task.total:
            self.finished_style = "warning"

        return super().render(task)


class TimeElapsedColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        elapsed = task.finished_time if task.finished else task.elapsed

        if not elapsed:
            return Text("")

        return Text(
            "in " + HumanDuration(elapsed).as_human(2), style="progress.elapsed"
        )


class CompletionColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        total = format_int(task.total) if task.total is not None else "?"
        completed = format_int(task.completed).rjust(len(total))

        unit = task.fields.get("unit")
        unit_text = f" {unit}" if unit is not None else ""

        return Text(f"{completed}/{total}{unit_text}")


class PercentageColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        if task.total is None or task.total == 1:
            return Text("-")

        txt = "[progress.percentage][{task.percentage:>3.0f}%]".format(task=task)
        return Text.from_markup(txt)


class ThroughputColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        elapsed = task.finished_time if task.finished else task.elapsed

        if not elapsed or not task.completed:
            return Text("(?/s)")

        throughput = HumanThroughput(task.completed / elapsed, "").as_human(2)

        eta = ""

        if task.total is not None and task.time_remaining:
            remaining = HumanDuration(task.time_remaining).as_human(2)
            eta = f" eta: {remaining}"

        message = f"({throughput}{eta})"

        return Text(message)


class StatsColumn(ProgressColumn):
    def __init__(self, table_column=None, sort_key=None):
        super().__init__(table_column=table_column)
        self.sort_key = sort_key

    def render(self, task: Task) -> Text:
        stats = task.fields.get("stats")

        if stats is None:
            return Text("")

        stats_item_shown = 0

        item_parts = []

        values = stats.values()

        if self.sort_key is not None:
            values = sorted(values, key=self.sort_key)

        for item in values:
            txt = Text()

            count = item["count"]

            if count is None:
                continue

            stats_item_shown += 1

            txt.append(str(item["name"]), style=item["style"])
            txt.append(" ")
            txt.append(format_int(count))

            item_parts.append(txt)

        parts = []

        if task.description and stats_item_shown:
            parts.append(Text("- "))

        return Text.assemble(*parts, *Text(" ").join(item_parts))


class NestedTotalColumn(ProgressColumn):
    def render(self, task: Task) -> Optional[Text]:
        sub_total_sum = task.fields.get("sub_total_sum")

        if sub_total_sum is None:
            return None

        unit = task.fields.get("unit")
        unit_text = f" {unit}" if unit is not None else ""

        return Text(f"total: {format_int(sub_total_sum)}{unit_text}")


class SingleLineNestedTotalColumn(ProgressColumn):
    def __init__(
        self, parent, unit: Optional[str], table_column: Optional[Column] = None
    ) -> None:
        self.__parent = parent
        self.__unit = unit
        super().__init__(table_column=table_column)

    def render(self, _) -> Optional[Text]:
        sub_total_sum = self.__parent.sub_total_sum

        if sub_total_sum is None:
            return None

        unit = self.__unit
        unit_text = f" {unit}" if unit is not None else ""

        return Text(f"total: {format_int(sub_total_sum)}{unit_text}")


class StatsItem(TypedDict):
    name: str
    style: NotRequired[str]
    initial: NotRequired[int]


CatchAttempt = namedtuple("CatchAttempt", ["item", "index", "exception"])


def attempt_to_catch(catch, exc, item, index=None) -> bool:
    if catch is None:
        return True

    msg = None

    # Callable version
    if callable(catch):
        return catch(CatchAttempt(item, index, exc))

    # Mapping version
    msg_format = catch.get(type(exc))

    if msg_format is None:
        return True

    if msg_format is not None:
        msg = msg_format.format(item=item, index=index)

    if index is not None:
        console.logh("Line %i" % (index + 1), msg)
    else:
        console.print(msg)

    return False


class LoadingBar(object):
    def __init__(
        self,
        title: Optional[str] = None,
        unit: Optional[str] = None,
        total: Optional[int] = None,
        completed: Optional[int] = None,
        show_label: bool = False,
        label_format: str = "{task.description}",
        stats: Optional[Iterable[StatsItem]] = None,
        stats_sort_key=None,
        nested: bool = False,
        sub_title: Optional[str] = None,
        sub_title_style: str = "info",
        sub_unit: Optional[str] = None,
        transient: bool = False,
        refresh_per_second: float = 10,
        simple: bool = False,
    ):
        self.title = title
        self.sub_total_sum = 0
        self.nested = nested
        self.show_label = show_label
        self.transient = transient
        self.known_total = total is not None
        self.already_stopped = False
        self.simple = simple

        self.bar_column = None
        self.label_progress = None
        self.label_progress_task_id = None
        self.sub_progress = None
        self.sub_task_id = None
        self.stats_progress = None
        self.stats_task = None
        self.stats = OrderedDict()
        self.stats_are_shown = False

        self.table = Table.grid(expand=True)

        # Label line
        # NOTE: this was never really used
        if show_label:
            label_progress_columns = []

            if show_label:
                label_progress_columns.append(TextColumn(label_format))

            self.label_progress = Progress(*label_progress_columns)
            self.label_progress_task_id = self.label_progress.add_task(
                description="", total=None
            )

            if not simple:
                self.table.add_row(self.label_progress)

        # Main progress line
        self.bar_column = CautiousBarColumn(pulse_style="white")

        if simple:
            self.bar_column = BarColumn(pulse_style="white", bar_width=10)

        columns = [
            TextColumn("[progress.description]{task.description}"),
            self.bar_column,
        ]

        columns.append(CompletionColumn(Column(overflow="ellipsis", no_wrap=True)))

        if not nested or simple:
            columns.append(SpinnerColumn("dots", style=None, finished_text="·"))

        columns.append(PercentageColumn(Column(overflow="ellipsis", no_wrap=True)))
        columns.append(TimeElapsedColumn(Column(overflow="ellipsis", no_wrap=True)))
        columns.append(ThroughputColumn(Column(overflow="ellipsis", no_wrap=True)))

        if nested and simple:
            columns.append(SingleLineNestedTotalColumn(self, sub_unit))

        self.progress = Progress(*columns)
        self.table.add_row(self.progress)

        self.task_id = self.progress.add_task(
            description=title or "",
            total=total,
            unit=unit,
            completed=completed or 0,
        )

        # Nested progress line
        if nested:
            sub_columns = [
                SpinnerColumn("dots", style="", finished_text="·"),
                TextColumn(
                    "{task.description}",
                    table_column=Column(max_width=50),
                    style=sub_title_style,
                ),
                CompletionColumn(),
                TimeElapsedColumn(),
                ThroughputColumn(),
                NestedTotalColumn(),
            ]

            self.sub_progress = Progress(*sub_columns)
            self.sub_task_id = self.sub_progress.add_task(
                description=sub_title or "",
                total=None,
                sub_total_sum=self.sub_total_sum,
                unit=sub_unit,
            )

            if not simple:
                self.table.add_row(self.sub_progress)

        # Stats line
        if stats is not None:
            for item in stats:
                count = item.get("initial")

                self.stats[item["name"]] = {
                    "name": item["name"],
                    "style": item.get("style", ""),
                    "count": count,
                }

                if count is not None:
                    self.stats_are_shown = True

        self.stats_progress = Progress(StatsColumn(sort_key=stats_sort_key))
        self.stats_task_id = self.stats_progress.add_task("", stats=self.stats)

        if self.stats_are_shown and not simple:
            self.table.add_row(self.stats_progress)

        # Internal live instance
        self.live = Live(
            self.table,
            refresh_per_second=refresh_per_second,
            console=console,
            transient=self.transient,
        )

    def cursor_up(self) -> None:
        # NOTE: cursor 1up
        console.file.write("\x1b[1A")

    def start(self) -> None:
        self.live.start()
        self.live.refresh()

    def stop(self, erase=False) -> None:
        if self.already_stopped:
            return

        if erase:
            self.live.transient = True

        self.live.stop()
        self.already_stopped = True

    def erase(self) -> None:
        self.stop(erase=True)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        erase = False

        if exc_type is not None:
            style = "error"

            if exc_type is KeyboardInterrupt:
                if not self.already_stopped:
                    self.cursor_up()

                style = "warning"

            elif exc_type is BrokenPipeError:
                style = "warning"
                erase = True

            if self.bar_column is not None:
                self.bar_column.complete_style = style
                self.bar_column.finished_style = style
                self.bar_column.pulse_style = style

                if not self.known_total:
                    self.bar_column.style = style
        else:
            self.bar_column.pulse_style = "success"
            self.bar_column.style = "success"

        self.stop(erase=erase)

    @contextmanager
    def step(self, item=None, count=1, index=None, catch=None, sub_total=None):
        interrupted = False

        # TODO: we could add some key kwarg if needed

        try:
            if self.nested:
                self.nested_reset()

                if item is not None:
                    self.update(sub_title=item)

                self.set_sub_total(sub_total)
            else:
                if self.show_label and item is not None:
                    self.set_label(item)
            yield

        except BaseException as exc:
            interrupted = attempt_to_catch(catch, exc, item, index)

            if interrupted:
                raise
        finally:
            if not interrupted:
                self.advance(count)

    @contextmanager
    def nested_step(self, count=1):
        assert self.nested
        interrupted = False

        try:
            yield
        except BaseException:
            interrupted = True
            raise
        finally:
            if not interrupted:
                self.nested_advance(count)

    def advance(self, count=1):
        self.progress.update(self.task_id, advance=count)

    def nested_advance(self, count=1):
        self.sub_total_sum += count
        self.sub_progress.update(
            self.sub_task_id, advance=count, sub_total_sum=self.sub_total_sum
        )

    def nested_reset(self):
        self.sub_progress.reset(self.sub_task_id)

    def __refresh_stats(self):
        self.stats_progress.update(self.stats_task_id, stats=self.stats)

        if not self.simple and not self.stats_are_shown:
            self.stats_are_shown = True
            self.table.add_row(self.stats_progress)

    def set_title(self, title: str):
        self.title = title
        self.progress.update(self.task_id, description=title)

    def append_to_title(self, string: str):
        self.set_title((self.title or "") + string)

    def set_total(self, total: Optional[int] = None):
        self.progress.update(self.task_id, total=total)
        self.known_total = total is not None

    def set_sub_total(self, total: Optional[int] = None):
        self.sub_progress.update(self.sub_task_id, total=total)

    def set_label(self, label: str):
        assert self.label_progress is not None
        self.label_progress.update(self.label_progress_task_id, description=label)

    # TODO: factorize
    def set_stat(self, name: str, count: Optional[int], style: str = None):
        assert self.stats is not None

        if name not in self.stats:
            self.stats[name] = {"name": name, "count": count, "style": style or ""}
        else:
            item = self.stats[name]
            item["count"] = count

            if style is not None:
                item["style"] = style

        self.__refresh_stats()

    def inc_stat(self, name: str, count: int = 1, style: Optional[str] = None):
        assert self.stats is not None

        if name not in self.stats:
            self.stats[name] = {"name": name, "count": count, "style": style or ""}
        else:
            item = self.stats[name]
            if item["count"] is None:
                item["count"] = count
            else:
                item["count"] += count

            if style is not None:
                item["style"] = style

        self.__refresh_stats()

    def update(self, count=None, sub_title=None, sub_count=None, label=None, **fields):
        if count is not None:
            self.advance(count)

        if sub_count is not None:
            self.nested_advance(sub_count)

        if sub_title is not None:
            self.sub_progress.update(self.sub_task_id, description=sub_title)

        if label is not None:
            self.set_label(label)

        if fields:
            assert self.stats is not None

            for field, count in fields.items():
                self.stats[field]["count"] = count

            self.__refresh_stats()

    def print(self, *msg, **kwargs):
        console.print(message_flatmap(*msg), **kwargs)

    def error(self, *args, **kwargs):
        console.error(*args, **kwargs)

    def warning(self, *args, **kwargs):
        console.warning(*args, **kwargs)
