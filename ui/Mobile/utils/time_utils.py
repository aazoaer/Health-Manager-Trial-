import datetime
from core.i18n import i18n_manager

_timezone_str = None

def get_timezone_str() -> str:
    global _timezone_str
    if _timezone_str is not None:
        return _timezone_str

    try:
        now_aware = datetime.datetime.now().astimezone()
        utc_offset = now_aware.utcoffset()
        
        if utc_offset is None:
            _timezone_str = "(UTC±00:00)"
            return _timezone_str

        total_seconds = utc_offset.total_seconds()
        sign = "+" if total_seconds >= 0 else "-"
        
        hours, remainder = divmod(abs(total_seconds), 3600)
        minutes, _ = divmod(remainder, 60)
        
        _timezone_str = f"(UTC{sign}{int(hours):02d}:{int(minutes):02d})"
        return _timezone_str
    except Exception:
        _timezone_str = "(UTC?)"
        return _timezone_str

def get_current_time_str() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_current_date_str() -> str:
    now = datetime.datetime.now()
    week_days = [
        i18n_manager.t("time_monday"), i18n_manager.t("time_tuesday"), i18n_manager.t("time_wednesday"),
        i18n_manager.t("time_thursday"), i18n_manager.t("time_friday"), i18n_manager.t("time_saturday"),
        i18n_manager.t("time_sunday")
    ]
    return now.strftime("%Y-%m-%d") + " " + week_days[now.weekday()]
