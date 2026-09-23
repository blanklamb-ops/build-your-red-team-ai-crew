from src.main import correlate as _correlate

DEFAULT_WINDOW_MINUTES = 30


def correlate(events, decisions, time_window: int = DEFAULT_WINDOW_MINUTES, asset_key: str = "asset"):
    """Correlate events↔decisions. `asset_key` retained for scaffold API compat."""
    _ = asset_key
    return _correlate(events, decisions, window_minutes=time_window)
