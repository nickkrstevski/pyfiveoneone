# your_module/client.py
import requests
import os
from pathlib import Path
from typing import Optional, Union

from .utils import parse_gtfs_realtime_bytes_to_dict


class Client:
    def __init__(self, api_key=None, base_url="http://api.511.org/"):
        self.base_url = base_url
        if api_key is None:
            api_key = str(os.getenv("FIVEONEONE_API_KEY"))
        self.api_key = api_key

    def _request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.get(url, params=params or {}, headers=headers)
        resp.encoding = "utf-8-sig"
        resp.raise_for_status()
        return resp.json()

    def _request_bytes(self, endpoint, params=None) -> bytes:
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.get(url, params=params or {}, headers=headers)
        resp.raise_for_status()
        return resp.content

    def _download(
        self,
        endpoint: str,
        dest_path: Optional[Union[str, Path]] = None,
        chunk_size: int = 8192,
    ) -> Path:
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        with requests.get(url, headers=headers, stream=True) as resp:
            resp.raise_for_status()

            # Determine output path
            suggested_name = (
                self._filename_from_content_disposition(
                    resp.headers.get("Content-Disposition")
                )
                or "download"
            )
            if dest_path is None:
                out_path = Path.cwd() / suggested_name
            else:
                dest_path = Path(dest_path)
                if dest_path.exists() and dest_path.is_dir():
                    out_path = dest_path / suggested_name
                elif dest_path.suffix == "":
                    # If suffix is empty and directory doesn't exist, treat as directory
                    out_path = dest_path / suggested_name
                else:
                    out_path = dest_path

            out_path.parent.mkdir(parents=True, exist_ok=True)

            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)

        return out_path

    def _filename_from_content_disposition(
        self, content_disposition: Optional[str]
    ) -> Optional[str]:
        if not content_disposition:
            return None
        # Typical formats: attachment; filename="file.zip" or attachment; filename=file.zip
        try:
            parts = [p.strip() for p in content_disposition.split(";")]
            for part in parts:
                if part.lower().startswith("filename="):
                    value = part.split("=", 1)[1].strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    return value
        except Exception:
            return None
        return None

    ### JSON APIs ###
    def gtfs_operators(self):
        """
        GTFS Operators provides the list of transit operators/agencies
        that have a GTFS dataset available for download. It provides the
        operator’s ID, name, and the date the operator’s feed was last updated.
        """
        endpoint = f"transit/gtfsoperators?api_key={self.api_key}"
        return self._request(endpoint)

    def gtfs_feed_list(self, operator_id: str):
        endpoint = f"transit/datafeeds?api_key={self.api_key}&operator_id={operator_id}"
        return self._request(endpoint)

    def scheduled_departures_at_stop(self, operator_id: str, stop_id: int):
        endpoint = f"transit/stoptimetable?api_key={self.api_key}&operatorref={operator_id}&monitoringref={stop_id}&format=json"
        return self._request(endpoint)

    ### ZIP APIs ###
    def gtfs_feed_download(
        self,
        operator_id: str,
        dest_path: Optional[Union[str, Path]],
        MM: Optional[str] = None,
        YYYY: Optional[str] = None,
    ) -> Path:
        """
        Download the GTFS feed ZIP for the given operator and save it to disk.

        If dest_path is a directory or None, the filename from the server's
        Content-Disposition header (when present) will be used inside that
        directory. If dest_path is a file path, it will be used as-is.

        Returns the absolute Path to the saved file.
        """
        if dest_path and not str(dest_path).lower().endswith(".zip"):
            dest_path = str(dest_path) + ".zip"
        endpoint = f"transit/datafeeds?api_key={self.api_key}&operator_id={operator_id}"
        if MM and YYYY:
            endpoint += f"&historic={YYYY}-{MM}"
        return self._download(endpoint, dest_path)

    def get_operators(self):
        endpoint = f"transit/operators?api_key={self.api_key}&format=json"
        return self._request(endpoint)

    def real_time_stop_monitoring(self, agency: str, stopcode=None):
        endpoint = (
            f"transit/StopMonitoring?api_key={self.api_key}&agency={agency}&format=json"
        )
        if stopcode:
            endpoint += f"&stopcode={stopcode}"
        return self._request(endpoint)

    ### Protocol Buffer APIs ###
    def gfts_rt_trip_updates(self, agency: str):
        endpoint = f"transit/tripupdates?api_key={self.api_key}&agency={agency}"
        data = self._request_bytes(endpoint)
        return parse_gtfs_realtime_bytes_to_dict(data)

    def gtfs_rt_vehicle_positions(self, agency: str):
        endpoint = f"transit/vehiclepositions?api_key={self.api_key}&agency={agency}"
        data = self._request_bytes(endpoint)
        return parse_gtfs_realtime_bytes_to_dict(data)

    def gtfs_rt_service_alerts(self, agency: str):
        endpoint = f"transit/servicealerts?api_key={self.api_key}&agency={agency}"
        data = self._request_bytes(endpoint)
        return parse_gtfs_realtime_bytes_to_dict(data)
