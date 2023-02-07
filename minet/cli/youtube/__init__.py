# =============================================================================
# Minet Youtube CLI Action
# =============================================================================
#
# Logic of the `yt` action.
#
from minet.cli.argparse import command, subcommand, ConfigAction, SplitterType

# TODO: this is a lazyloading issue
from minet.youtube.constants import (
    YOUTUBE_API_DEFAULT_SEARCH_ORDER,
    YOUTUBE_API_SEARCH_ORDERS,
)

KEY_ARGUMENT = {
    "flags": ["-k", "--key"],
    "help": "YouTube API Data dashboard API key. Can be used more than once.",
    "rc_key": ["youtube", "key"],
    "action": ConfigAction,
    "plural": True,
    "required": True,
}


def youtube_api_subcommand(*args, arguments=[], **kwargs):
    return subcommand(*args, arguments=arguments + [KEY_ARGUMENT], **kwargs)


YOUTUBE_CAPTIONS_SUBCOMMAND = subcommand(
    "captions",
    "minet.cli.youtube.captions",
    title="Youtube captions",
    description="Retrieve captions for the given YouTube videos.",
    epilog="""
        examples:

        . Fetching captions for a list of videos:
            $ minet yt captions video_id videos.csv > captions.csv

        . Fetching French captions with a fallback to English:
            $ minet yt captions video_id videos.csv --lang fr,en > captions.csv
    """,
    variadic_input={
        "dummy_column": "video",
        "item_label": "video url or id",
        "item_label_plural": "video urls or ids",
    },
    select=True,
    total=True,
    arguments=[
        {
            "flag": "--lang",
            "help": 'Language (ISO code like "en") of captions to retrieve. You can specify several languages by preferred order separated by commas. Defaults to "en".',
            "default": ["en"],
            "type": SplitterType(),
        }
    ],
)

YOUTUBE_CHANNEL_VIDEOS_SUBCOMMAND = youtube_api_subcommand(
    "channel-videos",
    "minet.cli.youtube.channel_videos",
    title="Youtube channel videos",
    description="""
        Retrieve metadata about all Youtube videos from one or many channel(s) using the API.

        Under the hood, this command extract the channel id from the given url or scrape the
        website to find it if necessary. Then the command uses the API to retrieve
        information about videos stored in the main playlist of the channel
        supposed to contain all the channel's videos.
    """,
    epilog="""
        example:

        . Fetching all the videos from a channel based on the channel's id or url:
            $ minet youtube channel-videos https://www.youtube.com/c/LinksOff -k my-api-key > linksoff_videos.csv
            $ minet youtube channel-videos https://www.youtube.com/channel/UCqnbDFdCpuN8CMEg0VuEBqA -k my-api-key > thenewyorktimes_videos.csv
            $ minet youtube channel-videos UCprclkVrNPls7PR-nHhf1Ow -k my-api-key > tonyheller_videos.csv

        . Fetching multiple channels' videos:
            $ minet youtube channel-videos channel_id channels_id.csv -k my-api-key > channels_videos.csv
            $ minet youtube channel-videos channel_url channels_url.csv -k my-api-key > channels_videos.csv
    """,
    variadic_input={"dummy_column": "channel"},
    select=True,
    total=True,
)

YOUTUBE_CHANNELS_SUBCOMMAND = youtube_api_subcommand(
    "channels",
    "minet.cli.youtube.channels",
    title="Youtube Channels Command",
    description="""
        Retrieve metadata about Youtube channel from one or many name(s) using the API.

        Under the hood, this command extract the channel id from the given url or scrape the
        website to find it if necessary. Then the command uses the API to retrieve
        information about the channel.
    """,
    epilog="""
        example:

        . Fetching metadata from a channel based on the channel's id or url:
            $ minet youtube channels https://www.youtube.com/c/LinksOff -k my-api-key > linksoff_meta.csv
            $ minet youtube channels https://www.youtube.com/channel/UCqnbDFdCpuN8CMEg0VuEBqA -k my-api-key > thenewyorktimes_meta.csv
            $ minet youtube channels UCprclkVrNPls7PR-nHhf1Ow -k my-api-key > tonyheller_meta.csv

        . Fetching multiple channels' metadata:
            $ minet youtube channels channel_id channels_id.csv -k my-api-key > channels.csv
            $ minet youtube channels channel_url channels_url.csv -k my-api-key > channels.csv
    """,
    variadic_input={"dummy_column": "channel"},
    select=True,
    total=True,
)

YOUTUBE_COMMENTS_SUBCOMMAND = youtube_api_subcommand(
    "comments",
    "minet.cli.youtube.comments",
    title="Youtube comments",
    description="Retrieve metadata about Youtube comments using the API.",
    epilog="""
        example:

        . Fetching a video's comments:
            $ minet yt comments https://www.youtube.com/watch?v=7JTb2vf1OQQ -k my-api-key > comments.csv
    """,
    variadic_input={"dummy_column": "video"},
    select=True,
    total=True,
)

YOUTUBE_SEARCH_SUBCOMMAND = youtube_api_subcommand(
    "search",
    "minet.cli.youtube.search",
    title="Youtube search",
    description="Retrieve metadata about Youtube search field using the API.",
    epilog="""
        example:

        . Searching videos about birds:
            $ minet youtube search bird -k my-api-key > bird_videos.csv
    """,
    variadic_input={"dummy_column": "query", "item_label_plural": "queries"},
    select=True,
    total=True,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of videos to retrieve per query.",
            "type": int,
        },
        {
            "flags": ["--order"],
            "help": "Order in which videos are retrieved. The default one is relevance.",
            "default": YOUTUBE_API_DEFAULT_SEARCH_ORDER,
            "choices": YOUTUBE_API_SEARCH_ORDERS,
        },
    ],
)

YOUTUBE_VIDEOS_SUBCOMMAND = youtube_api_subcommand(
    "videos",
    "minet.cli.youtube.videos",
    title="Youtube videos",
    description="Retrieve metadata about Youtube videos using the API.",
    variadic_input={"dummy_column": "video"},
    select=True,
    total=True,
)

YOUTUBE_COMMAND = command(
    "youtube",
    "minet.cli.youtube",
    "Minet YouTube Command",
    aliases=["yt"],
    description="""
        Gather data from Youtube.
    """,
    subcommands=[
        YOUTUBE_CAPTIONS_SUBCOMMAND,
        YOUTUBE_CHANNEL_VIDEOS_SUBCOMMAND,
        YOUTUBE_CHANNELS_SUBCOMMAND,
        YOUTUBE_COMMENTS_SUBCOMMAND,
        YOUTUBE_SEARCH_SUBCOMMAND,
        YOUTUBE_VIDEOS_SUBCOMMAND,
    ],
)
