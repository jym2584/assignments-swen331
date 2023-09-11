import mechanicalsoup
import requests
import re
from fuzzer_args import arg_parser
args = arg_parser().parse_args() # Namespace(type='discover', url='asdasdas', custom_auth=None, common_words=None, extensions=None, vectors=None, sanitized_chars=None, sensitive=None, slow=500)

# Error Handling
#if args.type == "discover" and (args.vectors or args.sanitized_chars or args.sensitive or args.slow): raise Exception("An option for {test} was used with {discover}. See py fuzzer.py -h for help.")

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

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
def parse_file(filename: str):
    contents=[]
    try:
        with open(filename) as file:
            for line in file:
                contents.append(line.strip())
        return contents
    except:
        raise Exception("{} cannot be parsed.".format(filename))
    
def parse_file_set(filename: str):
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
    routes = set()
    print("URLs for {}".format(web_url))
    browser.open(web_url)
    for tag in browser.page.select('a'):
        link = tag.get('href')
        try:
            if link in {".", "/"} or link.startswith("?C="):
                continue
            if check_page_status("{}/{}".format(web_url, link)):
                print("\t{}".format(link))
                routes.add(link)
        except: # requests.exceptions is thrown so avoid looking 
            pass
    return routes

def guess_pages(web_url, words):
    for word in words:
        print("Guessing {}/{}...".format(web_url, word))
        guess_pages_recursive("{}/{}".format(web_url, word))

def guess_pages_recursive(web_url):
    routes = get_pages_from_url(web_url)
    if len(routes) == 0: # dont guess any pages if there are no hits
        return
    if not re.findall(".*\/$", web_url): # dont guess current page if it doesn't lead to a directory
        return
    if not re.findall(".*\.\w+$", web_url): # dont guess current page if it is a file extension
        return
        
    for route in routes: 
        guess_pages_recursive("{}/{}".format(web_url, route))
        print(route)

def main():
    if args.custom_auth:
        print("******************Using custom authentication******************")
        custom_auth()
    
    if args.type == "discover":
        print("******************Discover******************")
        words = parse_file_set(args.common_words)
        guess_pages(args.url, words)


if __name__ == "__main__":
    main()