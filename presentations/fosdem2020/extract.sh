minet fetch https://echojs.com |
minet scrape echojs.yml |
minet fetch link --filename title -d html --total 30 > report.csv

minet extract -I html report.csv > contents.csv
