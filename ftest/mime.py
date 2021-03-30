from minet.web import request, extract_response_meta

err, response = request('http://localhost:8000/dumb.html')
# del response.headers['Content-Type']

print(response.status)
meta = extract_response_meta(response)
print(response.data)
print(meta)
