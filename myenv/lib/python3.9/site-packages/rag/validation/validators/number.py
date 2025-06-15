def number(v, accept=None, reject=None):
    if not isinstance(v, int) and not isinstance(v, float):
        reject('expected_number')
