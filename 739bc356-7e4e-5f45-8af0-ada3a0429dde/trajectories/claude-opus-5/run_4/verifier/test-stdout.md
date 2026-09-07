============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
rootdir: /home/cli-migration-test-3
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 8 items

tests/test_currency.py::test_get_rates PASSED                            [ 12%]
tests/test_currency.py::test_convert PASSED                              [ 25%]
tests/test_geo.py::test_geocode PASSED                                   [ 37%]
tests/test_geo.py::test_reverse_geocode PASSED                           [ 50%]
tests/test_news.py::test_get_top_stories PASSED                          [ 62%]
tests/test_news.py::test_get_story PASSED                                [ 75%]
tests/test_weather.py::test_get_weather PASSED                           [ 87%]
tests/test_weather.py::test_get_temperature PASSED                       [100%]

==================================== PASSES ====================================
=========================== short test summary info ============================
PASSED tests/test_currency.py::test_get_rates
PASSED tests/test_currency.py::test_convert
PASSED tests/test_geo.py::test_geocode
PASSED tests/test_geo.py::test_reverse_geocode
PASSED tests/test_news.py::test_get_top_stories
PASSED tests/test_news.py::test_get_story
PASSED tests/test_weather.py::test_get_weather
PASSED tests/test_weather.py::test_get_temperature
============================== 8 passed in 0.09s ===============================
