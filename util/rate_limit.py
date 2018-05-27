import time
from keyvaluestore.utils import get_value_or_default, set_key_value


def rate_limit(key, once_every):
    def _rate_limit_decorator(fn):
        def wrapper(*args, **kwargs):
            if shouldnt_rate_limit(key, once_every):
                return fn(*args, **kwargs)
            return None
        return wrapper
    return _rate_limit_decorator


def shouldnt_rate_limit(key, once_every):
    last_hit_key = 'rate_limit:last_hit:' + key

    last_hit = float(get_value_or_default(last_hit_key, 0))
    time_since_last_hit = time.time() - last_hit
    if time_since_last_hit < once_every:
        return False
    set_key_value(last_hit_key, time.time())
    return True

