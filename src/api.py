import ujson as json

from vendor.microdot import Microdot, send_file, Response
from lib.template import render_template
from shared_state import state, config
from config import USE_FAHRENHEIT, THINGSPEAK_ENABLED, THINGSPEAK_CHANNEL_ID
from tasks.memory_monitor import memory_history

app = Microdot()


@app.get("/")
async def index(request):
    # Read index.html as template
    with open("static/index.html", "r") as f:
        template = f.read()

    remote_dashboard_link = (
        f'<a href="https://thingspeak.mathworks.com/channels/{THINGSPEAK_CHANNEL_ID}/private_show" target="_blank" rel="noopener noreferrer">Dashboard</a>'
        if THINGSPEAK_ENABLED else ""
    )
    html = render_template(template, {
        "USE_FAHRENHEIT": "true" if USE_FAHRENHEIT else "false",
        "REMOTE_DASHBOARD_LINK": remote_dashboard_link
    })
    return Response(body=html, headers={"Content-Type": "text/html"})



# Routes for serving static files
@app.get("/favicon.ico")
async def favicon(request):
    return send_file("/static/favicon.ico")


@app.get("/favicon-16x16.png")
async def favicon_small(request):
    return send_file("/static/favicon-16x16.png")


@app.get("/favicon-32x32.png")
async def favicon_large(request):
    return send_file("/static/favicon-32x32.png")


@app.get("/apple-touch-icon.png")
async def apple_touch_icon(request):
    return send_file("/static/apple-touch-icon.png")


@app.get("/android-chrome-192x192.png")
async def android_icon_small(request):
    return send_file("/static/android-chrome-192x192.png")


@app.get("/android-chrome-512x512.png")
async def android_icon_large(request):
    return send_file("/static/android-chrome-512x512.png")


@app.get("/site.webmanifest")
async def site_manifest(request):
    return send_file("/static/site.webmanifest")


@app.get("/style.css")
async def stylesheet(request):
    return send_file("/static/style.css", content_type="text/css")


@app.get("/logs.html")
async def logs_page(request):
    return send_file("/static/logs.html")


@app.get("/memory.html")
async def memory_page(request):
    return send_file("/static/memory.html")


@app.get("/api/metrics")
async def get_metrics(request):
    return Response(
        body=json.dumps(state.as_dict()),
        headers={"Content-Type": "application/json"},
        status_code=200,
    )


@app.get("/api/memory")
async def get_memory(request):
    """Return detailed memory usage information"""

    # Prepare response
    memory_info = {
        "current": {
            "percent": memory_history["current"]["percent"],
            "free": memory_history["current"]["free"],
            "used": memory_history["current"]["used"],
            "total": memory_history["current"]["total"],
            "time": memory_history["current"]["time"],
        },
        "history": {
            "startup": memory_history["startup"],
            "min": memory_history["min"],
            "max": memory_history["max"],
            "trend_increasing": memory_history["trend_increasing"],
        },
    }

    # Add last 5 measurements if available
    last_measurements = []
    history_len = len(memory_history["last_hour"])
    if history_len > 0:
        for i in range(min(5, history_len)):
            last_measurements.append(memory_history["last_hour"][history_len - 1 - i])
    memory_info["recent"] = {"measurements": last_measurements}

    return Response(
        body=json.dumps(memory_info),
        headers={"Content-Type": "application/json"},
        status_code=200,
    )


@app.get("/api/ranges")
async def get_ranges(request):
    # Return AppConfig fields using the frontend contract
    resp = {
        "co2": {"on": config.on_co2, "off": config.off_co2},
        "temp": {"on": config.on_temp, "off": config.off_temp},
        "rh": {"on": config.on_humidity, "off": config.off_humidity},
    }
    return Response(
        body=json.dumps(resp),
        headers={"Content-Type": "application/json"},
        status_code=200,
    )


@app.put("/api/ranges")
async def set_ranges(request):
    try:
        data = request.json
        # Accept 'on' and 'off' for each metric, map to AppConfig fields
        if "co2" in data:
            if "on" in data["co2"]:
                config.on_co2 = float(data["co2"]["on"])
            if "off" in data["co2"]:
                config.off_co2 = float(data["co2"]["off"])
        if "temp" in data:
            if "on" in data["temp"]:
                config.on_temp = float(data["temp"]["on"])
            if "off" in data["temp"]:
                config.off_temp = float(data["temp"]["off"])
        if "rh" in data:
            if "on" in data["rh"]:
                config.on_humidity = float(data["rh"]["on"])
            if "off" in data["rh"]:
                config.off_humidity = float(data["rh"]["off"])
        config.save()
        return Response(
            body=json.dumps({"ok": True}), headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return Response(
            body=json.dumps({"ok": False, "error": str(e)}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )


@app.get("/api/modes")
async def get_modes(request):
    resp = {
        "heater": config.heater_mode,
        "fan": config.fan_mode,
        "humidifier": config.humidifier_mode,
    }
    return Response(
        body=json.dumps(resp),
        headers={"Content-Type": "application/json"},
        status_code=200,
    )


@app.put("/api/modes")
async def set_modes(request):
    try:
        data = request.json
        valid_modes = ["auto", "on", "off"]

        if "heater" in data and data["heater"] in valid_modes:
            config.heater_mode = data["heater"]
        if "fan" in data and data["fan"] in valid_modes:
            config.fan_mode = data["fan"]
        if "humidifier" in data and data["humidifier"] in valid_modes:
            config.humidifier_mode = data["humidifier"]

        config.save()
        return Response(
            body=json.dumps({"ok": True}), headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return Response(
            body=json.dumps({"ok": False, "error": str(e)}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )


@app.get("/api/fan-schedule")
async def get_fan_schedule(request):
    resp = {
        "enabled": config.fan_schedule_enabled,
        "interval_minutes": config.fan_schedule_interval_minutes,
        "duration_minutes": config.fan_schedule_duration_minutes,
    }
    return Response(
        body=json.dumps(resp),
        headers={"Content-Type": "application/json"},
        status_code=200,
    )


@app.put("/api/fan-schedule")
async def set_fan_schedule(request):
    try:
        data = request.json or {}
        if "enabled" in data:
            config.fan_schedule_enabled = bool(data["enabled"])
        if "interval_minutes" in data:
            config.fan_schedule_interval_minutes = float(data["interval_minutes"])
        if "duration_minutes" in data:
            config.fan_schedule_duration_minutes = float(data["duration_minutes"])
        config.save()
        return Response(
            body=json.dumps({"ok": True}), headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return Response(
            body=json.dumps({"ok": False, "error": str(e)}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )


@app.get("/logs/error.log")
async def serve_error_log(request):
    # Use path relative to current directory
    return send_file("logs/error.log")


@app.get("/api/logs/app")
async def api_app_logs(request):
    """Serve application log content as text"""
    try:
        with open("logs/mushboom.log", "r") as f:
            content = f.read()
        return Response(body=content, headers={"Content-Type": "text/plain"})
    except Exception as e:
        return Response(
            body=f"Error reading log: {str(e)}",
            status_code=500,
            headers={"Content-Type": "text/plain"},
        )


@app.get("/api/logs/error")
async def api_error_logs(request):
    """Serve error log content as text"""
    try:
        with open("logs/error.log", "r") as f:
            content = f.read()
        return Response(body=content, headers={"Content-Type": "text/plain"})
    except Exception as e:
        return Response(
            body=f"Error reading log: {str(e)}",
            status_code=500,
            headers={"Content-Type": "text/plain"},
        )


@app.get("/ping")
async def ping(request):
    """Simple lightweight endpoint for health checks"""
    return "pong"
