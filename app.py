from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import pydeck as pdk

# ---------------------------------------------------------------
# Base directory: where app.py and all CSVs live
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

HEALTH_PATH = BASE_DIR / "HDPulse_data_export.csv"
EV_REG_PATH = BASE_DIR / "Electric_Vehicle_Registration_Data.csv"
CHARGE_PATH = BASE_DIR / "Electric_Vehicle_Charging_Stations.csv"
POP_PATH = BASE_DIR / "2016cityandcountyenergyprofiles.csv"

# ---------------------------------------------------------------
# City → county mapping for Connecticut
# ---------------------------------------------------------------
CT_CITY_TO_COUNTY = {
    # Fairfield
    "BETHEL": "Fairfield",
    "BRIDGEPORT": "Fairfield",
    "BROOKFIELD": "Fairfield",
    "DANBURY": "Fairfield",
    "DARIEN": "Fairfield",
    "EASTON": "Fairfield",
    "FAIRFIELD": "Fairfield",
    "GREENWICH": "Fairfield",
    "MONROE": "Fairfield",
    "NEW CANAAN": "Fairfield",
    "NEW FAIRFIELD": "Fairfield",
    "NEWTOWN": "Fairfield",
    "NORWALK": "Fairfield",
    "REDDING": "Fairfield",
    "RIDGEFIELD": "Fairfield",
    "SHELTON": "Fairfield",
    "SHERMAN": "Fairfield",
    "STAMFORD": "Fairfield",
    "STRATFORD": "Fairfield",
    "TRUMBULL": "Fairfield",
    "WESTON": "Fairfield",
    "WESTPORT": "Fairfield",
    "WILTON": "Fairfield",

    # Hartford (examples)
    "AVON": "Hartford",
    "BERLIN": "Hartford",
    "BLOOMFIELD": "Hartford",
    "BRISTOL": "Hartford",
    "BURLINGTON": "Hartford",
    "CANTON": "Hartford",
    "EAST GRANBY": "Hartford",
    "EAST HARTFORD": "Hartford",
    "EAST WINDSOR": "Hartford",
    "ENFIELD": "Hartford",
    "FARMINGTON": "Hartford",
    "GLASTONBURY": "Hartford",
    "GRANBY": "Hartford",
    "HARTFORD": "Hartford",
    "MANCHESTER": "Hartford",
    "MARLBOROUGH": "Hartford",
    "NEW BRITAIN": "Hartford",
    "NEWINGTON": "Hartford",
    "PLAINVILLE": "Hartford",
    "ROCKY HILL": "Hartford",
    "SIMSBURY": "Hartford",
    "SOUTH WINDSOR": "Hartford",
    "SOUTHINGTON": "Hartford",
    "SUFFIELD": "Hartford",
    "WEST HARTFORD": "Hartford",
    "WETHERSFIELD": "Hartford",
    "WINDSOR": "Hartford",
    "WINDSOR LOCKS": "Hartford",

    # New Haven (examples)
    "ANSONIA": "New Haven",
    "BEACON FALLS": "New Haven",
    "BETHANY": "New Haven",
    "BRANFORD": "New Haven",
    "CHESHIRE": "New Haven",
    "DERBY": "New Haven",
    "EAST HAVEN": "New Haven",
    "HAMDEN": "New Haven",
    "MERIDEN": "New Haven",
    "MIDDLEBURY": "New Haven",
    "MILFORD": "New Haven",
    "NAUGATUCK": "New Haven",
    "NEW HAVEN": "New Haven",
    "NORTH BRANFORD": "New Haven",
    "NORTH HAVEN": "New Haven",
    "ORANGE": "New Haven",
    "OXFORD": "New Haven",
    "PROSPECT": "New Haven",
    "SEYMOUR": "New Haven",
    "SHELTON": "New Haven",
    "WALLINGFORD": "New Haven",
    "WATERBURY": "New Haven",
    "WEST HAVEN": "New Haven",
    "WOLCOTT": "New Haven",

    # New London (examples)
    "COLCHESTER": "New London",
    "EAST LYME": "New London",
    "GROTON": "New London",
    "LEDYARD": "New London",
    "MONTVILLE": "New London",
    "NEW LONDON": "New London",
    "NORWICH": "New London",
    "OLD LYME": "New London",
    "OLD SAYBROOK": "Middlesex",
    "STONINGTON": "New London",
    "WATERFORD": "New London",
}

# ---------------------------------------------------------------
# Data loading & cleaning
# ---------------------------------------------------------------
@st.cache_data(show_spinner=True)
def load_and_clean_data():
    # ----- Health / income data -----
    health_raw = pd.read_csv(
        HEALTH_PATH,
        skiprows=4,
        engine="python",
    )
    health_raw.columns = health_raw.columns.str.strip()
    health = health_raw.rename(
        columns={
            "County": "county",
            "FIPS": "fips",
            "Value (Dollars)": "median_income",
            "Rank within US (of 3141 counties)": "us_rank",
        }
    )
    health["county"] = (
        health["county"]
        .astype(str)
        .str.replace(" County", "", regex=False)
        .str.strip()
    )
    health["median_income"] = pd.to_numeric(health["median_income"], errors="coerce")
    health["us_rank"] = pd.to_numeric(health["us_rank"], errors="coerce")

    # If state column exists, keep CT only
    if "State Abbreviation" in health_raw.columns:
        health["state"] = health_raw["State Abbreviation"].str.strip()
        health = health[health["state"] == "CT"]

    # ----- EV registration data -----
    ev_raw = pd.read_csv(EV_REG_PATH)
    ev = ev_raw.copy()
    ev.columns = (
        ev.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )

    # CT only if state column exists
    if "state" in ev.columns:
        ev = ev[ev["state"].astype(str).str.upper() == "CT"]

    # Clean text columns when present
    if "primary_customer_city" in ev.columns:
        ev["primary_customer_city"] = (
            ev["primary_customer_city"].astype(str).str.title().str.strip()
        )
    if "vehicle_make" in ev.columns:
        ev["vehicle_make"] = ev["vehicle_make"].astype(str).str.title().str.strip()
    if "vehicle_model" in ev.columns:
        ev["vehicle_model"] = ev["vehicle_model"].astype(str).str.title().str.strip()

    # Vehicle year
    if "model_year" in ev.columns:
        ev["vehicle_year"] = pd.to_numeric(ev["model_year"], errors="coerce")
    elif "vehicle_year" in ev.columns:
        ev["vehicle_year"] = pd.to_numeric(ev["vehicle_year"], errors="coerce")

    ev_clean = ev.copy()

    # Drop duplicates if a unique key exists
    if "vin" in ev_clean.columns:
        ev_clean = ev_clean.drop_duplicates(subset=["vin"])
    elif "id" in ev_clean.columns:
        ev_clean = ev_clean.drop_duplicates(subset=["id"])

    # EV category from fuel code
    if "fuel_code" in ev_clean.columns:
        ev_clean["ev_category"] = ev_clean["fuel_code"].replace(
            {"E00": "BEV", "H04": "PHEV"}
        ).fillna("Other")
    else:
        ev_clean["ev_category"] = "Unknown"

    ev_clean["ev_count"] = 1

    # ----- Charging station data -----
    ch_raw = pd.read_csv(CHARGE_PATH)
    ch = ch_raw.copy()
    ch.columns = (
        ch.columns.str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )

    if "city" in ch.columns:
        ch["city"] = ch["city"].astype(str).str.title().str.strip()

    # Charger counts
    for col in ["ev_level1_evse_num", "ev_level2_evse_num", "ev_dc_fast_count"]:
        if col in ch.columns:
            ch[col] = pd.to_numeric(ch[col], errors="coerce").fillna(0).astype(int)
        else:
            ch[col] = 0

    ch["total_chargers"] = (
        ch.get("ev_level1_evse_num", 0)
        + ch.get("ev_level2_evse_num", 0)
        + ch.get("ev_dc_fast_count", 0)
    )
    ch["has_dc_fast"] = (ch.get("ev_dc_fast_count", 0) > 0).astype(int)
    ch["has_level2"] = (ch.get("ev_level2_evse_num", 0) > 0).astype(int)
    ch["has_level1"] = (ch.get("ev_level1_evse_num", 0) > 0).astype(int)

    # Location columns
    if {"longitude", "latitude"}.issubset(ch.columns):
        ch["lon"] = ch["longitude"]
        ch["lat"] = ch["latitude"]
    elif {"lng", "lat"}.issubset(ch.columns):
        # already fine
        pass

    # ----- Map city → county -----
    ev_reg = ev_clean.copy()

    if "primary_customer_city" in ev_reg.columns:
        ev_reg["city_clean"] = (
            ev_reg["primary_customer_city"].astype(str).str.upper().str.strip()
        )
    else:
        ev_reg["city_clean"] = ""

    ch["city_clean"] = ch.get("city", "").astype(str).str.upper().str.strip()

    ev_reg["county"] = ev_reg["city_clean"].map(CT_CITY_TO_COUNTY)
    ch["county"] = ch["city_clean"].map(CT_CITY_TO_COUNTY)

    # ----- County EV & charging summaries -----
    ev_count_by_county = (
        ev_reg.groupby("county")
        .size()
        .reset_index(name="ev_registrations")
        .sort_values("ev_registrations", ascending=False)
    )

    ch_summary_by_county = (
        ch.groupby("county")
        .agg(
            total_stations=("station_name", "count") if "station_name" in ch.columns else ("city", "count"),
            total_chargers=("total_chargers", "sum"),
            fast_chargers=("has_dc_fast", "sum"),
            level2_chargers=("has_level2", "sum"),
            level1_chargers=("has_level1", "sum"),
        )
        .reset_index()
    )

    county_full = (
        ev_count_by_county
        .merge(ch_summary_by_county, on="county", how="outer")
        .merge(health[["county", "median_income"]], on="county", how="left")
    )

    # EVs per charger
    county_full["evs_per_charger"] = (
        county_full["ev_registrations"]
        / county_full["total_chargers"].replace({0: np.nan})
    )

    # ----- Population from 2016 city/county energy profiles -----
    raw_pop = pd.read_csv(POP_PATH, header=None, low_memory=False)

    ct_rows = raw_pop[
        (raw_pop[1].astype(str).str.upper() == "CT")
        | (raw_pop[2].astype(str).str.contains(", CT", na=False))
    ].copy()

    # From inspection: col 4 = county name, col 8 = 2016 population
    ct_county = ct_rows[[4, 8]].copy()
    ct_county.columns = ["county_raw", "population_2016"]

    ct_county["county"] = (
        ct_county["county_raw"]
        .astype(str)
        .str.replace(" County", "", regex=False)
        .str.strip()
    )
    ct_county["population_2016"] = pd.to_numeric(
        ct_county["population_2016"], errors="coerce"
    )

    ct_county = ct_county[["county", "population_2016"]]

    # Merge population into county_full
    county_full = county_full.merge(ct_county, on="county", how="left")

    # Per-capita metrics
    county_full["evs_per_1k_people"] = (
        county_full["ev_registrations"]
        / (county_full["population_2016"] / 1000.0)
    )
    county_full["chargers_per_1k_people"] = (
        county_full["total_chargers"]
        / (county_full["population_2016"] / 1000.0)
    )

    return ev_clean, ch, health, county_full, ev_reg


# ---------------------------------------------------------------
# Load data
# ---------------------------------------------------------------
ev_clean, ch, health, county_full, ev_reg = load_and_clean_data()

# ---------------------------------------------------------------
# Streamlit page config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="CT EV Infrastructure & Energy Capacity Explorer",
    layout="wide",
    page_icon="🚗",
)

alt.data_transformers.disable_max_rows()

st.title("CT EV Infrastructure & Energy Capacity Explorer")

st.markdown(
    """
This app documents and explores the **cleaned datasets** used in our project:

> *How well does Connecticut’s EV charging infrastructure keep up with EV adoption
> and local socio-economic conditions (income, population)?*

Use the sidebar filters to focus on **specific counties**, **EV types**, and **vehicle years**.  
The KPIs and visuals will update to reflect your current view.
"""
)

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.header("Filters")

county_options = ["All CT"] + sorted(
    county_full["county"].dropna().unique().tolist()
)
selected_county = st.sidebar.selectbox("Focus on county", county_options, index=0)

ev_category_options = ["All EV types"] + sorted(
    ev_clean["ev_category"].dropna().unique().tolist()
)
selected_ev_cat = st.sidebar.selectbox("EV type", ev_category_options, index=0)

if "vehicle_year" in ev_clean.columns and ev_clean["vehicle_year"].notna().any():
    year_min, year_max = (
        int(ev_clean["vehicle_year"].min()),
        int(ev_clean["vehicle_year"].max()),
    )
else:
    year_min, year_max = (2000, 2025)

year_range = st.sidebar.slider(
    "Vehicle year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**How to use**\n"
    "- Start on *Overview* for KPIs\n"
    "- Use *County comparison* when writing results\n"
    "- Use *Maps & gaps* to discuss geography\n"
)

# ---------------------------------------------------------------
# Apply filters for EV and charging data
# ---------------------------------------------------------------
ev_filtered = ev_clean.copy()
if selected_ev_cat != "All EV types":
    ev_filtered = ev_filtered[ev_filtered["ev_category"] == selected_ev_cat]

if "vehicle_year" in ev_filtered.columns:
    ev_filtered = ev_filtered[
        (ev_filtered["vehicle_year"] >= year_range[0])
        & (ev_filtered["vehicle_year"] <= year_range[1])
    ]

if selected_county != "All CT":
    if "primary_customer_city" in ev_filtered.columns:
        ev_filtered["city_clean"] = (
            ev_filtered["primary_customer_city"].astype(str).str.upper().str.strip()
        )
        ev_filtered["county"] = ev_filtered["city_clean"].map(CT_CITY_TO_COUNTY)
        ev_filtered = ev_filtered[ev_filtered["county"] == selected_county]

    ch_filtered = ch[ch["county"] == selected_county]
    county_filtered = county_full[county_full["county"] == selected_county]
else:
    ch_filtered = ch.copy()
    county_filtered = county_full.copy()

# ---------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------
tab_overview, tab_docs, tab_county, tab_maps = st.tabs(
    ["📊 Overview", "📚 Data documentation", "🏛️ County comparison", "🗺️ Maps & gaps"]
)

# ---------------------------------------------------------------
# TAB 1 – OVERVIEW
# ---------------------------------------------------------------
with tab_overview:
    st.subheader("Big picture")

    # KPIs based on filtered data
    total_ev_records = len(ev_filtered)
    total_charging_stations = len(ch_filtered)
    counties_in_view = county_filtered["county"].nunique()

    total_public_chargers = None
    if "total_chargers" in ch_filtered.columns:
        total_public_chargers = int(ch_filtered["total_chargers"].sum())

    evs_per_charger = None
    if total_public_chargers and total_public_chargers > 0:
        evs_per_charger = total_ev_records / total_public_chargers

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EV records (filtered)", f"{total_ev_records:,}")
    c2.metric("Charging stations (filtered)", f"{total_charging_stations:,}")
    c3.metric("Counties in view", int(counties_in_view))
    if total_public_chargers is not None:
        c4.metric("Total public chargers", f"{total_public_chargers:,}")
    else:
        c4.metric("Total public chargers", "N/A")

    c5, c6 = st.columns(2)
    if evs_per_charger is not None:
        c5.metric("EVs per public charger", f"{evs_per_charger:,.1f}")
    else:
        c5.metric("EVs per public charger", "No chargers in view")

    share_of_state = (
        total_ev_records / len(ev_clean) * 100 if len(ev_clean) > 0 else 0
    )
    c6.metric("Share of CT EV records in view", f"{share_of_state:,.1f}%")

    st.markdown(
        """
**How this ties to our proposal**

- Each row in the EV table represents **one registered EV in CT**.  
- Each row in the charging table represents **one public station**.  
- The county table aggregates EVs, chargers, income, and population so we can
  identify **where EV adoption is outpacing infrastructure**, especially in
  higher-population counties.
"""
    )

    st.markdown("#### Sample of filtered EV registrations")
    st.dataframe(ev_filtered.head(50), use_container_width=True)

# ---------------------------------------------------------------
# TAB 2 – DATA DOCUMENTATION
# ---------------------------------------------------------------
with tab_docs:
    st.subheader("What we cleaned and how")

    with st.expander("EV registrations (Electric_Vehicle_Registration_Data.csv)", True):
        st.markdown(
            """
- Standardized column names and parsed year fields.  
- Restricted to **CT registrations only** and removed duplicate IDs.  
- Cleaned city names, vehicle make, and model text.  
- Created:
    - `ev_category` from `fuel_code` (BEV / PHEV / Other)  
    - `ev_count = 1` so each row counts as one vehicle.  
- Parsed `vehicle_year` from model year.
"""
        )
        st.dataframe(ev_clean.head(25), use_container_width=True)

    with st.expander("Charging stations (Electric_Vehicle_Charging_Stations.csv)", True):
        st.markdown(
            """
- Standardized column names and cleaned city names.  
- Converted Level 1, Level 2, and DC fast columns to integers.  
- Created:
    - `total_chargers`
    - Boolean flags `has_dc_fast`, `has_level2`, `has_level1`  
- Added latitude/longitude for mapping.
"""
        )
        st.dataframe(
            ch.head(25)[
                [
                    col
                    for col in [
                        "station_name",
                        "city",
                        "county",
                        "total_chargers",
                        "ev_dc_fast_count",
                        "ev_level2_evse_num",
                        "ev_level1_evse_num",
                        "lat",
                        "lon",
                    ]
                    if col in ch.columns
                ]
            ],
            use_container_width=True,
        )

    with st.expander("County summary (joined table)", True):
        st.markdown(
            """
This table is built by:

1. Aggregating EV registrations by county → `ev_registrations`  
2. Aggregating charging infrastructure by county → `total_stations`, `total_chargers`, etc.  
3. Joining with county-level `median_income` from HDPulse.  
4. Joining with `population_2016` from the DOE city & county energy profiles.  
5. Computing:
    - `evs_per_charger`  
    - `evs_per_1k_people`  
    - `chargers_per_1k_people`
"""
        )
        st.dataframe(county_full.head(25), use_container_width=True)

# ---------------------------------------------------------------
# TAB 3 – COUNTY COMPARISON
# ---------------------------------------------------------------
with tab_county:
    st.subheader("EV adoption vs charging capacity across counties")

    st.markdown(
        """
Use these charts when writing about **which counties are better served vs underserved**.
"""
    )

    # Bar: EV registrations by county
    st.markdown("##### EV registrations by county")
    ev_bar = (
        alt.Chart(county_full.dropna(subset=["ev_registrations"]))
        .mark_bar()
        .encode(
            x=alt.X("ev_registrations:Q", title="EV registrations"),
            y=alt.Y("county:N", sort="-x", title="County"),
            tooltip=["county", "ev_registrations"],
        )
    )
    st.altair_chart(ev_bar, use_container_width=True)

    # Bar: chargers by county
    st.markdown("##### Total public chargers by county")
    ch_bar = (
        alt.Chart(county_full.dropna(subset=["total_chargers"]))
        .mark_bar()
        .encode(
            x=alt.X("total_chargers:Q", title="Total public chargers"),
            y=alt.Y("county:N", sort="-x", title="County"),
            tooltip=["county", "total_chargers"],
        )
    )
    st.altair_chart(ch_bar, use_container_width=True)

    # Scatter: EVs vs chargers (robust to missing income)
    st.markdown("##### EV registrations vs total public chargers")

    # Check whether we actually have any median_income data
    has_income = county_full["median_income"].notna().any()

    if has_income:
        scatter_data = county_full.dropna(
            subset=["ev_registrations", "total_chargers", "median_income"]
        )
        color_enc = alt.Color(
            "median_income:Q",
            title="Median income (HDPulse)",
        )
    else:
        # No income data → still show the relationship, just color by county
        scatter_data = county_full.dropna(
            subset=["ev_registrations", "total_chargers"]
        )
        color_enc = alt.Color("county:N", legend=None)

    scatter = (
        alt.Chart(scatter_data)
        .mark_circle(size=150)
        .encode(
            x=alt.X("ev_registrations:Q", title="EV registrations"),
            y=alt.Y("total_chargers:Q", title="Total public chargers"),
            color=color_enc,
            tooltip=[
                "county:N",
                "ev_registrations:Q",
                "total_chargers:Q",
                "median_income:Q",
            ],
        )
        .interactive()
    )
    st.altair_chart(scatter, use_container_width=True)

    # Gap table
    st.markdown("##### EVs per charger by county (gap view)")

    gap_cols = [
        "county",
        "ev_registrations",
        "total_chargers",
        "evs_per_charger",
        "evs_per_1k_people",
        "chargers_per_1k_people",
    ]
    gap_df = (
        county_full.dropna(subset=["evs_per_charger"])
        .loc[:, [c for c in gap_cols if c in county_full.columns]]
        .sort_values("evs_per_charger", ascending=False)
    )

    st.markdown(
        "Counties at the top of this table have **more EVs per public charger**, "
        "which can signal potential infrastructure gaps."
    )
    st.dataframe(gap_df.head(15), use_container_width=True)

# ---------------------------------------------------------------
# TAB 4 – MAPS & GAPS
# ---------------------------------------------------------------
with tab_maps:
    st.subheader("Spatial distribution of public chargers")

    st.markdown(
        """
Each point is a station; bubble size reflects **total chargers**, and color reflects
**DC fast availability**. Use this to highlight **geographic gaps** in your narrative.
"""
    )

    # slider to hide very small sites
    min_chargers = st.slider(
        "Minimum total chargers per station to display", 1, 20, value=1
    )

    # Work on a copy of the filtered charging data
    ch_map = ch_filtered.copy()

    # Ensure we have lat/lon columns
    if "lat" not in ch_map.columns or "lon" not in ch_map.columns:
        # Try to infer from other columns
        if "latitude" in ch_map.columns and "longitude" in ch_map.columns:
            ch_map["lat"] = pd.to_numeric(ch_map["latitude"], errors="coerce")
            ch_map["lon"] = pd.to_numeric(ch_map["longitude"], errors="coerce")
        elif "new_georeferenced_column" in ch_map.columns:
            # Example of parsing a WKT-like POINT column if present
            coords = ch_map["new_georeferenced_column"].astype(str).str.extract(
                r"POINT\s*\(([-\d\.]+)\s+([-\d\.]+)\)"
            )
            ch_map["lon"] = pd.to_numeric(coords[0], errors="coerce")
            ch_map["lat"] = pd.to_numeric(coords[1], errors="coerce")

    # Keep only rows with valid coordinates and above the charger threshold
    ch_map = ch_map.dropna(subset=["lat", "lon"]).copy()
    ch_map = ch_map[ch_map["total_chargers"] >= min_chargers]

    if ch_map.empty:
        st.warning("No stations meet the filter criteria or have valid coordinates.")
    else:
        avg_lat = ch_map["lat"].mean()
        avg_lon = ch_map["lon"].mean()

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=ch_map,
            get_position="[lon, lat]",  
            get_radius="total_chargers * 400",
            get_fill_color="[has_dc_fast * 255, has_level2 * 180, 120, 180]",
            pickable=True,
        )

        view_state = pdk.ViewState(
            longitude=avg_lon,
            latitude=avg_lat,
            zoom=7,
            pitch=35,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "{station_name}\n{city}, {county}\n"
                        "Total chargers: {total_chargers}\n"
                        "DC fast: {ev_dc_fast_count}"
            },
        )

        st.pydeck_chart(deck)

        with st.expander("Stations shown on the map"):
            st.dataframe(
                ch_map[
                    [
                        "station_name",
                        "city",
                        "county",
                        "total_chargers",
                        "ev_dc_fast_count",
                        "ev_level2_evse_num",
                        "ev_level1_evse_num",
                        "lat",
                        "lon",
                    ]
                ],
                use_container_width=True,
            )
