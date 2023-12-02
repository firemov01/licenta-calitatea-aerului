import re
import json
import time

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def convert_json(d, convert):
    if isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            new_d[convert(k)] = convert_json(v, convert)
        return new_d
    elif isinstance(d, list):
        return [convert_json(x, convert) for x in d]
    else:
        return d


def convert_load(*args, **kwargs):
    json_obj = json.load(*args, **kwargs)
    return convert_json(json_obj, camel_to_underscore)


def convert_dump(*args, **kwargs):
    args = (convert_json(args[0], underscore_to_camel),) + args[1:]
    json.dump(*args, **kwargs)

def functiondelay(function):
    def wrapper(*args, **kwargs):
        time.sleep(2)
        return function(*args, **kwargs)
    wrapper.nodelay = function
    return wrapper
