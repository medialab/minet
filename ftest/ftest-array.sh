#!/bin/bash
set -e
MINET="python -m minet.cli"

echo "Minet version:"
$MINET --version
echo

echo "Cookies:"
$MINET cookies firefox --url https://www.lemonde.fr
echo

echo "Fetch & Scrape"
$MINET fetch https://news.ycombinator.com/ | $MINET scrape ftest/scrapers/hackernews.json - | wc -l
echo

echo "Fetch & Extract"
$MINET fetch https://github.com/medialab/minet | $MINET extract - | wc -l
echo

echo "Resolve"
$MINET resolve https://medialab.sciencespo.fr/ | grep hit
echo

echo "Extract"
$MINET fetch https://news.ycombinator.com/ | $MINET url-extract raw_contents - --from html | wc -l
echo

echo "Url Join"
cat ftest/resources/entities.csv | $MINET url-join url - url ftest/resources/medias.csv | wc -l
echo

echo "Url Parse"
$MINET url-parse url -i ftest/resources/medias.csv | wc -l
echo

echo "Scraping Twitter"
$MINET twitter scrape tweets "from:medialab_ScPo" --limit 40 | wc -l
echo
