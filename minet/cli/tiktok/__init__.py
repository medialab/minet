# =============================================================================
# Minet Tiktok CLI Action
# =============================================================================
#
# Logic of the `tk` action.
#


def tiktok_action(cli_args):

    if cli_args.tk_action == "search-videos":

        from minet.cli.tiktok.search_videos import search_videos_action

        search_videos_action(cli_args)
