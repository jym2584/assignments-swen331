import argparse, textwrap
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
    parser.add_argument('url', type=str, help="hostname")
    parser.add_argument('--custom-auth', '--ca', type=str, help="{discover,test} Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa).")
    parser.add_argument('--common-words', '--cw', type=str, help="{discover,test} Newline-delimited file of common words to be used in page guessing. REQUIRED.")
    parser.add_argument('--extensions', '--ext', type=str, help="{discover,test} Newline-delimited file of path extensions, e.g. \".php\". OPTIONAL. (Defaults to \".php\" and the empty string if not specified)")
    parser.add_argument('--vectors', '--vec', type=str, help="{test} Newline-delimited file of common exploits to vulnerabilities. REQUIRED.")
    parser.add_argument('--sanitized-chars', '--san', type=str, help="{test} Newline-delimited file of characters that should be sanitized from inputs (Defaults to just < and >)")
    parser.add_argument('--sensitive', '--sen', type=str, help="{test} Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. REQUIRED.")
    parser.add_argument('--slow', type=int, default=500, help="{test} Number of milliseconds considered when a response is considered \"slow\". OPTIONAL. (Default is 500 milliseconds)")
    return parser