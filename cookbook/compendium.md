# Minet Examples Compendium

This document list many examples of using **minet** from the command line to achieve various goals.

## Summary

* [Extract raw text content from HTML pages](#extract-raw-text-content-from-html-pages)
* [Parsing and normalizing urls](#parsing-and-normalizing-urls)

## Extract raw text content from HTML pages

```bash
# From a `minet fetch` report:
minet extract report.csv > extracted.csv

# Directly from a bunch of HTML files:
minet extract --glob "./html/*.html" > extracted.csv
```

## Parsing and normalizing urls

```bash
minet url-parse url articles.csv > articles-parsed.csv
```
