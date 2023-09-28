import mechanicalsoup
import re
import time
import copy
import random
def parse_file(filename: str):
    """
    Parses a file and returns it as a set
    """
    contents=set()
    try:
        with open(filename) as file:
            for line in file:
                contents.add(line.strip())
        print("Loaded {}".format(filename))
        return contents
    except:
        raise Exception("{} cannot be parsed.".format(filename))
    
web_urls = ["http://localhost:80/fuzzer-tests/index.php",
"http://localhost:80/fuzzer-tests/index.php?message=Back+Home!",
"http://localhost:80/fuzzer-tests/admin.php"
]

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
SANITIZED_CHARS=parse_file("files/sanitation.txt")
SENSITIVE=parse_file("files/sensitive.txt")
VECTORS=parse_file("files/vectors.txt")
SLOW = 500
def vector_test(web_url_with_inputs):

    for page in web_url_with_inputs:
        print("\t" + page)
        browser.open(page)
        
        browser.select_form()
        inputs = browser.get_current_page().find_all("input")
        for input in inputs:
            fields = input.attrs
            if fields['type'] == 'text':
                ALREADY_CHECKED_SANITIZED=False
                ALREADY_CHECKED_STATUS_CODE=False
                ALREADY_CHECKED_SENSITIVE=False
                ALREADY_CHECKED_SLOW=False
                for vector in VECTORS:
                    browser.open(page)
                    browser.select_form()
                    browser[fields['name']] = vector
                    begin = time.perf_counter()
                    response = browser.submit_selected()
                    end = time.perf_counter()
                    if not ALREADY_CHECKED_STATUS_CODE and response.status_code != 200:
                        print("Broken input for field: " + fields['name'])
                        ALREADY_CHECKED_STATUS_CODE = True
                    if not ALREADY_CHECKED_SLOW and (end - begin) > SLOW:
                        print("Slow response")
                        ALREADY_CHECKED_SLOW = True

                    html_content = str(response.content)
                    if not ALREADY_CHECKED_SENSITIVE:
                        for word in SENSITIVE:
                            regex = re.findall("(?i)({})".format(word), html_content)
                            if regex:
                                print("Contains sensitive words:\n\t{}".format(regex))
                                ALREADY_CHECKED_SENSITIVE = True

                    if not ALREADY_CHECKED_SANITIZED:
                        for word in SANITIZED_CHARS:
                            regex = re.findall("(?i)({})".format(word), html_content)
                            if regex:
                                print("Vector {} may not be sanitized.".format(word))
                                ALREADY_CHECKED_SANITIZED=True



vector_test(web_urls)


