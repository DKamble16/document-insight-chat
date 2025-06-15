def floating(v, accept=None, reject=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        reject('expected_valid_float_format')
