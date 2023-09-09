import mechanicalsoup
from fuzzer_args import arg_parser
args = arg_parser().parse_args() # Namespace(type='discover', url='asdasdas', custom_auth=None, common_words=None, extensions=None, vectors=None, sanitized_chars=None, sensitive=None, slow=500)
print(args)
# Error Handling
#if args.type == "discover" and (args.vectors or args.sanitized_chars or args.sensitive or args.slow): raise Exception("An option for {test} was used with {discover}. See py fuzzer.py -h for help.")

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

def custom_auth():
    auth = args.custom_auth
    if auth == "dvwa":
        # setup
        browser.open("{}/setup.php".format(args.url))
        browser.select_form('form[action="#"]')
        browser.submit_selected()
        # login page
        browser.open(f"{args.url}")
        browser.select_form('form[action="login.php"]')
        browser["username"] = "admin" 
        browser["password"] = "password"
        browser.submit_selected()
        # security page
        browser.open(f"{args.url}/security.php")
        browser.select_form('form[action="#"]')['security'] = 'low' # security is a select element
        browser.submit_selected()
    else:
        print(f"There is no custom-auth logic for {auth}")

def main():
    if args.custom_auth:
        custom_auth()

if __name__ == "__main__":
    main()