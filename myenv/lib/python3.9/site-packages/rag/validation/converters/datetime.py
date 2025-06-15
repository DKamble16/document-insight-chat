from datetime import datetime as dt, timezone
import dateutil.parser


# always returns an aware datetime in utc
def datetime(v, accept=None, reject=None):
    # is already a datetime object just ensure it has a timezone
    if isinstance(v, dt):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            v = v.replace(tzinfo=timezone.utc)
        return v
    # try integer unix timestamp
    try:
        return dt.fromtimestamp(v, tz=timezone.utc)
    except (TypeError, ValueError):
        pass
    # try string unix timestamp
    try:
        return dt.fromtimestamp(int(v), tz=timezone.utc)
    except (TypeError, ValueError):
        pass
    # try iso timestamp
    try:
        ts = dateutil.parser.isoparse(v)
        if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)
    except (TypeError, ValueError):
        reject('expected_valid_datetime_format')
