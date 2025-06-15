from functools import wraps
from rag import abort
from .validators.defined import defined
from .acceptors.undefined import undefined
from .utils import *


# class to build validation rules
class Validator():

    def __init__(self, chain):
        self.chain = chain

    def link(self, validator):
        return self.chain + [passthrough(validator)]

    @classmethod
    def attach(cls, validator):
        # if this takes no arguments attach it as property
        if hasattr(validator, 'dynamic'):
            def wrapped(self, *args, **kwargs):
                return Validator(self.link(validator(*args, **kwargs)))
        # otherwise attach as a function
        else:
            @property
            def wrapped(self):
                return Validator(self.link(validator))
        # attach validator to class
        setattr(cls, validator.__name__, wrapped)

    def execute(self, value):
        for validator in self.chain:
            value = validator(value, accept, reject)
        return value

    @property
    def to(self):
        return Converter(self.chain)

    @property
    def am(self):
        return Validator(self.chain)

    @property
    def accepts(self):
        return Acceptor(self.chain)

    @property
    def skips(self):
        return Skipper(self.chain)

# like validator class, but instead of rejecting values short circuits and accepts values
class Acceptor(Validator):

    def link(self, validator):
        return self.chain + [validator]

# like validator class, but instead of rejecting values short circuits and ignores values
class Skipper(Validator):

    def link(self, validator):
        return self.chain + [validator]

# like validator class, but is able to modify values
class Converter(Validator):

    def link(self, validator):
        return self.chain + [validator]

# root validator checks if things are even defined before validating or converting
class Root():

    @property
    def to(self):
        return Converter([passthrough(defined)])

    @property
    def am(self):
        return Validator([passthrough(defined)])

    @property
    def accepts(self):
        return Acceptor([passthrough(defined)])

    @property
    def skips(self):
        return Skipper([passthrough(defined)])

    @property
    def optional(self):
        return Validator([passthrough(undefined)])

# define entry point for building a validator
v = Root()

# attach all of the validators and converters to classes
attach(Validator, "validators", "rag.validation.validators")
attach(Converter, "converters", "rag.validation.converters")
attach(Acceptor, "acceptors", "rag.validation.acceptors")
attach(Skipper, "skippers", "rag.validation.skippers")

# check data against schema
def check_recursive(data, schema, errors, cleaned, path):
    current = dig(schema, path)
    if isinstance(current, dict):
        for key in current:
            check_recursive(data, schema, errors, cleaned, path + [key])
    else:
        try:
            value = dig(data, path)
        except KeyError:
            value = Undefined
        validator = dig(schema, path)
        try:
            value = validator.execute(value)
            place(cleaned, path, value)
        except ShortCircuit as acc:
            if acc.value != Undefined:
                place(cleaned, path, acc.value)
        except ValidationError as exc:
            place(errors, path, exc.code)

# check data against schema
def check(data, schema):
    errors = {}
    cleaned = {}
    check_recursive(data, schema, errors, cleaned, [])
    return errors, cleaned

# decorator that checks that a requests data is valid
def validate(schema, field='data'):
    def decorator(view_func):
        # make sure this function hasn't already been routed with route decorator or validation fails silently
        if hasattr(view_func, 'routed') and view_func.routed:
            raise RuntimeError(f'Ensure route decorator is the outermost decorator on function: {view_func.__name__}')

        # wrap view function with validation code
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            errors, data = check(getattr(request, field), schema)
            if errors: abort(400, errors)
            setattr(request, field, data)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
