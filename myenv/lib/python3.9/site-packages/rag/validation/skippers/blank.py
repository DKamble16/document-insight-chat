from ..utils import Undefined

def blank(v, accept, reject=None):
    if v == '': accept(Undefined)
    return v
