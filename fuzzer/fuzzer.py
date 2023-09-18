import mechanicalsoup
import requests
import re
from fuzzer_args import arg_parser
args = arg_parser().parse_args() # Namespace(type='discover', url='asdasdas', custom_auth=None, common_words=None, extensions=None, vectors=None, sanitized_chars=None, sensitive=None, slow=500)

# Error Handling
#if args.type == "discover" and (args.vectors or args.sanitized_chars or args.sensitive or args.slow): raise Exception("An option for {test} was used with {discover}. See py fuzzer.py -h for help.")

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
EXTENSIONS=set()
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
            full_link = "{}/{}".format(web_url, link)
            if check_page_status(full_link):
                print(full_link)
                print(check_page_status(full_link))
                full_link = "{}{}".format(re.findall("^(.*[\\\/])[^\\\/]*$", web_url)[0], link) # parse out link
                routes.add(full_link)
        except: # requests.exceptions is thrown so avoid looking 
            pass
    return routes

def guess_pages(web_url, words, extensions):
    """
    Guess pages given a list of words and extensions
    """
    guessed_pages=set()
    print("Guessing {} words and {} extensions from {}...".format(len(words), len(extensions), web_url))
    for word in words:
        for ext in extensions:
            guessed_url = "{}/{}{}".format(web_url, word, ext)
            if check_page_status(guessed_url):
                guessed_pages.add(guessed_url)
    print("\n" + "Guessed pages:")
    for link in guessed_pages:
        print("\t" + link)
    return guessed_pages

def crawl_pages(guessed_pages):
    """
    Crawled web pages
    """
    crawled = set()
    for page in guessed_pages:
        print("Crawling " + page + " .....")
        routes = get_pages_from_url(page)
        crawled.update(routes)
    print("Crawled:")
    for link in crawled:
        print("\t" + link)
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

def get_urls_with_forms(valid_url):
    """ Returns a list of urls that has valid forms
    """
    urls_with_forms = set()
    for page in valid_url:
        fields = get_input_fields(page)
        if fields: # print forms if a form has been returned
            page_string = "************ {} ************".format(page)
            print(len(page_string) * "*")
            print(page_string)
            print(len(page_string) * "*")
            print(fields)
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
    list = []
    for group in re.match("^(.*?)(\?.*)?$", web_url).groups():
        if group is None:
            list.append("")
        else:
            list.append(group)
    return tuple(list)
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
        guessed_pages = guess_pages(args.url, words, EXTENSIONS)
        print("*************************************************************************************")
        print("************************************Crawled Pages************************************")
        print("*************************************************************************************")
        crawled = crawl_pages(guessed_pages)
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
        forms_guessed = get_urls_with_forms(guessed_pages)
        print("*******************************END Guessed pages END *******************************\n\n")
        print("*******************************Crawled pages*******************************")
        print()
        forms_crawled = get_urls_with_forms(crawled)
        print("*******************************END Crawled pages END *******************************\n\n")
        print("*****************************************************************************************")
        print("**************************************** Cookies ****************************************")
        print("*****************************************************************************************")
        cookies = get_cookies(args.url)
        for cookie in cookies:
            print(cookie.name + ":" + cookie.value)

if __name__ == "__main__":
    main()