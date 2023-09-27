import re
def parse_url(url):
    parsed_url = re.sub(r'(https?://[^/]+)/(?!$)|/{2,}', r'\1/', re.sub(r'(https?://[^/]+)/+', r'\1/', url))
    return parsed_url

print(parse_url("http://localhost:80/////vulnerabilities/////sqli////"))