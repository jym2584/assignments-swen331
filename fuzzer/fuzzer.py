import argparse, textwrap
import mechanicalsoup

def arg_parser():
    parser = argparse.ArgumentParser(description='Fuzzer is an exploratory testing tool used for finding weaknesses in a program by scanning its attack surfaces.', formatter_class=argparse.RawTextHelpFormatter)
    parser._positionals.title = 'POSITIONAL ARGUMENTS'
    parser._optionals.title = 'OPTIONS'
    parser.add_argument('type', choices=["discover", "test"], help=textwrap.dedent('''\
                                                                                discover - outputs a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.
                                                                                test - discovers all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.
                                                                                
                                                                                NOTE:
                                                                                The options below are available based on the respective choices indicated in brackets ({}).
                                                                                
                                                                                For example:
                                                                                    --common-words is available to `discover` and `test`
                                                                                    --vectors is only available to `test`
                                                                                
                                                                                '''))
    parser.add_argument('url', help="hostname")
    parser.add_argument('--custom-auth', '--ca', help="{discover,test} Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa).")
    parser.add_argument('--common-words', '--cw', help="{discover,test} Newline-delimited file of common words to be used in page guessing. REQUIRED.")
    parser.add_argument('--extensions', '--ext', help="{discover,test} Newline-delimited file of path extensions, e.g. \".php\". OPTIONAL. (Defaults to \".php\" and the empty string if not specified)")
    parser.add_argument('--vectors', '--vec', help="{test} Newline-delimited file of common exploits to vulnerabilities. REQUIRED.")
    parser.add_argument('--sanitized-chars', '--san', help="{test} Newline-delimited file of characters that should be sanitized from inputs (Defaults to just < and >)")
    parser.add_argument('--sensitive', '--sen', help="{test} Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. REQUIRED.")
    parser.add_argument('--slow', default=500, help="{test} Number of milliseconds considered when a response is considered \"slow\". OPTIONAL. (Default is 500 milliseconds)")
    return parser

args = arg_parser().parse_args() # Namespace(type='discover', url='asdasdas', custom_auth=None, common_words=None, extensions=None, vectors=None, sanitized_chars=None, sensitive=None, slow=500)
# Error Handling
#if args.type == "discover" and (args.vectors or args.sanitized_chars or args.sensitive or args.slow): raise Exception("An option for {test} was used with {discover}. See py fuzzer.py -h for help.")
browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

def custom_auth():
    auth = args.custom_auth
    if auth == "dvwa":
        # setup
        browser.open(f"{args.url}/setup.php")
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