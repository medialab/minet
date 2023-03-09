#!/bin/bash
set -e
MINET="python -m minet.cli"
EXTRACT_DIR=ftest/resources/extraction

echo "Minet version:"
$MINET --version
echo

echo "Cookies:"
$MINET cookies firefox --url https://www.lemonde.fr
echo

# echo "Fetch & Scrape"
echo "Scrape"
echo "  - Single HTML file"
$MINET scrape -p 1 $EXTRACT_DIR/scraper.yml $EXTRACT_DIR/article.html | wc -l
echo "  - Single glob pattern"
$MINET scrape -p 1 $EXTRACT_DIR/scraper.yml "$EXTRACT_DIR/*.html" -g | wc -l
echo "  - CSV input"
$MINET scrape -p 1 $EXTRACT_DIR/scraper.yml name -i $EXTRACT_DIR/articles.csv -I $EXTRACT_DIR | wc -l
echo "  - CSV bodies"
$MINET scrape -p 1 $EXTRACT_DIR/scraper.yml -i $EXTRACT_DIR/bodies.csv --body-column html | wc -l
echo "  - Piping fetch"
$MINET fetch https://github.com/medialab/minet | $MINET scrape -p 1 $EXTRACT_DIR/scraper.yml -i - | wc -l
echo

echo "Extract"
echo "  - Single HTML file"
$MINET extract -p 1 $EXTRACT_DIR/article.html | wc -l
echo "  - Single glob pattern"
$MINET extract -p 1 "$EXTRACT_DIR/*.html" -g | wc -l
echo "  - CSV input"
$MINET extract -p 1 name -i $EXTRACT_DIR/articles.csv -I $EXTRACT_DIR | wc -l
echo "  - CSV bodies"
$MINET extract -p 1 -i $EXTRACT_DIR/bodies.csv --body-column html | wc -l
echo "  - Piping fetch"
$MINET fetch https://github.com/medialab/minet | $MINET extract -p 1 -i - | wc -l
echo

echo "Resolve"
$MINET resolve https://medialab.sciencespo.fr/ | grep hit
echo

echo "Url Extract"
$MINET fetch https://news.ycombinator.com/ | $MINET url-extract body - --from html | wc -l
echo

echo "Url Join"
cat ftest/resources/entities.csv | $MINET url-join url - url ftest/resources/medias.csv | wc -l
echo

echo "Url Parse"
$MINET url-parse url -i ftest/resources/medias.csv | wc -l
echo

echo "Url Parse --explode"
$MINET url-parse url -i ftest/resources/plural_urls.csv --explode '|' | wc -l
echo

echo "Scraping Twitter"
$MINET twitter scrape tweets "from:medialab_ScPo" --limit 40 | wc -l
echo
