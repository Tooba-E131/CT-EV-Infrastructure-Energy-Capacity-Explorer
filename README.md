Connecticut EV Infrastructure & Energy Capacity Explorer
A data-driven analysis examining whether Connecticut’s rapid electric vehicle (EV) adoption is adequately supported by public charging infrastructure and municipal energy capacity. The project integrates multiple datasets to identify gaps, forecast strain, and provide actionable policy insights.
📌 Project Overview
This project investigates the relationship between:
EV adoption
Public charging infrastructure
City-level electricity capacity
Using high-quality Connecticut municipal datasets, we build a unified analytical framework to:
Identify EV adoption trends
Evaluate whether infrastructure growth keeps pace
Examine grid capacity constraints
Reveal underserved counties and cities
Provide data-driven policy recommendations
Connecticut’s clean and consistent datasets make it an ideal case study for cross-sector EV analysis.
🚀 Live Streamlit App
🔗 https://ct-ev-infrastructure-energy-capacity-explorer.streamlit.app
The app features:
City & county-level EV adoption
Charging station distribution
Charger Pressure Index & underserved area identification
Grid load & peak demand indicators
Interactive filters, visuals, and insights
📁 Repository Contents
├── app.py                                  # Streamlit application
├── Data cleaning + Analysis (1).ipynb      # Full data cleaning & analysis workflow
├── Electric_Vehicle_Registration_Data.csv  # EV adoption dataset
├── Electric_Vehicle_Charging_Stations.csv  # Public charging station dataset
├── 2016cityandcountyenergyprofiles.csv     # Energy capacity dataset
├── HDPulse_data_export.csv                 # Supplemental socioeconomic dataset
├── Connecticut-EV-Infrastructure-and-Energy-Capacity-Analysis.pdf  # Presentation slides
└── README.md
🧩 Project Motivation
As outlined in the project goals, our analysis focuses on answering:
Is EV adoption outpacing charging infrastructure growth?
Where are the geographic mismatches between EV demand and public charging availability?
What grid constraints could limit future EV expansion?
Given Connecticut’s aggressive clean-transportation targets, these insights directly support state-level planning.
🔍 Data Sources
This project integrates three primary data streams:
1. Transportation Data
EV registration counts by city & county
EV model types and adoption years
2. Energy Consumption & Grid Capacity Data
Municipal electricity-use profiles
Peak load indicators
City-level energy demand distributions
3. Demographic & Socioeconomic Data
Median household income
Population density
Housing characteristics
This triangulation provides a holistic understanding of EV mobility readiness statewide.
📊 Key Findings
1. EV Adoption Outpaces Public Charging Growth
EV ownership is rising rapidly across Connecticut, but infrastructure has not kept up.
2. Severe City-Level Infrastructure Gaps
Affluent towns like New Canaan, Weston, and Avon have high EV adoption but minimal public charging options.
3. Charger Pressure Index (CPI)
Some municipalities face 700–1,100 EVs per public charger, indicating severe unmet demand.
4. Predictors of EV Adoption
Regression analysis shows:
Each additional port → ≈15 more EVs
Every $1,000 in median income → ≈18 more EVs
5. Future EV Surge & Grid Stress
By 2026, Connecticut is projected to exceed 60,000 EVs (+45% from 2023).
High-load hubs like Stamford, Westport, Greenwich, and Fairfield may surpass 334 MW peak load thresholds.
🗺️ Interactive Visualizations
The Streamlit app provides:
County Comparison Dashboard
Charger Pressure Maps
Energy Load & Peak Demand Indicators
Scatterplots connecting EV adoption with income and infrastructure
Filterable maps and views
These help identify underserved regions and anticipate future energy strain.
🧭 Recommendations
1. Prioritize Charging Deserts
Invest in high-EV, low-charger communities:
New Canaan, Weston, Avon, Riverside, Old Greenwich
2. Adopt Data-Driven Infrastructure Planning
Use forecasting models to allocate new charging ports strategically.
3. Accelerate DC Fast Charger Deployment
Enhance charging efficiency beyond major hubs.
4. Modernize the Grid Proactively
Coordinate with utilities to prepare for projected 2026 peak loads.
🛠️ Installation & Local Development
1. Clone the Repository
git clone https://github.com/Tooba-E131/CT-EV-Infrastructure-Energy-Capacity-Explorer.git
cd CT-EV-Infrastructure-Energy-Capacity-Explorer
2. Install Dependencies
pip install -r requirements.txt
3. Run the Streamlit App
streamlit run app.py
👥 Team Members
Tooba Edhi
Supriya Sinha
Tavishi Chaturvedi
Tejas Kulkarni
