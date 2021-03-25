# =============================================================================
# Minet Scraper Constants
# =============================================================================
#
# Constants used throughout the minet.scrape package.
#
EXTRACTOR_NAMES = ['text', 'html', 'inner_html', 'outer_html']
SELECT_ALIASES = ['sel', '$']
ITERATOR_ALIASES = ['iterator', '$$']
PLURAL_MODIFIERS = ['filter', 'filter_eval', 'uniq']
BURROWING_KEYS = ITERATOR_ALIASES + ['item', 'fields']
LEAF_KEYS = ['attr', 'extract', 'get_context', 'eval', 'default']
