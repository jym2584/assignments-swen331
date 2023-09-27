# Jin Moon Fuzzer SWEN-331
## Setup
- pip install -r requirements.txt
- Run {python, py, python3} fuzzer.py -h for help

## For DVWA Assignment
- [Setup and Run DVWA](https://www.se.rit.edu/~swen-331/activities/webapps/)

### HW 0
- Run `python fuzzer.py discover http://localhost:80 --custom-auth "dvwa"`

### HW 1
-  Run `py fuzzer.py discover http://localhost:80 --custom-auth="dvwa" --cw="files/common_words.txt" --ext="files/extensions.txt"`

Alternate tests:
- `py fuzzer.py discover http://localhost:80 --custom-auth="dvwa" --cw="files/common_words.txt"`
- `py fuzzer.py discover http://localhost:80/fuzzer-tests --cw="files/common_words.txt"`