"""Cache en memoria (TTL) para optimizar respuestas de lectura frecuente.

Nivel Avanzado pide "Cache de respuestas para optimizar rendimiento". Usamos
cachetools.TTLCache en memoria del proceso: es suficiente para una API con
un solo worker/instancia y evita la complejidad de levantar Redis solo para
el ejercicio. El diseno queda aislado en este modulo para poder sustituirlo
por un backend distribuido (Redis) sin tocar los routers.
"""

from typing import Any

from cachetools import TTLCache

from app.core.config import settings

_cache: TTLCache = TTLCache(maxsize=1024, ttl=settings.cache_ttl_seconds)


def cache_key(prefix: str, *args: Any) -> str:
    return prefix + ":" + ":".join(str(a) for a in args)


def get_cached(key: str) -> Any | None:
    return _cache.get(key)


def set_cached(key: str, value: Any) -> None:
    _cache[key] = value


def invalidate_prefix(prefix: str) -> None:
    """Elimina todas las entradas cuya clave empiece por `prefix`."""
    for key in [k for k in _cache.keys() if str(k).startswith(prefix)]:
        del _cache[key]


def clear_cache() -> None:
    _cache.clear()
