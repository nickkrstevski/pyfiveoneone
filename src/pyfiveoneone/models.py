# your_module/models.py
from dataclasses import dataclass


@dataclass
class Route:
    route_id: int
    agency_id: str
    route_short_name: str
    route_long_name: str
    route_desc: str
    route_type: str
    route_url: str
    route_color: str
    route_text_color: str


@dataclass
class Stop:
    stop_id: int
    stop_code: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    zone_id: str
    stop_desc: str
    stop_url: str
    location_type: str
    parent_station: str
    stop_timezone: str
    wheelchair_boarding: str
    platform_code: str


@dataclass
class StopTime:
    # trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled,timepoint
    trip_id: int
    arrival_time: str
    departure_time: str
    stop_id: int
    stop_sequence: int
    stop_headsign: str
    pickup_type: str
    drop_off_type: str
    shape_dist_traveled: float
    timepoint: str


@dataclass
class Trip:
    route_id: int
    service_id: int
    trip_id: int
    trip_headsign: str
    direction_id: int
    block_id: int
    shape_id: int
    trip_short_name: str
    bikes_allowed: str
    wheelchair_accessible: str


@dataclass
class CalendarAttribute:
    service_id: int
    service_description: str


@dataclass
class Calendar:
    service_id: int
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int
    start_date: int
    end_date: int


@dataclass
class Direction:
    route_id: int
    direction_id: int
    direction_name: str


@dataclass
class Operator:
    id: str
    name: str
    short_name: str
    siri_operator_ref: str
    time_zone: str
    default_language: str
    contact_telephone_number: str
    web_site: str
    primary_mode: str
    private_code: str
    monitored: bool
    other_modes: str
