# Fetching a bunch of urls from the web

Let's say you are interested in what urls are shared by some Twitter accounts and you suceeded in collecting them using a dedicated tool ([gazouilloire](https://github.com/medialab/gazouilloire) or [TCAT](https://github.com/digitalmethodsinitiative/dmi-tcat), for instance).

You now have a large bunch of urls shared by people and want to move on to the next step: what if we analyzed the text content linked by those urls to see what people are speaking about.

You will obviously need to download the pages before being able to do anything.

Let's use the `minet fetch` command to do so!

## Summary

* [Summary](#summary)
* [Baby steps](#baby-steps)
* [Options, options, options](#options-options-options)
  * [Customizing the output directory and file names](#customizing-the-output-directory-and-file-names)
  * [Throttling](#throttling)
  * [Displaying a finite loading bar](#displaying-a-finite-loading-bar)
  * [Keeping only selected columns in report](#keeping-only-selected-columns-in-report)
  * [Standardizing encoding of fetched files](#standardizing-encoding-of-fetched-files)
  * [Resuming an operation](#resuming-an-operation)
* [Unix compliance](#unix-compliance)

## Baby steps

Being a diligent researcher, you decided to store the found url in a very simple [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file containing more than 50k urls:

*urls.csv*

| id    | url                          |
|-------|------------------------------|
| 1     | https://www.lemonde.fr       |
| 2     | https://www.lefigaro.fr      |
| 3     | https://www.liberation.fr    |
| ...   | ...                          |
| 54038 | https://news.ycombinator.com |

You could very well create a script that will fetch the url one by one until you are done. But the Internet is quite slow and this could take a while. `minet`, on the contrary, is able to leverage [multithreading](https://en.wikipedia.org/wiki/Multithreading) to fetch multiple urls at once (typically at least 25) so you can complete this task faster.

Here is what you would need to type in your terminal to make it happen:

```bash
minet fetch url urls.csv > report.csv
```

You will need to give at least two pieces of information to `minet` so it can work its magic:

1. `minet` needs to know the name you gave to the column containing urls in your CSV file.
2. Then `minet` needs to know where you put the beforementioned CSV file.

When firing this command, `minet` will start fetching the urls in your file as fast as possible while writing the found HTML files into a folder named `content` in your working directory.

To help you figure out which urls are now dead (404, for instance) or to be able to give you additional information `minet` will also print a CSV report to your terminal.

This CSV report is in fact a copy of the input file with some added columns such as `status` giving you the HTTP status code of the response or `encoding`, telling you how the response was encoded.

But since reading the report in your terminal might not be very handy, our example redirects what is printed into the `report.csv` file using this handy piece of shell syntax: `>`.

## Options, options, options

Most of `minet` commands come with a wide array of options. If you ever feel lost, or forgot some option or argument? Don't forget you can always ask `minet` to help you remember:

```bash
# This work with every command
minet fetch --help

# Or if you are in a hurry:
minet fetch -h
```

Now let's check some of the most useful options of the `fetch` command:

### Customizing the output directory and file names

### Throttling

### Displaying a finite loading bar

### Keeping only selected columns in report

### Standardizing encoding of fetched files

### Resuming an operation

## Unix compliance

Whenever possible, `minet` tries to be Unix-compliant. This means that most of its output is printed to `stdout` so you can pipe the results into other commands:

```bash
# Only interested in the frequency of http codes?
minet fecth url urls.csv | xsv frequency -s status
```

Note that I often use the wonderful CSV handling CLI tool [xsv](https://github.com/BurntSushi/xsv) in my examples because I tend to use it a lot. But other similar tools exists: be sure to check out [miller](https://github.com/johnkerl/miller) and [csvkit](https://csvkit.readthedocs.io/en/latest/), for instance.

Also, `minet` is perfectly capable of handling `stdin` if you need to:

```bash
# Want to filter the input file to fetch only facebook urls?
xsv search -s url facebook | minet fetch url > report.csv
```
