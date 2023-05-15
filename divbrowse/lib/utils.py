from simplejson import JSONEncoder

#from flask.json.provider import JSONProvider
import orjson

RED = '\033[31m'
RESET = '\033[0m'

def print_error(msg):
    print(f"{RED}ERROR: {msg}{RESET}")
    pass

class ApiError(Exception):
    status_code = 200
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message
        return rv


class StrictEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs["allow_nan"] = False
        kwargs["ignore_nan"] = True
        super().__init__(*args, **kwargs)

class ORJSONEncoder:

    def __init__(self, **kwargs):
        # eventually take into consideration when serializing
        self.options = kwargs

    def encode(self, obj):
        # decode back to str, as orjson returns bytes
        return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode('utf-8')