from json import loads, dumps, dump


def make_json(data):
    string = dumps(data).encode("utf-8")
    return string


def write_json_to(file, data):
    dump(data, file)


def make_dict(json_string):
    try:
        return loads(json_string)
    except:
        return None
