from minet.web import request, extract_response_meta, looks_like_html

err, response = request('https://news.ycombinator.com/')
del response.headers['Content-Type']

print(response.status)
meta = extract_response_meta(response)
# print(response.data)
print(meta)
