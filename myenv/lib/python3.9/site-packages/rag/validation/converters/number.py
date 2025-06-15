def number(v, accept=None, reject=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return float(v)
        except (TypeError, ValueError):
            reject('expected_valid_numeric_format')
