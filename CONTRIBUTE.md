# Guidelines and tips for contributors

## Installation

To get the code locally:
```
git clone https://github.com/medialab/minet
```

To install the dependencies needed for minet:
```
make deps
```

## To test your changes

To run your local minet version on the command line, add this line in your `.bashrc` or `.bash_profile` file:
```
alias lminet="python -m minet.cli"
```
You can now run the commands using `lminet` instead of `minet` to test your changes.

## Before making a pull request

*Always* run this to ensure your new code complies with the linter recommendations et does not break any unit test:
```
make
```

If needed, please run this to regenerate the cli documentation:
```
make readme
```
