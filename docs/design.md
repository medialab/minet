# CLI Design Considerations

## Use cases decanter

`fetch` polymorphism

```shell
# Consuming urls from CSV file
minet fetch url_column file.csv -d html_folder > report.csv

# Consuming urls from CSV unix stream
xsv select url_column file.csv | minet fetch url_column -d html_folder > report.csv

# Consuming a single url (for piping into `scrape` e.g.)
minet fetch http://google.fr -d html_folder

# Override stdout
minet fetch url_column file.csv -d html_folder -o report.csv

# Resuming
minet fetch url_column file.csv -d html_folder --resume-from report.csv
```

`extract` polymorphism

```shell
# Consuming files from a CSV report
minet extract report.csv -i html_folder > dragnet.csv

# Consuming report from unix stream
minet fetch url_column file.csv -d html_folder | minet extract -i html_folder > dragnet.csv

# Extracting from glob
minet extract "./content/*.html" --glob > dragnet.csv
```

`scrape` polymorphism

```shell
# Consuming files from a CSV report
minet scrape ./scraper.json report.csv -i html_folder > scraped.csv

# Consuming report from unix stream
minet fetch url_column file.csv -d html_folder | minet scrape ./scraper.json -i html_folder > scraped.csv

# Scraping from glob
minet scrape ./scraper.json "./content/*.html" --glob > scraped.csv
```
