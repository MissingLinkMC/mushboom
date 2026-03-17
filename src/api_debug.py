import ujson as json

from vendor.microdot import Response
from lib.logger import get_logger

logger = get_logger("api_debug")

VALID_KEYS = {
    "temperature", "co2", "relative_humidity",
    "temperature_1", "temperature_2", "temperature_3",
}


def register_debug_routes(app, sensor_driver):
    @app.put("/api/debug/state")
    async def set_debug_state(request):
        data = request.json or {}
        unknown = set(data.keys()) - VALID_KEYS
        if unknown:
            return Response(
                body=json.dumps({"ok": False, "error": f"Unknown keys: {sorted(unknown)}"}),
                status_code=400,
                headers={"Content-Type": "application/json"},
            )
        sensor_driver.values.update(data)
        return Response(
            body=json.dumps({"ok": True}),
            headers={"Content-Type": "application/json"},
        )

    @app.delete("/api/debug/state")
    async def clear_debug_state(request):
        sensor_driver.values.clear()
        return Response(
            body=json.dumps({"ok": True}),
            headers={"Content-Type": "application/json"},
        )
