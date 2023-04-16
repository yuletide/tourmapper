import requests
import json
import geojson
from mapbox import Geocoder
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
artist_id = 32875
start_date = "2023-07-17T14%3A00%3A00"
base_url = "https://www.bandsintown.com/a"
endpoint = "get-past-events"

events_data = []

geocoder = Geocoder(name="mapbox.places")
types = ("place", "poi")


def get_tours_by_date(artist_id, start_date):
    query = f"{base_url}/{artist_id}/{endpoint}?startDate={start_date}"
    # print("querying", query)
    resp = requests.get(query, headers=headers)
    resp_parsed = json.loads(resp.text)
    next_date = resp_parsed["nextStartingDate"]
    data = resp_parsed["events"]
    events_data.extend(data)
    if next_date:
        get_tours_by_date(artist_id, next_date)
    # print(data)


def geocode_event(event):
    query = f"{event['venue']}, {event['location']}"
    response = geocoder.forward(query, types=types)
    collection = response.json()
    # print(collection)
    if len(collection["features"]):
        feature = collection["features"][0]
        # print(feature)
        if "id" in feature:
            event["geo_place_id"] = feature["id"]
        event["geo_place_name"] = feature["place_name"]
        event["geo_place_type"] = feature["place_type"][0]
        event["geo_relevance"] = feature["relevance"]
        event["geo_center"] = str(feature["center"])
        event["geo_geom"] = feature["geometry"]
        event["geo_properties"] = json.dumps(feature["properties"])
        if "context" in feature:
            event["geo_context"] = json.dumps(feature["context"])
        return event
    else:
        print("no geocode results")
        return event


def process_events():
    output_events = []
    features = []
    for event in events_data:
        # print("processing event")
        # print(event)
        date_str = f"{event['year']} {event['month']} {event['day']}"
        date_parsed = datetime.strptime(date_str, "%Y %b %d")
        _event_obj = {
            "venue": event["venueName"],
            "location": event["location"],
            "eventUrl": event["eventUrl"],
            "date": str(date_parsed),
        }
        geocoded = geocode_event(_event_obj)
        feature = geojson.Feature(geometry=geocoded["geo_geom"], properties=geocoded)
        features.append(feature)
    print(geojson.dumps(features, sort_keys=True, default=str))


get_tours_by_date(artist_id, start_date)
process_events()
# print(json.dumps(events_data))
