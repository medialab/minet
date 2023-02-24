python -m minet.cli fetch url -i ftest/resources/urls.csv \
  -O ftest/content \
  --filename id \
  --folder-strategy normalized-hostname \
  --grab-cookies firefox \
  --compress \
  -s id,url \
  -t 25 \
  -o ftest/report.csv --resume
