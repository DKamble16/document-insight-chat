from ..utils import Undefined

def empty(v, accept=None, reject=None):
    if len(v) == 0: accept(Undefined)
