# =============================================================================
# Minet Scraper Compilation
# =============================================================================
#
# Schemes related to scraper definition "compilation".
#
import itertools
from io import StringIO

from minet.scrape.constants import EXTRACTOR_NAMES


class CompilerStackItem(object):
    def __init__(self, printer, node, parent_var, container_var, parent,
                 identifier, level, plural=False):
        self.printer = printer
        self.node = node
        self.parent_var = parent_var
        self.container_var = container_var
        self.parent = parent
        self.identifier = identifier
        self.level = level
        self.plural = plural

    def close(self):
        grandparent = self.parent.parent

        if grandparent is None:
            return

        if not grandparent.plural:
            self.printer(
                '{parent_container} = {container}',
                level=self.level - 1,
                parent_container=grandparent.container_var,
                container=self.container_var
            )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def print(self, string, **kwargs):
        return self.printer(
            string,
            level=self.level,
            id=self.identifier,
            parent=self.parent_var,
            container=self.container_var,
            **kwargs
        )

    def format(self, string, **kwargs):
        return string.format(
            id=self.identifier,
            parent=self.parent_var,
            container=self.container_var,
            **kwargs
        )


class CompilerStack(object):
    def __init__(self, printer):
        self.inner = []
        self.printer = printer
        self.counter = itertools.count()

        self.last_seen_item = None

    def pop(self):
        item = self.inner.pop()
        self.last_seen_item = item

        return item

    def empty(self):
        return len(self.inner) == 0

    def append(self, node, plural=False):
        item = CompilerStackItem(
            printer=self.printer,
            node=node,
            parent_var=self.last_seen_item.format('element_{id}'),
            container_var=self.last_seen_item.format('value_{id}'),
            parent=self.last_seen_item,
            identifier=next(self.counter),
            level=self.last_seen_item.level + 1,
            plural=plural
        )

        self.inner.append(item)

    @staticmethod
    def from_definition(definition, printer):
        stack = CompilerStack(printer)

        parent = CompilerStackItem(
            printer,
            None,
            None,
            'main_value',
            None,
            None,
            0,
            False
        )

        stack.inner.append(CompilerStackItem(
            printer=printer,
            node=definition,
            parent_var='root',
            container_var=None,
            parent=parent,
            identifier=next(stack.counter),
            level=1
        ))

        return stack


def compile_scraper(definition, as_string=False):
    output = StringIO()

    def p(string, level=0, **kwargs):
        if kwargs:
            string = string.format(**kwargs)

        # Note: from extraneous state above
        if level:
            string = ('  ' * level) + string

        print(string, file=output)

    scope = {}

    p('def scrape(root, context={}):')
    p('  main_value = None')

    counter = itertools.count()

    stack = CompilerStack.from_definition(definition, p)

    while not stack.empty():
        item = stack.pop()

        with item:
            node = item.node

            if node is None or (isinstance(node, str) and node in EXTRACTOR_NAMES):
                item.print('{container}.append({parent}.get_text().strip())')
                continue

            if isinstance(node, str):
                item.print('{container}.append({parent}.get("""{attr}"""))', attr=node)
                continue

            if 'iterator' in node:
                item.print(
                    'elements_{id} = {parent}.select("""{selector}""")',
                    selector=node['iterator']
                )
                item.print('value_{id} = []')
                item.print('for element_{id} in elements_{id}:')

                if 'item' in node:
                    stack.append(
                        node=node['item'],
                        plural=True
                    )
                else:
                    stack.append(
                        node=None,
                        plural=True
                    )

    p('  return main_value')

    # Only return string
    if as_string:
        return output.getvalue()

    # Execute in scope to create function
    exec(output.getvalue(), scope)

    return scope['scrape']
