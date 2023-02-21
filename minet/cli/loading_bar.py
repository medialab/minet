# =============================================================================
# Minet Loading Bars
# =============================================================================
#
# Various loading bar utilities used by minet CLI.
#
from typing import Optional, Iterable
from typing_extensions import TypedDict, NotRequired

from contextlib import contextmanager
from collections import OrderedDict
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

        return Text("in " + str(HumanDuration(elapsed)), style="progress.elapsed")


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

        throughput = HumanThroughput(task.completed / elapsed, "s")

        eta = ""

        if task.total is not None and task.time_remaining:
            remaining = HumanDuration(task.time_remaining)
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

        total = 0

        item_parts = []

        values = stats.values()

        if self.sort_key is not None:
            values = sorted(values, key=self.sort_key)

        for item in values:
            txt = Text()

            count = item["count"]

            if count == 0:
                continue

            total += count

            txt.append(str(item["name"]), style=item["style"])
            txt.append(" ")
            txt.append(format_int(count))

            item_parts.append(txt)

        parts = []

        if task.description and total:
            parts.append(Text("- "))

        return Text.assemble(*parts, *Text(" ").join(item_parts))


class NestedTotalColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        sub_total = task.fields.get("sub_total")

        if sub_total is None:
            return None

        unit = task.fields.get("unit")
        unit_text = f" {unit}" if unit is not None else ""

        return Text(f"total: {format_int(sub_total)}{unit_text}")


class StatsItem(TypedDict):
    name: str
    style: NotRequired[str]
    initial: NotRequired[int]


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
    ):
        self.sub_total = 0
        self.nested = nested
        self.transient = transient
        self.known_total = total is not None

        self.bar_column = None
        self.label_progress = None
        self.label_progress_task_id = None
        self.sub_progress = None
        self.sub_task = None
        self.stats_progress = None
        self.stats_task = None
        self.stats = OrderedDict()
        self.stats_are_shown = False

        self.table = Table.grid(expand=True)

        # Label line
        if show_label:
            label_progress_columns = []

            if show_label:
                label_progress_columns.append(TextColumn(label_format))

            self.label_progress = Progress(*label_progress_columns)
            self.label_progress_task_id = self.label_progress.add_task(
                description="", total=None
            )
            self.table.add_row(self.label_progress)

        # Main progress line
        self.bar_column = CautiousBarColumn(pulse_style="white")

        columns = [
            TextColumn("[progress.description]{task.description}"),
            self.bar_column,
        ]

        columns.append(CompletionColumn())

        if not nested:
            columns.append(SpinnerColumn("dots", style=None, finished_text="·"))

        columns.append(PercentageColumn())
        columns.append(TimeElapsedColumn())
        columns.append(ThroughputColumn())

        self.progress = Progress(*columns, console=console)
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
                    table_column=Column(width=50, min_width=0),
                    style=sub_title_style,
                ),
                CompletionColumn(),
                TimeElapsedColumn(),
                ThroughputColumn(),
                NestedTotalColumn(),
            ]

            self.sub_progress = Progress(*sub_columns)
            self.sub_task = self.sub_progress.add_task(
                description=sub_title or "",
                total=None,
                sub_total=self.sub_total,
                unit=sub_unit,
            )

            self.table.add_row(self.sub_progress)

        # Stats line
        if stats is not None:
            for item in stats:
                count = item.get("count", 0)

                self.stats[item["name"]] = {
                    "name": item["name"],
                    "style": item.get("style", ""),
                    "count": count,
                }

                if count:
                    self.stats_are_shown = True

        self.stats_progress = Progress(StatsColumn(sort_key=stats_sort_key))
        self.stats_task_id = self.stats_progress.add_task("", stats=self.stats)

        if self.stats_are_shown:
            self.table.add_row(self.stats_progress)

        # Internal live instance
        self.live = Live(
            self.table, refresh_per_second=10, console=console, transient=self.transient
        )

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):

        if exc_type is not None:
            style = "error"

            # NOTE: cursor 1up
            if exc_type is KeyboardInterrupt:
                console.file.write("\x1b[1A")
                style = "warning"

            if self.bar_column is not None:
                self.bar_column.complete_style = style
                self.bar_column.finished_style = style
                self.bar_column.pulse_style = style

                if not self.known_total:
                    self.bar_column.style = style
        else:
            self.bar_column.pulse_style = "success"
            self.bar_column.style = "success"

        self.live.stop()

    @contextmanager
    def step(self, label=None, count=1):
        interrupted = False

        try:
            if self.nested:
                self.nested_reset()

                if label is not None:
                    self.update(sub_title=label)
            else:
                if label is not None:
                    self.set_label(label)
            yield
        except BaseException:
            interrupted = True
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
        self.sub_total += 1
        self.sub_progress.update(self.sub_task, advance=count, sub_total=self.sub_total)

    def nested_reset(self):
        self.sub_progress.reset(self.sub_task)

    def __refresh_stats(self):
        self.stats_progress.update(self.stats_task_id, stats=self.stats)

        if not self.stats_are_shown:
            self.stats_are_shown = True
            self.table.add_row(self.stats_progress)

    def set_title(self, title: str):
        self.progress.update(self.task_id, description=title)

    def set_total(self, total: Optional[int] = None):
        self.progress.update(self.task_id, total=total)
        self.known_total = total is not None

    def set_label(self, label: str):
        assert self.label_progress is not None
        self.label_progress.update(self.label_progress_task_id, description=label)

    # TODO: factorize
    def set_stat(self, name: str, count: int, style: str = None):
        assert self.stats is not None

        if name not in self.stats:
            self.stats[name] = {"name": name, "count": count, "style": style or ""}
        else:
            item = self.stats[name]
            item["count"] = count

            if style is not None:
                item["style"] = style

        self.__refresh_stats()

    def inc_stat(self, name: str, style: str = None, count=1):
        assert self.stats is not None

        if name not in self.stats:
            self.stats[name] = {"name": name, "count": count, "style": style or ""}
        else:
            item = self.stats[name]
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
            self.sub_progress.update(self.sub_task, description=sub_title)

        if label is not None:
            self.set_label(label)

        if fields:
            assert self.stats is not None

            for field, count in fields.items():
                self.stats[field]["count"] = count

            self.__refresh_stats()

    def print(self, *msg):
        console.print(message_flatmap(*msg))
