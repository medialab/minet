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
