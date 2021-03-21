# =============================================================================
# Minet Scraper Compilation
# =============================================================================
#
# Schemes related to scraper definition "compilation".
#
import itertools
import soupsieve
from io import StringIO

from minet.scrape.constants import EXTRACTOR_NAMES


def escape_string_as_literal(string):
    double_quotes = string.count('"')
    single_quotes = string.count('\'')

    quote = '"' if single_quotes > double_quotes else '\''

    return quote + string.replace(quote, '\\' + quote) + quote


class CompilerContext(object):
    def __init__(self, printer, counter=None, level=0, var='root', container='main_value',
                 parent=None):
        self.printer = printer
        self.counter = counter if counter is not None else itertools.count(0)

        self.level = level
        self.identifier = next(self.counter)
        self.container = container
        self.var = var
        self.parent = parent

        self.container_type = 'var'
        self.container_key = None

    def descend(self):
        return CompilerContext(
            printer=self.printer,
            counter=self.counter,
            level=self.level + 1,
            var='element_%i' % self.identifier,
            container='value_%i' % self.identifier,
            parent=self
        )

    def linger(self):
        context = CompilerContext(
            printer=self.printer,
            counter=self.counter,
            level=self.level,
            var='element_%i' % self.identifier,
            container='value_%i' % self.identifier,
            parent=self
        )

        return context

    def print(self, string, **kwargs):
        self.printer(
            string,
            level=self.level,
            parent=self.parent.identifier,
            id=self.identifier,
            next=self.identifier + 1,
            **kwargs
        )

    def yield_to_parent(self, expr, **kwargs):
        if self.parent.container_type == 'list':
            self.print('value_{parent}.append(%s)' % expr, **kwargs)
        elif self.parent.container_type == 'dict':
            self.print('value_{parent}[%s] = %s' % (escape_string_as_literal(self.parent.container_key), expr), **kwargs)
        else:
            self.print('value_{parent} = %s' % expr, **kwargs)


class FieldsNode(object):
    def __init__(self, definition):
        self.definition = definition

    def unwrap(self):
        return self.definition


def compile_scraper(definition, as_string=False):
    output = StringIO()

    def printer(string, level=0, **kwargs):
        if kwargs:
            string = string.format(**kwargs)

        # Note: from extraneous state above
        if level:
            string = ('  ' * level) + string

        print(string, file=output)

    scope = {
        'soupsieve': soupsieve
    }

    printer('def scrape(root, context={}):')
    printer('  value_0 = None')
    printer('  element_1 = root')

    root_context = CompilerContext(printer)
    initial_context = root_context.descend()

    def recurse(node, context):

        # Default extraction
        if node is None or (isinstance(node, str) and node in EXTRACTOR_NAMES):
            context.yield_to_parent('element_{id}.get_text().strip()')
            return

        # Attribute
        if isinstance(node, str):
            context.yield_to_parent('element_{id}.get({attr})', attr=escape_string_as_literal(node))
            return

        # Fields
        if isinstance(node, FieldsNode):
            fields = node.unwrap()
            context.container_type = 'dict'

            context.print('value_{id} = dict()')

            for k, spec in fields.items():
                context.container_key = k
                next_context = context.linger()
                context.print('element_{target} = element_{id}', target=next_context.identifier)
                recurse(spec, next_context)

            context.yield_to_parent('value_{id}')

            return

        # Iterating
        if 'iterator' in node:
            context.container_type = 'list'

            context.print('elements_{id} = soupsieve.select({selector}, element_{id})', selector=escape_string_as_literal(node['iterator']))
            context.print('value_{id} = []')

            context.print('for element_{next} in elements_{id}:')

            if 'fields' in node:
                recurse(FieldsNode(node['fields']), context.descend())
            else:
                recurse(node.get('item'), context.descend())

            context.yield_to_parent('value_{id}')

    recurse(definition, initial_context)

    printer('  return value_0')

    # Only return string
    if as_string:
        return output.getvalue()

    # Execute in scope to create function
    exec(output.getvalue(), scope)

    return scope['scrape']
