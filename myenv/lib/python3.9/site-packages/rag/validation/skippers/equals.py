from ..utils import Undefined

def equals(*args):
    def validator(v, accept, reject=None):
        if v in args: accept(Undefined)
        return
    return validator
equals.dynamic = True
