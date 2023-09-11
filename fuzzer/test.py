import re
string = "http://localhost:80/hi.php"
print(re.findall(".*\.\w+$", string))