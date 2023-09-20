import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
string = "http://localhost:80//vulnerabilities//brute/"
print(re.sub(r"(https?://[^/\s]+)(/{2,})", r'\1/', string))

# import mechanicalsoup
# browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
# def check_page_status(web_url):
#     """
#     Checks if the response code for a web page is 200
#     """
#     response = browser.open(web_url)
#     print(response)
#     return response.status_code == 200
# web_url = "http://localhost:80/fuzzer-tests/CioffiIsTheBest.html"
# print(check_page_status(web_url))