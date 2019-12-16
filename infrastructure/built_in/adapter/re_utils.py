import re

def regex_match(str,pattern):
    match = re.match(pattern=pattern,string=str)
    return match.string if match else None