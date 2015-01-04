class BaseError(Exception):
	pass

class DuplicateSymbolError(BaseError):
    def __init__(self,msg):
        self.msg = msg
        self.num = num


class LineFieldsError(BaseError):
    def __init__(self, msg):
        self.msg = msg
        self.num = num


class OpcodeLookupError(BaseError):
    def __init__(self,msg):
        self.msg = msg
        self.num = num


