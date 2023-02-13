# Fetching a large amount of urls

Let's say you are interested in what urls are shared by some Twitter accounts and you suceeded in collecting them using a dedicated tool ([gazouilloire](https://github.com/medialab/gazouilloire) or [TCAT](https://github.com/digitalmethodsinitiative/dmi-tcat), for instance).

You now have a large bunch of urls shared by people and want to move on to the next step: what if we analyzed the text content linked by those urls to see what people are speaking about?

You will obviously need to download the pages before being able to do anything.

Let's use the `minet fetch` command to do so!

## Summary

- [First steps](#first-steps)
- [Options](#options)
  - [Customizing the output directory and file names](#customizing-the-output-directory-and-file-names)
  - [Throttling & Threading](#throttling--threading)
  - [Displaying a finite loading bar](#displaying-a-finite-loading-bar)
  - [Keeping only selected columns in report](#keeping-only-selected-columns-in-report)
  - [Standardizing encoding of fetched files](#standardizing-encoding-of-fetched-files)
  - [Resuming an operation](#resuming-an-operation)
- [Unix compliance](#unix-compliance)
- [Fetching from a python script](#fetching-from-a-python-script)

## First steps

Being a diligent researcher, you decided to store the found urls in a very simple [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file containing more than 50k urls:

_urls.csv_

| id    | url                          |
| ----- | ---------------------------- |
| 1     | https://www.lemonde.fr       |
| 2     | https://www.lefigaro.fr      |
| 3     | https://www.liberation.fr    |
| ...   | ...                          |
| 54038 | https://news.ycombinator.com |

You could very well create a script that will fetch the url one by one until you are done. But the Internet is quite slow and this could take a while. `minet`, on the contrary, is able to leverage [multithreading](https://en.wikipedia.org/wiki/Multithreading) to fetch multiple urls at once (typically at least 25) so you can complete this task faster.

Here is what you would type in your terminal to make it happen:

```bash
minet fetch url urls.csv > report.csv
```

`minet` needs at least two pieces of information to be able to work its magic:

1. the name you gave to the column containing urls in your CSV file.
2. the location of the beforementioned CSV file.

When firing this command, `minet` will start fetching the urls from the indicated column as fast as possible while writing the found HTML files into a folder named `content`, in your working directory.

To help you figure out which urls are now dead (404, for instance) or to be able to give you additional information `minet` will also print a CSV report to your terminal.

This CSV report is in fact a copy of the input file with some added columns such as `status` giving you the HTTP status code of the response or `encoding`, telling you how the response was encoded.

But since reading the report in your terminal might not be very handy, our example redirects what is printed into the `report.csv` file using this handy piece of shell syntax: `>`.

## Options

Most of `minet` commands come with a wide array of options. If you ever feel lost, or forgot some option or argument? Don't forget you can always ask `minet` to help you remember:

```bash
# This works with every command
minet fetch --help

# Or if you are in a hurry:
minet fetch -h
```

Now let's check some of the most useful options of the `fetch` command:

### Customizing the output directory and file names

#### Output directory

By default, `minet` will write the fetched files in a folder named `content` relative to your working directory. But maybe this is not what you want. Here is how to change this:

```bash
minet fetch url urls.csv -O /store/project/html > /store/project/report.csv
```

#### File names

Also, by default, because the Internet is a messy place and it could be hard to find an unambiguous name for all the fetched html files, `minet` will generate [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier)s to use as file names.

But you might want to customize your file names because you have relevant metadata: It is then possible to tell `minet` to use another column from your file as file name likewise:

_urls.csv_

| id    | url                          |
| ----- | ---------------------------- |
| 1     | https://www.lemonde.fr       |
| 2     | https://www.lefigaro.fr      |
| 3     | https://www.liberation.fr    |
| ...   | ...                          |
| 54038 | https://news.ycombinator.com |

```bash
minet fetch url urls.csv --filename id > report.csv

ls content
>>> 1.html 2.html 3.html ...
```

#### File paths

But what if you want more complex things? What if you want to create a specific folder hierarchy for performance or organizational reasons? It is also possible to pass a template to `minet` so it will be able to build the desired file paths.

_urls.csv_

| id    | url                          | media      |
| ----- | ---------------------------- | ---------- |
| 1     | https://www.lemonde.fr       | lemonde    |
| 2     | https://www.lefigaro.fr      | lefigaro   |
| 3     | https://www.liberation.fr    | liberation |
| ...   | ...                          | ...        |
| 54038 | https://news.ycombinator.com | hackernews |

```bash
minet fetch url urls.csv \
    --filename-template '{line["media"]}/{line["id"]}{ext}' \
    > report.csv

ls content
>>> hackernews lefigaro lemonde liberation

ls content/liberation
>>> 3.html
```

#### File paths performance tip

It is not a good idea to store hundreds of thousands files in a single directory because it can easily become a performance pit on some file systems. So, if you need to fetch a whole lot of urls, it can be a good idea to randomly distribute fetched files into directories based on the first characters of their names, for instance:

```bash
minet fetch url urls.csv --filename-template '{value[:4]}/{value}{ext}' > report.csv
# Which is basically the same as
minet fetch url urls.csv --folder-strategy prefix-4 > report.csv
```

Be sure to read everything about so called "folder strategies" in the command's help to see how you can leverage the different available strategies (such as putting files in folders by url hostname for instance).

### Throttling & Threading

Not to be too hard on servers and to avoid being kicked by those, `minet` throttles its requests by domain. But, by default, `minet` can still be a bit aggressive, using only a throttle of `0.2` seconds. You might want to change that:

```bash
# Waiting 2 seconds between requests on a same domain
minet fetch url urls.csv --throttle 2 > report.csv
```

Also, if your computer is powerful enough and if you know you are going to fetch pages from a wide variety of domains, you can increase the number of used threads to complete the task even faster:

```bash
minet fetch url urls.csv --threads 100 > report.csv
```

### Displaying a finite loading bar

By default, and because we cannot know the number of urls we have to fetch beforehand, `minet` displays an indefinite progress bar. If you happen to know the number of urls, you can indicate it likewise to have a more useful progress bar:

```bash
minet fetch url urls.csv --total 50000 > report.csv

# If your input file is not too large, this can be useful:
minet fetch url urls.csv --total `xsv count urls.csv` > report.csv
```

Note that most of `minet` commands recognize this `--total` option.

### Keeping only selected columns in report

If the input CSV file is very large and full of metadata, you might want to thin the report a little bit by selecting the columns to keep:

```bash
minet fetch url urls.csv -s url > report.csv

# To keep more that one column, separate their name with ",":
minet fetch url urls.csv -s id,url > report.csv
```

### Standardizing encoding of fetched files

The web is a messy place and not every page is wisely encoded in `utf-8`. As such, `minet`, like web browsers, attempts to guess the page's encoding and will indicate it in its report. However, you might also say that you are done with encoding issues and tell `minet` to standardize everything to `utf-8` for simplicity's sake:

```bash
minet fetch url urls.csv --standardize-encoding > report.csv
```

Just note that in some cases, where we cannot really find the correct encoding, this operation will be lossy as we may replace or delete some unknown characters.

### Resuming an operation

Let's say we started fetching urls likewise:

```bash
minet fetch url urls.csv > report.csv
```

But somewhere around the 1000th one, something broke, or Internet went down, or your server was shutdown by an unexpected power outage. This kind of things happens. Wouldn't it be nice if we could resume the process without having to restart from scratch?

Well you perfectly can and here is what you would need to change:

```bash
minet fetch url urls.csv -o report.csv --resume
```

## Unix compliance

Whenever possible, `minet` tries to be Unix-compliant. This means that most of its output is printed to `stdout` so you can pipe the results into other commands:

```bash
# Only interested in the frequency of http codes?
minet fetch url urls.csv | xsv frequency -s status
```

Note that I often use the wonderful CSV handling CLI tool [xsv](https://github.com/BurntSushi/xsv) in my examples because I tend to use it a lot. But other similar tools exists: be sure to check out [miller](https://github.com/johnkerl/miller) and [csvkit](https://csvkit.readthedocs.io/en/latest/), for instance.

Also, `minet` is perfectly capable of handling `stdin` if you need to:

```bash
# Want to filter the input file to fetch only facebook urls?
xsv search -s url facebook | minet fetch url - > report.csv
```

## Fetching from a python script

Maybe CLI is not your tool of choice and you prefer scripting right away. Maybe you need very specific logic not offered by `minet` CLI. You can still beneficiate from `minet` multithreaded logic in your own code. To do so, just use `minet` as a python library:

```python
import csv
from minet import multithreaded_fetch

with open('./urls.csv') as f:
    reader = csv.DictReader(f)

    for result in multithreaded_fetch(reader, key=lambda line: line['url']):
        if result.error is not None:
            print('Something went wrong', result.error)
        else:
            print(result.response.status)
```

Check out full documentation about this API [here](/README.md#multithreaded_fetch)
