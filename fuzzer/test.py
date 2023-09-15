import re
string = "https://asdasdsa"
string = "https://asdasdsa"
print(re.findall("^(.*[\\\/])[^\\\/]*$", string))