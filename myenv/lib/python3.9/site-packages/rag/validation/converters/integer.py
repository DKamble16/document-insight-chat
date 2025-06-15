def integer(v, accept=None, reject=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        reject('expected_valid_integer_format')
