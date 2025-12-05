from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import pydeck as pdk
import re

# ---------------------------------------------------------------
# Base directory: where app.py and all CSVs live (OIM7502_F25)
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

HEALTH_PATH = BASE_DIR / "HDPulse_data_export.csv"
EV_REG_PATH = BASE_DIR / "Electric_Vehicle_Registration_Data.csv"
CHARGE_PATH = BASE_DIR / "Electric_Vehicle_Charging_Stations.csv"
POP_PATH = BASE_DIR / "2016cityandcountyenergyprofiles.csv"

# ---------------------------------------------------------------
# Streamlit config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="CT EV Infrastructure & Energy Capacity Explorer",
    layout="wide",
    page_icon="🚗",
)

alt.data_transformers.disable_max_rows()

st.title("🚗⚡ CT EV Infrastructure & Energy Capacity Explorer")

st.markdown(
    """
This app documents and explores the **cleaned datasets** used in our project:

> *How well does Connecticut’s EV charging infrastructure keep up with EV adoption
> and local socio-economic conditions (income, population)?*

Use the **sidebar** to filter by county, EV type, and model year, then navigate
the tabs to see:

1. **Overview** – key metrics and filtered EV sample.  
2. **Data documentation** – what we cleaned and how, with preview tables.  
3. **County comparison** – EV vs chargers vs income & population.  
4. **Maps & gaps** – spatial distribution of public charging stations.
"""
)

# ---------------------------------------------------------------
# City → County mapping
# ⚠️ IMPORTANT: extend this with the full mapping from your notebook
# ---------------------------------------------------------------
ct_city_to_county = {
    # Fairfield County (examples)
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

    # Hartford County (examples)
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
    "SUFFIELD": "Hartford",
    "WEST HARTFORD": "Hartford",
    "WETHERSFIELD": "Hartford",
    "WINDSOR": "Hartford",
    "WINDSOR LOCKS": "Hartford",

    # 👉 Add New Haven, New London, Litchfield, Middlesex, Tolland, Windham cities here
}


# ---------------------------------------------------------------
# Data loading & cleaning (mirrors notebook, uses BASE_DIR paths)
# ---------------------------------------------------------------
@st.cache_data
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
    health = health[health["county"] != "United States"].copy()

    health["median_income"] = (
        health["median_income"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    health["median_income"] = pd.to_numeric(
        health["median_income"], errors="coerce"
    )
    health = health.dropna(subset=["median_income"]).copy()
    health["median_income"] = health["median_income"].astype(int)

    health["us_rank"] = (
        health["us_rank"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
    )
    health["us_rank"] = pd.to_numeric(health["us_rank"], errors="coerce")
    health = health.dropna(subset=["us_rank"]).copy()
    health["us_rank"] = health["us_rank"].astype(int)

    health["county"] = (
        health["county"]
        .astype(str)
        .str.replace(" County", "", regex=False)
        .str.strip()
    )

    # ----- EV registration data -----
    ev_reg = pd.read_csv(EV_REG_PATH, low_memory=False)

    ev_clean = ev_reg.copy()
    ev_clean.columns = ev_clean.columns.str.lower().str.replace(" ", "_")

    # These column names align with the CT EV data structure
    ev_clean["registration_start_date"] = pd.to_datetime(
        ev_clean.get("registration_start_date"), errors="coerce"
    )
    ev_clean["registration_expiration_date"] = pd.to_datetime(
        ev_clean.get("registration_expiration_date"), errors="coerce"
    )
    if "vehicle_year" in ev_clean.columns:
        ev_clean["vehicle_year"] = pd.to_numeric(
            ev_clean["vehicle_year"], errors="coerce"
        )

    ev_clean["primary_customer_city"] = (
        ev_clean["primary_customer_city"].astype(str).str.strip().str.title()
    )
    ev_clean["vehicle_make"] = ev_clean["vehicle_make"].astype(str).str.title()
    ev_clean["vehicle_model"] = ev_clean["vehicle_model"].astype(str).str.title()
    ev_clean["vehicle_type"] = ev_clean["vehicle_type"].astype(str).str.upper()

    # CT only, unique vehicles
    if "primary_customer_state" in ev_clean.columns:
        ev_clean = ev_clean[ev_clean["primary_customer_state"] == "CT"]
    if "id" in ev_clean.columns:
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
        ch["city"] = ch["city"].astype(str).str.strip().str.title()

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

    # Connector flags
    if "ev_other_info" in ch.columns:
        ch["ev_other_info"] = (
            ch["ev_other_info"]
            .fillna("")
            .str.upper()
            .str.strip()
        )
        ch["is_tesla_connector"] = ch["ev_other_info"].str.contains("TESLA").astype(int)
        ch["is_conductive_120"] = ch["ev_other_info"].str.contains("120V").astype(int)
        ch["has_other_connector_info"] = (ch["ev_other_info"] != "NONE").astype(int)
    else:
        ch["is_tesla_connector"] = 0
        ch["is_conductive_120"] = 0
        ch["has_other_connector_info"] = 0

    # ----- Map city → county -----
    if "Primary Customer City" in ev_reg.columns:
        ev_reg["city_clean"] = (
            ev_reg["Primary Customer City"].astype(str).str.upper().str.strip()
        )
    else:
        ev_reg["city_clean"] = ""

    ch["city_clean"] = ch.get("city", "").astype(str).str.upper().str.strip()

    ev_reg["county"] = ev_reg["city_clean"].map(ct_city_to_county)
    ch["county"] = ch["city_clean"].map(ct_city_to_county)

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
            total_stations=("station_name", "count"),
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

    return ev_clean, ch, health, county_full


# ---------------------------------------------------------------
# Load data (with friendly error if files missing)
# ---------------------------------------------------------------
try:
    ev_clean, ch, health, county_full = load_and_clean_data()
except FileNotFoundError as e:
    st.error(
        "❌ One of the required CSV files was not found.\n\n"
        "Make sure the following files are in the SAME folder as `app.py` "
        "(your `OIM7502_F25` folder):\n\n"
        "- `HDPulse_data_export.csv`\n"
        "- `Electric_Vehicle_Registration_Data.csv`\n"
        "- `Electric_Vehicle_Charging_Stations.csv`\n"
        "- `2016cityandcountyenergyprofiles.csv`\n\n"
        f"Technical details: {e}"
    )
    st.stop()

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

# Apply filters for EV and charging data
ev_filtered = ev_clean.copy()
if selected_ev_cat != "All EV types":
    ev_filtered = ev_filtered[ev_filtered["ev_category"] == selected_ev_cat]

if "vehicle_year" in ev_filtered.columns:
    ev_filtered = ev_filtered[
        (ev_filtered["vehicle_year"] >= year_range[0])
        & (ev_filtered["vehicle_year"] <= year_range[1])
    ]

if selected_county != "All CT":
    ev_filtered["city_clean"] = (
        ev_filtered["primary_customer_city"].astype(str).str.upper().str.strip()
    )
    ev_filtered["county"] = ev_filtered["city_clean"].map(ct_city_to_county)
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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EV records (CT)", f"{len(ev_clean):,}")
    c2.metric("Charging stations", f"{len(ch):,}")
    c3.metric("Counties with income data", f"{health['county'].nunique()}")
    if "total_chargers" in county_full.columns:
        c4.metric(
            "Total public chargers",
            f"{int(county_full['total_chargers'].sum()):,}",
        )

    st.markdown(
        """
**How this ties to our proposal**

- Each row in the EV table represents **one registered EV in CT**.  
- Each row in the charging table represents **one public station**.  
- The county table aggregates EVs, chargers, income, and population so we can
  identify **where EV adoption is outpacing infrastructure**, especially in
  higher-income and higher-population counties.
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
- Standardized column names and parsed date fields.  
- Restricted to **CT registrations only** and removed duplicate IDs.  
- Cleaned city names, vehicle make, and model text.  
- Created:
    - `ev_category` from `fuel_code` (BEV / PHEV / Other)  
    - `ev_count = 1` so each row counts as one vehicle.
"""
        )
        st.dataframe(ev_clean.head(25), use_container_width=True)

    with st.expander("Charging stations (Electric_Vehicle_Charging_Stations.csv)", True):
        st.markdown(
            """
- Standardized column names and cleaned city names.  
- Converted Level 1, Level 2, and DC fast columns to integers.  
- Created:
    - `total_chargers` (L1 + L2 + DC fast)  
    - Flags: `has_dc_fast`, `has_level2`, `has_level1`  
    - Parsed geospatial info into lat/lon where available.
"""
        )
        st.dataframe(ch.head(25), use_container_width=True)

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
    - `chargers_per_1k_people`.

This is the **core table** for our gap analysis and proposal.
"""
        )
        st.dataframe(county_full, use_container_width=True)

        csv = county_full.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download county summary as CSV",
            csv,
            file_name="ct_ev_county_summary.csv",
            mime="text/csv",
        )

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
            x=alt.X("county:N", sort="-y", title="County"),
            y=alt.Y("ev_registrations:Q", title="EV registrations"),
            tooltip=[
                "county:N",
                "ev_registrations:Q",
                "total_chargers:Q",
                "median_income:Q",
                "population_2016:Q",
            ],
        )
        .properties(height=350)
    )
    st.altair_chart(ev_bar, use_container_width=True)

    # EVs per charger vs median income
    st.markdown("##### EVs per charger vs median household income")
    df1 = county_full.dropna(subset=["evs_per_charger", "median_income"])
    scatter1 = (
        alt.Chart(df1)
        .mark_circle(size=150)
        .encode(
            x=alt.X("median_income:Q", title="Median household income (USD)"),
            y=alt.Y("evs_per_charger:Q", title="EVs per public charger"),
            color=alt.Color("county:N", legend=None),
            tooltip=[
                "county:N",
                "ev_registrations:Q",
                "total_chargers:Q",
                "evs_per_charger:Q",
                "median_income:Q",
            ],
        )
        .interactive()
    )
    st.altair_chart(scatter1, use_container_width=True)

    # EVs per 1k people vs chargers per 1k people
    st.markdown("##### EVs per 1,000 people vs chargers per 1,000 people")
    df2 = county_full.dropna(subset=["evs_per_1k_people", "chargers_per_1k_people"])
    scatter2 = (
        alt.Chart(df2)
        .mark_circle(size=150)
        .encode(
            x=alt.X("evs_per_1k_people:Q", title="EVs per 1,000 people"),
            y=alt.Y("chargers_per_1k_people:Q", title="Chargers per 1,000 people"),
            color=alt.Color("county:N", legend=None),
            tooltip=[
                "county:N",
                "evs_per_1k_people:Q",
                "chargers_per_1k_people:Q",
                "ev_registrations:Q",
                "total_chargers:Q",
                "population_2016:Q",
            ],
        )
        .interactive()
    )
    st.altair_chart(scatter2, use_container_width=True)

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

    # Ensure we have lat/lon
    ch_map = ch_filtered.copy()
    if "lat" not in ch_map.columns or "lon" not in ch_map.columns:
        # Try to infer from other columns
        if "latitude" in ch_map.columns and "longitude" in ch_map.columns:
            ch_map["lat"] = pd.to_numeric(ch_map["latitude"], errors="coerce")
            ch_map["lon"] = pd.to_numeric(ch_map["longitude"], errors="coerce")
        elif "new_georeferenced_column" in ch_map.columns:
            coords = ch_map["new_georeferenced_column"].astype(str).str.extract(
                r"POINT\s*\(([-\d\.]+)\s+([-\d\.]+)\)"
            )
            ch_map["lon"] = pd.to_numeric(coords[0], errors="coerce")
            ch_map["lat"] = pd.to_numeric(coords[1], errors="coerce")

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
