# Minet Library Google Utilities

Documentation for the utilities found in the `minet.google` subpackage.

## Summary

* [export_google_sheets_as_csv](#export_google_sheets_as_csv)

## export_google_sheets_as_csv

Function taking either a google sheets url, a google sheets sharing url or a google sheets id and returning it as a CSV file. It can optionally take or retrieve your google drive authentication cookies to access non-public sheets.

```python
from minet.google import export_google_sheets_as_csv

url = 'https://docs.google.com/spreadsheets/d/16qMVxHWthPzm9Jha5tgcgL-flfexJceLFxITGyhF4rc/edit#gid=0'

data = export_google_sheets_as_csv(url)

# Writing the result to a file
with open('file.csv', 'w') as f:
  f.write(data)

# Reading the output as a CSV on the fly
import csv
from io import StringIO

reader = csv.DictReader(StringIO(data))

for line in reader:
  print(line)

# Extracting cookies from Firefox because your sheet is not public
data = export_google_sheets_as_csv(url, cookie='firefox')
```

*Arguments*

* **target** *str*: url, sharing url or id of sheets to retrieve.
* **cookie** *?str*: either your Google drive authentication cookie or the name of the browser to extract it from (e.g. 'firefox', 'chrome' etc.).
* **authuser** *?int*: if you are connected to multiple google accounts at once and know which account the sheets are related to, you can pass it thusly.
* **max_authuser_attempts** *?int* [`4`]: if **authuser** is not given, sets how many times the function will try to increment the `authuser` parameter to find the correct one automatically.
