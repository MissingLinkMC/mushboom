def get_reset_reason(reason: int) -> str:
  reasons = {
    1:  "Vbat power on reset",
    3:  "Software reset digital core",
    4:  "Legacy watch dog reset digital core",
    5:  "Deep Sleep reset digital core",
    6:  "Reset by SLC module, reset digital core",
    7:  "Timer Group0 Watch dog reset digital core",
    8:  "Timer Group1 Watch dog reset digital core",
    9:  "RTC Watch dog Reset digital core",
    10: "Instrusion tested to reset CPU",
    11: "Time Group reset CPU",
    12: "Software reset CPU",
    13: "RTC Watch dog Reset CPU",
    14: "for APP CPU, reset by PRO CPU",
    15: "Reset when the vdd voltage is not stable",
    16: "RTC Watch dog reset digital core and rtc module",
  }
  return reasons.get(reason, "NO_MEAN")