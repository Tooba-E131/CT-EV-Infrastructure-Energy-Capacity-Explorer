📌 Project Overview
This project investigates the relationship between EV adoption, public charging infrastructure, and city-level electricity capacity across Connecticut. Using publicly available municipal datasets—one of the few states with well-aligned geographic data—we build a unified analytical framework to:
Identify EV adoption trends
Evaluate whether charging infrastructure keeps pace
Examine grid capacity constraints
Reveal underserved counties and cities
Provide data-driven policy recommendations
According to the project brief, Connecticut’s clean and consistent datasets make it an ideal case study for cross-sectoral EV infrastructure analysis.



🚀 Live Streamlit App
🔗 https://ct-ev-infrastructure-energy-capacity-explorer.streamlit.app
The app includes:
City & county-level EV adoption
Public charging station distribution
Charger pressure & underserved area identification
Energy capacity and grid load indicators
Interactive filters, visuals, and insights



📁 Repository Contents
├── app.py                                  # Streamlit application
├── Data cleaning + Analysis (1).ipynb      # Full data cleaning & analysis workflow
├── Electric_Vehicle_Registration_Data.csv  # EV adoption dataset
├── Electric_Vehicle_Charging_Stations.csv  # Public charging station dataset
├── 2016cityandcountyenergyprofiles.csv     # Energy capacity dataset
├── HDPulse_data_export.csv                 # Supplemental socioeconomic dataset
├── Connecticut-EV-Infrastructure-and-Energy-Capacity-Analysis.pdf # Presentation slides
└── README.md



🧩 Project Motivation
As summarized in the project aims (PDF p.2), the analysis focuses on answering:
Is EV adoption in Connecticut outpacing infrastructure growth?
Where are the geographic mismatches between EV demand and public charging capacity?
What grid constraints could limit future EV expansion?
Connecticut has aggressive EV adoption goals, making these insights directly relevant for planning.
🔍 Data Sources
This project integrates three primary data streams (Unified Analytical Framework, PDF p.3) :
1. Transportation Data
EV registration counts by city & county
EV model types and year of adoption
2. Energy Consumption & Grid Capacity Data
Municipal electricity-use profiles
Peak load indicators
City-level energy demand distributions
3. Demographic & Socioeconomic Data
Median income
Population density
Housing characteristics
This triangulation enables a holistic view of EV mobility readiness across the state.



📊 Key Findings
1. EV Adoption Outpaces Public Charging Growth
Connecticut EV ownership is rising rapidly, but infrastructure has not kept pace (PDF p.5) .
2. Severe City-Level Infrastructure Gaps
Even within well-served counties, many wealthy suburbs—New Canaan, Weston, Avon—have very few or no public charging ports, despite high EV counts.
3. Charger Pressure Index (CPI)
Some cities face 700–1,100 EVs per public charger, indicating severe strain and unmet charging demand (PDF p.5) .
4. Predictors of EV Adoption
Regression analysis reveals:
Each additional public port is associated with ≈15 more EVs
Every $1,000 increase in median income predicts ≈18 additional EVs (PDF p.6)
5. Future EV Surge & Grid Stress
By 2026, Connecticut is projected to exceed 60,000 EVs, a 45%+ rise from 2023.
High-load hubs such as Stamford, Westport, Greenwich, and Fairfield are projected to exceed 334 MW peak load thresholds (PDF p.7) .



🗺️ Interactive Visualizations
The Streamlit app provides:
County Comparison Dashboard: EV adoption vs. charging capacity
Charger Pressure Maps
Energy Load & Peak Demand Indicators
City-Level Scatterplots linking EV adoption, income, and ports
Filterable geographic views
These visuals make gaps in infrastructure—and risk of grid strain—highly interpretable for policymakers and planners.



🧭 Recommendations
Based on the integrated analysis (PDF p.8) :
1. Prioritize Charging Deserts
Invest in high-EV, low-infrastructure towns (New Canaan, Weston, Avon, Riverside, Old Greenwich).
2. Adopt Data-Driven Infrastructure Planning
Use regression-based demand forecasting to strategically deploy new ports.
3. Accelerate DC Fast Charger Deployment
Expand beyond major hubs; diversify charger types to meet growing daily mobility needs.
4. Modernize the Grid Proactively
Coordinate with utilities to upgrade systems ahead of projected 2026 load peaks.



🛠️ Installation & Local Development
1. Clone the Repository
git clone https://github.com/Tooba-E131/CT-EV-Infrastructure-Energy-Capacity-Explorer.git
cd CT-EV-Infrastructure-Energy-Capacity-Explorer
2. Install Dependencies
pip install -r requirements.txt
3. Run Streamlit App
streamlit run app.py



👥 Team Members
Tooba Edhi
Supriya Sinha
Tavishi Chaturvedi
Tejas Kulkarni
