# =============================================================================
# Minet Telegram CLI Action
# =============================================================================
#
# Logic of the `tl` action.
#


def telegram_action(cli_args):

    if cli_args.tl_action == "channel-infos":

        from minet.cli.telegram.channel_infos import channel_infos_action

        channel_infos_action(cli_args)

    elif cli_args.tl_action == "channel-messages":

        from minet.cli.telegram.channel_messages import channel_messages_action

        channel_messages_action(cli_args)
