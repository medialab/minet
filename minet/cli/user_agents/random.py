from minet.user_agents import get_random_user_agent


def action(cli_args):
    cli_args.output.write(get_random_user_agent() + "\n")
