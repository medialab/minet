from minet.cli.buzzsumo import BUZZSUMO_COMMAND
from minet.cli.crowdtangle import CROWDTANGLE_COMMAND
from minet.cli.facebook import FACEBOOK_COMMAND
from minet.cli.google import GOOGLE_COMMAND
from minet.cli.hyphe import HYPHE_COMMAND
from minet.cli.instagram import INSTAGRAM_COMMAND
from minet.cli.mediacloud import MEDIACLOUD_COMMAND
from minet.cli.telegram import TELEGRAM_COMMAND
from minet.cli.tiktok import TIKTOK_COMMAND
from minet.cli.twitter import TWITTER_COMMAND
from minet.cli.url_parse import URL_PARSE_COMMAND

# TODO: move to commands.py in the end
MINET_COMMANDS = {
    "buzzsumo": BUZZSUMO_COMMAND,
    "crowdtangle": CROWDTANGLE_COMMAND,
    "facebook": FACEBOOK_COMMAND,
    "google": GOOGLE_COMMAND,
    "hyphe": HYPHE_COMMAND,
    "instagram": INSTAGRAM_COMMAND,
    "mediacloud": MEDIACLOUD_COMMAND,
    "telegram": TELEGRAM_COMMAND,
    "tiktok": TIKTOK_COMMAND,
    "url-parse": URL_PARSE_COMMAND,
    "twitter": TWITTER_COMMAND,
}
