import streamlit as st
import datetime
import pytz
from utils.predicthq import get_api_key, get_predicthq_client
from utils.code_examples import get_code_example


def show_sidebar_options():
    locations = [
        {
            "id": "indianapolis",
            "name": "101 W Maryland St, Indianapolis",
            "address": "101 W Maryland St, Indianapolis, IN 46225, United States",
            "lat": 39.76553,
            "lon": -86.16025,
            "tz": "America/Indiana/Indianapolis",
            "units": "imperial",
        },
        {
            "id": "cleveland",
            "name": "3294 Steelyard Dr, Cleveland",
            "address": "3294 Steelyard Dr, Cleveland, OH 44109, United States",
            "lat": 41.46439,
            "lon": -81.68835,
            "tz": "America/New_York",
            "units": "imperial",
        },
        {
            "id": "st-louis",
            "name": "1253 Hampton Ave, St. Louis",
            "address": "1253 Hampton Ave, St. Louis, MO 63139, United States",
            "lat": 38.62729,
            "lon": -90.28778,
            "tz": "America/Chicago",
            "units": "imperial",
        },
        {
            "id": "sheridan",
            "name": "3502 River Point Pkwy, Sheridan",
            "address": "3502 River Point Pkwy, Sheridan, CO 80110, United States",
            "lat": 39.65298,
            "lon": -105.01275,
            "tz": "America/Denver",
            "units": "imperial",
        },
        {
            "id": "overland-park",
            "name": "7510 W 63rd St, Overland Park",
            "address": "7510 W 63rd St, Overland Park, KS 66202, United States",
            "lat": 39.01534,
            "lon": -94.67292,
            "tz": "America/Chicago",
            "units": "imperial",
        },
    ]

    # Work out which location is currently selected
    index = 0

    if "location" in st.session_state:
        for idx, location in enumerate(locations):
            if st.session_state["location"]["id"] == location["id"]:
                index = idx
                break

    location = st.sidebar.selectbox(
        "Restaurant",
        locations,
        index=index,
        format_func=lambda x: x["name"],
        help="Select the restaurant location.",
        disabled=get_api_key() is None,
        key="location",
    )

    # Prepare the date range (today + 30d as the default)
    tz = pytz.timezone(location["tz"])
    today = datetime.datetime.now(tz).date()
    date_options = [
        {
            "id": "next_7_days",
            "name": "Next 7 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=7),
        },
        {
            "id": "next_30_days",
            "name": "Next 30 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=30),
        },
        {
            "id": "next_90_days",
            "name": "Next 90 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=90),
        },
    ]

    # Work out which date is currently selected
    index = 0

    if "daterange" in st.session_state:
        for idx, date_option in enumerate(date_options):
            if st.session_state["daterange"]["id"] == date_option["id"]:
                index = idx
                break

    st.sidebar.selectbox(
        "Date Range",
        date_options,
        index=index,
        format_func=lambda x: x["name"],
        help="Select the date range for fetching event data.",
        disabled=get_api_key() is None,
        key="daterange",
    )

    # Use an appropriate radius unit depending on location
    radius_unit = (
        "mi" if "units" in location and location["units"] == "imperial" else "km"
    )

    st.session_state.suggested_radius = fetch_suggested_radius(
        location["lat"], location["lon"], radius_unit=radius_unit
    )

    # Allow changing the radius if needed (default to suggested radius)
    # The Suggested Radius API is used to determine the best radius to use for the given location and industry
    st.sidebar.slider(
        f"Suggested Radius around restaurant ({radius_unit})",
        0.0,
        10.0,
        st.session_state.suggested_radius.get("radius", 2.0),
        0.1,
        help="[Suggested Radius Docs](https://docs.predicthq.com/resources/suggested-radius)",
        key="radius",
    )


@st.cache_data
def fetch_suggested_radius(lat, lon, radius_unit="mi", industry="restaurants"):
    phq = get_predicthq_client()
    suggested_radius = phq.radius.search(
        location__origin=f"{lat},{lon}", radius_unit=radius_unit, industry=industry
    )

    return suggested_radius.to_dict()


def show_map_sidebar_code_examples():
    st.sidebar.markdown("## Code examples")

    # The code examples are saved as markdown files in docs/code_examples
    examples = [
        {"name": "Suggested Radius API", "filename": "suggested_radius_api"},
        {
            "name": "Features API (Predicted Attendance aggregation)",
            "filename": "features_api",
        },
        {"name": "Count of Events", "filename": "count_api"},
        {"name": "Demand Surge API", "filename": "demand_surge_api"},
        {"name": "Search Events", "filename": "events_api"},
        {"name": "Python SDK for PredictHQ APIs", "filename": "python_sdk"},
    ]

    for example in examples:
        with st.sidebar.expander(example["name"]):
            st.markdown(get_code_example(example["filename"]))

    st.sidebar.caption(
        "Get the code for this app at [GitHub](https://github.com/predicthq/streamlit-restaurant-demo)"
    )
