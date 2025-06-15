from ..utils import Undefined

def any(collection):
    def validator(v, accept, reject=None):
        if v in collection: accept(Undefined)
        return
    return validator
any.dynamic = True
