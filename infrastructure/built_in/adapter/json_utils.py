from json import loads, dumps, dump

def make_json(dict):
    string = dumps(dict).encode("utf-8")
    return string

def write_json_to(file,dict):
    dump(dict,file)
    return None

def make_dict(json_string):
    try:
        return loads(json_string)
    except:
        return None