import logging
from functools import wraps
from typing import Any, Callable, List, Dict

from django.core.cache import cache

logger = logging.getLogger(__name__)

CATALOG_CACHE_TTL = 900
SEVERIDAD_CACHE_TTL = 3600
GEO_CACHE_TTL = 1800
UNIDAD_CACHE_TTL = 3600


def cached_catalog(key_prefix: str, ttl: int = CATALOG_CACHE_TTL):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{hash(str(args))}"
            if kwargs:
                cache_key += f":{hash(str(sorted(kwargs.items())))}"

            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached

            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


def memoize(func: Callable) -> Callable:
    _cache: Dict[Any, Any] = {}

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        hashable_args = tuple(
            tuple(a) if isinstance(a, list) else a for a in args
        )
        hashable_kwargs = tuple(
            (k, tuple(v) if isinstance(v, list) else v)
            for k, v in sorted(kwargs.items())
        )
        key = (hashable_args, hashable_kwargs)
        if key in _cache:
            return _cache[key]
        result = func(*args, **kwargs)
        _cache[key] = result
        return result

    wrapper.cache_clear = lambda: _cache.clear()
    wrapper.cache_info = lambda: {"size": len(_cache)}
    return wrapper


def get_or_set_cache(key: str, callable_fn: Callable, ttl: int = CATALOG_CACHE_TTL) -> Any:
    cached = cache.get(key)
    if cached is not None:
        return cached
    result = callable_fn()
    cache.set(key, result, ttl)
    return result


def invalidate_catalog_cache(key_prefix: str) -> None:
    pass