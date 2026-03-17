import sys
import os
import types
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ujson is MicroPython-only — alias CPython's json for host-side tests
sys.modules['ujson'] = json

mock_logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['lib'] = types.ModuleType('lib')
sys.modules['lib.logger'] = types.SimpleNamespace(get_logger=lambda name: mock_logger)

# Minimal Microdot mock — just enough to capture registered routes
class MockResponse:
    def __init__(self, body, status_code=200, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {}

sys.modules['vendor'] = types.ModuleType('vendor')
mock_microdot = types.ModuleType('vendor.microdot')
mock_microdot.Response = MockResponse
sys.modules['vendor.microdot'] = mock_microdot

import importlib
api_debug = importlib.import_module('src.api_debug')


class MockRequest:
    def __init__(self, body_dict):
        self.json = body_dict


class MockApp:
    def __init__(self):
        self._put = {}
        self._delete = {}
    def put(self, path):
        def decorator(fn):
            self._put[path] = fn
            return fn
        return decorator
    def delete(self, path):
        def decorator(fn):
            self._delete[path] = fn
            return fn
        return decorator


import asyncio as stdlib_asyncio


class TestApiDebugValidation:
    def setup_method(self):
        self.app = MockApp()
        self.driver = type('Driver', (), {'values': {}})()
        api_debug.register_debug_routes(self.app, self.driver)
        self.put_handler = self.app._put["/api/debug/state"]
        self.delete_handler = self.app._delete["/api/debug/state"]

    def test_valid_keys_update_driver_values(self):
        req = MockRequest({"temperature": 25.0, "co2": 800})
        resp = stdlib_asyncio.run(self.put_handler(req))
        assert self.driver.values["temperature"] == 25.0
        assert self.driver.values["co2"] == 800

    def test_unknown_key_returns_400(self):
        req = MockRequest({"temperture": 25.0})  # typo
        resp = stdlib_asyncio.run(self.put_handler(req))
        assert resp.status_code == 400
        data = json.loads(resp.body)
        assert data["ok"] is False
        assert "temperture" in data["error"]

    def test_unknown_key_does_not_update_driver(self):
        self.driver.values.clear()
        req = MockRequest({"bad_key": 1.0})
        stdlib_asyncio.run(self.put_handler(req))
        assert self.driver.values == {}

    def test_empty_body_is_valid(self):
        req = MockRequest({})
        resp = stdlib_asyncio.run(self.put_handler(req))
        assert resp.status_code == 200

    def test_delete_clears_driver_values(self):
        self.driver.values["temperature"] = 25.0
        req = MockRequest(None)
        resp = stdlib_asyncio.run(self.delete_handler(req))
        assert self.driver.values == {}

    def test_delete_returns_ok(self):
        req = MockRequest(None)
        resp = stdlib_asyncio.run(self.delete_handler(req))
        data = json.loads(resp.body)
        assert data["ok"] is True

    def test_valid_keys_set_is_complete(self):
        expected = {
            "temperature", "co2", "relative_humidity",
            "temperature_1", "temperature_2", "temperature_3"
        }
        assert api_debug.VALID_KEYS == expected
