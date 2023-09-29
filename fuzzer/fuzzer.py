import mechanicalsoup
import re
import time
from fuzzer_args import arg_parser
args = arg_parser().parse_args() # Namespace(type='discover', url='asdasdas', custom_auth=None, common_words=None, extensions=None, vectors=None, sanitized_chars=None, sensitive=None, slow=500)

# Error Handling
#if args.type == "discover" and (args.vectors or args.sanitized_chars or args.sensitive or args.slow): raise Exception("An option for {test} was used with {discover}. See py fuzzer.py -h for help.")

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
EXTENSIONS=set()
SANITIZED_CHARS=set()
SENSITIVE=set()
VECTORS=set()
def custom_auth():
    """ Custom authentication for known applications
    """
    auth = args.custom_auth
    if auth == "dvwa":
        print("Using DVWA as a custom authentication method...")
        # setup
        browser.open("{}/setup.php".format(args.url)) # gitlab ci uses python 3.5.2, fstrings not supported
        browser.select_form('form[action="#"]')
        browser.submit_selected()
        # login page
        browser.open(args.url)
        browser.select_form('form[action="login.php"]')
        browser["username"] = "admin" 
        browser["password"] = "password"
        browser.submit_selected()
        # security page
        browser.open("{}/security.php".format(args.url))
        browser.select_form('form[action="#"]')['security'] = 'low' # security is a select element
        browser.submit_selected()
        # back to home page
        browser.open(args.url)
    else:
        raise Exception("There is no custom-auth logic for {}".format(auth))
    print("Done!")

###########################################
# Discover
###########################################
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

def check_page_status(web_url):
    """
    Checks if the response code for a web page is 200
    """
    response = browser.open(web_url)
    return response.status_code == 200

def get_pages_from_url(web_url):
    """ Retreives web pages <a> tags from url 
    TODO: Fix url parsing
    """
    routes = set()
    if not re.findall("(\..*)$", web_url): # add a slash if there is no extension at the end of the website
        web_url = web_url + "/"
    browser.open(web_url)

    for tag in browser.page.select('a'):
        link = tag.get('href')
        if re.findall("(http://|https://|www.)", link): # skip external links
            continue
        try:
            if link in {".", "/"} or link.startswith("?C=") or link.endswith("logout.php"): # this is mostly for built-in pages that has folders in them
                continue
            full_link = re.sub("(\.\/)", "", "{}/{}".format(re.findall("^(.*[\\\/])[^\\\/]*$", web_url)[0], link))
            #if check_page_status(full_link):
            routes.add(parse_web_url(full_link))
        except: # requests.exceptions is thrown so avoid looking 
            pass
    return routes

def guess_pages(web_url, words, extensions):
    """
    Guess pages given a list of words and extensions
    """
    guessed_pages=set()
    for word in words:
        for ext in extensions:
            guessed_url = "{}/{}{}".format(web_url, word, ext)
            if check_page_status(guessed_url):
                guessed_pages.add(guessed_url)
    return guessed_pages

def crawl_pages(guessed_pages):
    """
    Crawled web pages
    """
    crawled = set()
    for page in guessed_pages:
        routes = get_pages_from_url(page)
        crawled.update(routes)
    return crawled

def get_input_fields(web_url):
    """ Returns list of html code that has a 'form' on it

    Returns None if it tries to fetch a form but cannot be found
    """
    try:
        browser.open(web_url)
        forms = browser.get_current_page().find_all('form')
        return forms
    except: return None

def get_urls_with_forms(valid_url, printForms=False):
    """ Returns a list of urls that has valid forms
    """
    urls_with_forms = set()
    for page in valid_url:
        fields = get_input_fields(page)
        if fields: # print forms if a form has been returned
            if printForms:  # print if required
                page_string = "************ {} ************".format(page)
                print(len(page_string) * "*")
                print(page_string)
                print(len(page_string) * "*")
                print(str(fields).encode("UTF-8"))
                print("\n")
            urls_with_forms.add(page)
    return urls_with_forms

def get_cookies(web_url):
    """
    Get cookies of a web_url
    """
    browser.open(web_url)
    cookies = browser.get_cookiejar()
    return cookies # key: cookie.name, value: cookie.value

def parse_url(web_url):
    """ Parses URL for any query parameters    
    """
    return web_url.split("?")
    # """ Given a web_url and an input (something=a, something=b, etc.), determines whether the web_url goes to the same page
    
    # Returns:
    #     bool: true if they're the same
    #     string: source and target urls
    # """
    # web_url = browser.open(web_url).url
    # before = web_url + "?" + input
    # response = browser.open(before)
    # after = response.url
    
    # src = re.match("^(.*?)(?:\?.*)?$", before).group(1)
    # target = re.match("^(.*?)(?:\?.*)?$", after).group(1)
    #return src == target, (src, target)

########################################
######            TEST            ######
########################################
def check_leaked_data_from_url(web_url):
    html_content = str(browser.open(web_url).content)

    for word in SENSITIVE:
        regex = re.findall("(?i)({})".format(word), html_content)
        if regex:
            print("\t{} contains sensitive words:\n\t\t{}".format(web_url, regex))

def check_for_delayed_response(web_url):
    """
    Checks whether a website hangs. Returns true if it hangs past args.slow
    """
    begin = time.perf_counter()
    browser.open(web_url)
    end = time.perf_counter()
    duration = end - begin
    if (duration > int(args.slow)/1000):
        return True, duration
    return False, duration

def test_page_status(web_url):
    """
    Checks if the response code for a web page is 200. Returns true if it is
    """
    response = browser.open(web_url)
    if response.status_code != 200:
        return False, response.status_code
    return True, response.status_code

def parse_web_url(web_url):
    """
    Parses web url and removes any repeated slashes
    """
    # please dont judge me
    return re.sub(r'(https?://[^/]+)/(?!$)|/{2,}', r'\1/', re.sub(r'(https?://[^/]+)/+', r'\1/', web_url))

def vector_test(web_url_with_inputs):

    for page in web_url_with_inputs:
        print(page)
        browser.open(page)
        
        browser.select_form()
        inputs = browser.get_current_page().find_all("input")
        for input in inputs:
            fields = input.attrs
            if fields['type'] == 'text':
                # ALREADY_CHECKED_SANITIZED=False
                # ALREADY_CHECKED_STATUS_CODE=False
                # ALREADY_CHECKED_SENSITIVE=False
                # ALREADY_CHECKED_SLOW=False
                for vector in VECTORS:
                    before = browser.open(page)
                    browser.select_form()
                    print (" \tSubmitting vector: {} on input: {}".format(vector, fields['name']))
                    browser[fields['name']] = vector
                    begin = time.perf_counter()
                    response = browser.submit_selected()
                    end = time.perf_counter()
                    if response.status_code != 200:
                        print("\t\tBroken input for field: " + fields['name'])
                    if (end - begin) > args.slow:
                        print("\t\tSlow response")

                    html_content = str(response.content)
                    for word in SENSITIVE:
                        regex = re.findall("(?i)({})".format(word), html_content)
                        if regex:
                            print("\t\tContains sensitive words:\n\t\t\t{}".format(regex))

                    for word in SANITIZED_CHARS:
                        regex = re.findall("(?i)({})".format(word), html_content)
                        if regex:
                            print("\t\tVector {} may not be sanitized.".format(word))
def main():
    if args.custom_auth:
        print("******************Using custom authentication******************")
        custom_auth()
        
    global EXTENSIONS 
    if args.extensions == None:
        EXTENSIONS = {"", ".php"}
    else:
        EXTENSIONS = parse_file(args.extensions)
    
    words = parse_file(args.common_words) # required

    if args.type == "discover":
        print("*************************************************************************************")
        print("************************************Guessed Pages************************************")
        print("*************************************************************************************")
        print("Guessing pages with {} words and {} extensions...".format(len(words), len(EXTENSIONS)))
        guessed_pages = guess_pages(args.url, words, EXTENSIONS)
        [print("\t" + str(guessed)) for guessed in guessed_pages]
        print("*************************************************************************************")
        print("************************************Crawled Pages************************************")
        print("*************************************************************************************")
        crawled = crawl_pages(guessed_pages)
        [print("\t" + str(crawl)) for crawl in crawled]
        print("******************************************************************************************************")
        print("************************************Parsed URLs (Query Parameters)*************************************")
        print("******************************************************************************************************")
        print("Guessed pages:")
        [print("\t" + str(parse_url(guessed))) for guessed in guessed_pages]
        print("Crawled pages:")
        [print("\t" + str(parse_url(crawl))) for crawl in crawled]
        print("****************************************************************************************")
        print("************************************ FORM PARAMETERS ************************************")
        print("****************************************************************************************")
        print("")
        print("*******************************Guessed pages*******************************")
        print()
        get_urls_with_forms(guessed_pages, True)
        print("*******************************END Guessed pages END *******************************\n\n")
        print("*******************************Crawled pages*******************************")
        print()
        get_urls_with_forms(crawled, True)
        print("*******************************END Crawled pages END *******************************\n\n")
        print("*****************************************************************************************")
        print("**************************************** Cookies ****************************************")
        print("*****************************************************************************************")
        cookies = get_cookies(args.url)
        if cookies:
            for cookie in cookies:
                print(cookie.name + ":" + cookie.value)
        else:
            print("No cookies :(")
    elif args.type == "test":
        global SENSITIVE
        SENSITIVE = parse_file(args.sensitive)
        global SANITIZED_CHARS
        if args.sanitized_chars == None:
            SANITIZED_CHARS = {"&lt;", "&gt;"}
        else:
            SANITIZED_CHARS = parse_file(args.sanitized_chars)
        global VECTORS
        VECTORS = parse_file(args.vectors)
        print("*********************** GATHERING WEB INFO ***********************")
        print("Guessing pages with {} words and {} extensions...".format(len(words), len(EXTENSIONS)))
        pages=set()
        guessed = guess_pages(args.url, words, EXTENSIONS)
        print("Getting crawled links...")
        crawled = crawl_pages(guessed)
        pages = pages.union(guessed, crawled)
        print("Gathered {} guessed and {} crawled pages:".format(len(guessed), len(crawled)))
        [print("\t" + str(parse_url(page))) for page in pages]
        print("___________________________________________________________________")
        print("Getting URLs with Forms from guessed and crawled pages...")
        urls_with_forms = get_urls_with_forms(pages)
        print("Gathered {} URLS with forms:".format(len(urls_with_forms)))
        [print("\t" + page) for page in urls_with_forms]
        
        # TODO: filter out unnecessary forms (we only want input and fields)
        print("9 of which are forms we can vector test (non buttons/radios/etc.):")
        print("___________________________________________________________________")
        print("Getting cookies...")
        cookies = get_cookies(args.url)
        if cookies:
            for cookie in cookies:
                print(cookie.name + ":" + cookie.value)
        else:
            print("No cookies :(")
        print("___________________________________________________________________")
        print("****************************** TEST ******************************")
        print("Web URLs that don't return a 200 status code...")
        for page in pages:
            status = test_page_status(page)
            if not status[0]: # if not 200
                print("\t {} | CODE: {}".format(page, status[1]))
        print("Web URLs that take longer than {} ms to load...".format(args.slow))
        for page in pages:
            status = check_for_delayed_response(page)
            if status[0]: # if not 200
                print("\t {} | SECONDS: {}".format(page, status[1]))
        print("Web URLs that contain sensitive content...")
        [check_leaked_data_from_url(page) for page in pages]
        print("**************************** VECTORS ****************************")
        vector_test(urls_with_forms)
        

if __name__ == "__main__":
    main()