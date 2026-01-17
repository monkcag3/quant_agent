
import json


class StructureMessage:
    def __init__(self, msg, /, **kwargs):
        self.msg = msg
        self.kwargs = kwargs

    def __str__(self):
        return "{} {}".format(self.msg, json.dumps(self.kwargs, default=str))