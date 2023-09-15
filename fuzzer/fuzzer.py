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
    contents=set()
    try:
        with open(filename) as file:
            for line in file:
                contents.add(line.strip())
        return contents
    except:
        raise Exception("{} cannot be parsed.".format(filename))

def check_page_status(web_url):
    response = browser.open(web_url)
    return response.status_code == 200

def get_pages_from_url(web_url):
    """ Retreives web pages <a> tags from url 
    """
    routes = set()

    if not re.findall("(\..*)$", web_url): # add a slash if there is no extension at the end of the website
        web_url = web_url + "/"
    print("URLs for {}".format(web_url))
    browser.open(web_url)

    for tag in browser.page.select('a'):
        link = tag.get('href')
        if re.findall("(http://|https://|www.)", link): # skip external links
            continue
        try:
            if link in {".", "/"} or link.startswith("?C="): # this is mostly for built-in pages that has folders in them
                continue
            full_link = "{}/{}".format(web_url, link)
            if check_page_status(full_link):
                full_link = "{}{}".format(re.findall("^(.*[\\\/])[^\\\/]*$", web_url)[0], link) # parse out link
                print("\t" + full_link)
                routes.add(full_link)
        except: # requests.exceptions is thrown so avoid looking 
            pass
    return routes

def guess_pages(web_url, words, extensions):
    guessed_pages=set()
    print("************************************Guessed web pages************************************")
    for word in words:
        for ext in extensions:
            guessed_url = "{}/{}{}".format(web_url, word, ext)
            if check_page_status(guessed_url):
                print(guessed_url)
                guessed_pages.add(guessed_url)
    return guessed_pages

def crawl_pages(guessed_pages):
    print("************************************Crawled web pages************************************")
    for page in guessed_pages:
        get_pages_from_url(page)

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
        guessed_pages = guess_pages(args.url, words, EXTENSIONS)
        crawl_pages(guessed_pages)


if __name__ == "__main__":
    main()