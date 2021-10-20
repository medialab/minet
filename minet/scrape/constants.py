# =============================================================================
# Minet Scraper Constants
# =============================================================================
#
# Constants used throughout the minet.scrape package.
#
EXTRACTOR_NAMES = ['text', 'display_text', 'html', 'inner_html', 'outer_html']
SELECT_ALIASES = ['sel', '$']
ITERATOR_ALIASES = ['iterator', '$$']
PLURAL_MODIFIERS = ['filter', 'filter_eval', 'uniq']
BURROWING_KEYS = ITERATOR_ALIASES + ['item', 'fields']
LEAF_KEYS = ['attr', 'extract', 'get_context', 'eval', 'default']
KNOWN_KEYS = SELECT_ALIASES + PLURAL_MODIFIERS + BURROWING_KEYS + LEAF_KEYS + [
    'sel_eval',
    'iterator_eval'
]

BLOCK_ELEMENTS = {
    'article',
    'aside',
    'blockquote',
    'body',
    'br',
    'button',
    'canvas',
    'caption',
    'col',
    'colgroup',
    'dd',
    'div',
    'dl',
    'dt',
    'embed',
    'fieldset',
    'figcaption',
    'figure',
    'footer',
    'form',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'header',
    'hgroup',
    'hr',
    'li',
    'map',
    'object',
    'ol',
    'output',
    'p',
    'pre',
    'progress',
    'section',
    'table',
    'tbody',
    'textarea',
    'tfoot',
    'thead',
    'tr',
    'ul',
    'video'
}

CONTENT_BLOCK_ELEMENTS = {
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'p',
    'ul',
    'ol',
    'pre',
    'blockquote'
}
