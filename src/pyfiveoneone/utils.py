# your_module/utils.py
from datetime import datetime, timezone
from typing import Any, Dict

from google.protobuf.json_format import MessageToDict


def parse_iso_timestamp(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _convert_epoch_timestamps_to_iso(obj: Any) -> Any:
    if isinstance(obj, dict):
        converted: Dict[str, Any] = {}
        for key, value in obj.items():
            if key in {"time", "timestamp"}:
                try:
                    ts_int = int(value)
                    converted[key] = datetime.fromtimestamp(
                        ts_int, tz=timezone.utc
                    ).isoformat()
                except Exception:
                    converted[key] = _convert_epoch_timestamps_to_iso(value)
            else:
                converted[key] = _convert_epoch_timestamps_to_iso(value)
        return converted
    if isinstance(obj, list):
        return [_convert_epoch_timestamps_to_iso(item) for item in obj]
    return obj


def parse_gtfs_realtime_bytes_to_dict(
    data: bytes, convert_timestamps: bool = True
) -> Dict[str, Any]:
    # Import dynamically to avoid static analysis issues
    _gtfs_rt = __import__(
        "google.transit.gtfs_realtime_pb2", fromlist=["gtfs_realtime_pb2"]
    )
    feed_cls = getattr(_gtfs_rt, "FeedMessage")
    feed = feed_cls()
    feed.ParseFromString(data)
    as_dict = MessageToDict(feed, preserving_proto_field_name=True)
    if convert_timestamps:
        return _convert_epoch_timestamps_to_iso(as_dict)
    return as_dict
