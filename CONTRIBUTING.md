# Contributing to minet

## Summary

* [Installing a dev environment](#installing-a-dev-environment)
* [Testing changes to the CLI](#testing-changes-to-the-cli)
* [Linting & unit tests](#linting--unit-tests)

## Installing a dev environment

First you will need to clone the repo (or your fork):

```bash
git clone https://github.com/medialab/minet
```

Then you will need to install the project's dependencies by running:

```bash
make deps
```

We recommend that you do so in a python virtual environment to guarantee other dependencies won't crash with the project's.

## Testing changes to the CLI

To run your local minet version on the command line, add this line in your `.bashrc`, `.zshrc` or `.bash_profile` etc. file:

```bash
alias lminet="python -m minet.cli"
```

You can now run the commands using `lminet` instead of `minet` to test your changes locally without clashing with the global command if installed.

You can also install `minet` as a package in your curent environment like so:

```bash
pip install -e .
```

But be sure not to conflict with a standalone install of the tool.

## Linting & unit tests

To lint the code and run the unit tests you can use the following command:

```bash
# Only linter
make lint

# Only unit tests
make test

# Both
make
```

**Always** run `make` and add relevant unit tests before submitting any pull request to ensure your additions will not break the tool.

If you edited the CLI's help in `minet/cli/commands.py`, please run the following command to regenerate the related markdown documentation:

```bash
make readme
```

## Adding a new CLI command

Imagine we want to add a new command to minet, something like `minet platform script`.

* First go in the `minet/cli/commands.py` file and add the command in the MINET_COMMANDS dictionary (take example on other similar commands to write it).

* Then create a `platform` folder in the `minet/cli` folder and add a `script.py` file in it. In this file, create a function called `platform_script_action` that will execute the code you want to run when calling the `minet platform script` command.

* Finally create an `__init__` file at the root of your `platform` folder with the following code:
```
import sys

def platform_action(cli_args):
    if cli_args.pf_action == 'script':
        from minet.cli.platform.script import platform_script_action
        platform_script_action(cli_args)
```

After these three steps, you should be able to test your newly created command using:
```
lminet platform script
```

When your command is finalized, do not forget to add your command's documentation (written by you in the `minet/cli/commands.py` file) in the `Minet Command Line Usage` documentation file that can be found in `docs/cli.md`.
To do so, you should do three things:

* In the `docs/cli.template.md` file, in the `*Platform-related commands*` section (around the line 20-30) you should add:
```
* [platform (pf)](#platform)
  * [script](#platform-script)
```
[Please respect the alphabetical order between the platforms when adding those lines.]

* Around the end of the same file, you should add:
```
## Platform

<% pf %>

<h3 id="platform-script">script</h3>

<% pf/script %>
```

* Finally run:

```
make readme
```
so that the `docs/cli.template.md` file you modified will change the `docs/cli.md` file.