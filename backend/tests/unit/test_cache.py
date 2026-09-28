from app.core.cache import cache_key, clear_cache, get_cached, invalidate_prefix, set_cached


def setup_function():
    clear_cache()


def test_set_and_get_cached_value():
    key = cache_key("courses", 0, 20, None)
    set_cached(key, {"items": [], "total": 0})

    assert get_cached(key) == {"items": [], "total": 0}


def test_get_cached_miss_devuelve_none():
    assert get_cached(cache_key("courses", 1, 2, 3)) is None


def test_invalidate_prefix_borra_solo_las_claves_afectadas():
    set_cached(cache_key("courses", 0, 20, None), "cursos")
    set_cached(cache_key("students", 0, 20, None), "estudiantes")

    invalidate_prefix("courses")

    assert get_cached(cache_key("courses", 0, 20, None)) is None
    assert get_cached(cache_key("students", 0, 20, None)) == "estudiantes"
