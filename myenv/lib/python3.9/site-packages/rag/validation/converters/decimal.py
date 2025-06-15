from decimal import Decimal

def decimal(v, accept=None, reject=None):
    try:
        return Decimal(v)
    except (TypeError, ValueError):
        reject('expected_valid_decimal_format')
