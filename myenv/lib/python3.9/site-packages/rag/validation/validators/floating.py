def floating(v, accept=None, reject=None):
    if not isinstance(v, float): reject('expected_float')
