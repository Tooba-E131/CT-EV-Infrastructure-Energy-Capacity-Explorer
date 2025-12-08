# Connecticut EV Infrastructure & Energy Capacity Explorer

A data-driven analysis examining whether Connecticut’s rapid electric vehicle (EV) adoption is adequately supported by public charging infrastructure and municipal energy capacity. This project integrates multiple datasets to identify gaps, forecast strain, and provide actionable policy insights.

---

## 📌 Project Overview

This project investigates the relationship between:

- **EV adoption**
- **Public charging infrastructure**
- **City-level electricity capacity**

Using Connecticut’s clean municipal datasets, we developed a unified analytical framework to:

- Identify EV adoption trends  
- Evaluate whether infrastructure growth keeps pace  
- Examine grid capacity constraints  
- Reveal underserved counties and cities  
- Provide data-driven policy recommendations  

---

## 🚀 Live Streamlit App

🔗 **https://ct-ev-infrastructure-energy-capacity-explorer.streamlit.app**

The app includes:

- City & county-level EV adoption  
- Public charging station distribution  
- Charger Pressure Index & underserved area detection  
- Energy capacity and grid load indicators  
- Interactive filters, maps, charts, and insights  

---

## 📁 Repository Contents
├── app.py # Streamlit application
├── Data cleaning + Analysis (1).ipynb # Full data cleaning & analysis workflow
├── Electric_Vehicle_Registration_Data.csv # EV adoption dataset
├── Electric_Vehicle_Charging_Stations.csv # Public charging station dataset
├── 2016cityandcountyenergyprofiles.csv # Energy capacity dataset
├── HDPulse_data_export.csv # Supplemental socioeconomic dataset
├── Connecticut-EV-Infrastructure-and-Energy-Capacity-Analysis.pdf # Presentation slides
└── README.md


---

## 🧩 Project Motivation

This project aims to answer key statewide questions:

- **Is EV adoption in Connecticut outpacing charging infrastructure growth?**  
- **Where are geographic mismatches between EV demand and public charging?**  
- **Which cities will face grid stress as EV adoption accelerates?**  

Given the state's ambitious EV and clean-energy targets, these insights directly inform statewide planning and investment.

---

## 🔍 Data Sources

### **1. Transportation Data**
- EV registration counts by city & county  
- Model types and adoption years  

### **2. Energy Consumption & Grid Capacity Data**
- Municipal electricity-use profiles  
- Peak load indicators  
- Local energy demand distributions  

### **3. Demographic & Socioeconomic Data**
- Median household income  
- Population density  
- Housing characteristics  

Together, these datasets provide a holistic picture of EV readiness across the state.

---

## 📊 Key Findings

### **1. EV Adoption Outpaces Charging Infrastructure**
Statewide EV ownership is rising quickly, but infrastructure is not keeping pace.

### **2. Severe Infrastructure Gaps in Wealthy Towns**
Cities such as **New Canaan, Weston, and Avon** have large EV fleets but minimal public charging access.

### **3. Charger Pressure Index (CPI)**
Several towns experience **700–1,100 EVs per public charger**, indicating severe unmet demand.

### **4. Predictors of EV Adoption**
Regression analysis reveals:  
- **Each additional public port → ≈15 more EVs**  
- **Every $1,000 increase in median income → ≈18 more EVs**  

### **5. Future EV Surge & Grid Stress**
By **2026**, Connecticut is projected to exceed **60,000 EVs** (+45% since 2023).  
High-load hubs like **Stamford, Westport, Greenwich, and Fairfield** may exceed **334 MW** peak loads.

---

## 🗺️ Interactive Visualizations

The Streamlit dashboard includes:

- County comparison charts (EV adoption vs. charger availability)  
- Charger Pressure Index heatmaps  
- Grid load and peak-demand indicators  
- Scatterplots linking EV adoption with income and infrastructure  
- Filterable maps and views  

These visuals highlight infrastructure disparities and future grid constraints.

---

## 🧭 Recommendations

### **1. Prioritize Charging Deserts**
Expand infrastructure in high-EV, low-charger towns such as:
**New Canaan, Weston, Avon, Riverside, Old Greenwich**

### **2. Use Data-Driven Infrastructure Planning**
Deploy chargers strategically using demand-forecasting models.

### **3. Accelerate DC Fast Charger Deployment**
Boost fast-charging accessibility beyond major urban hubs.

### **4. Modernize the Grid Proactively**
Coordinate with utilities to prepare for projected 2026 load exceedances.



## 👥 Team Members
Tooba Edhi
Supriya Sinha
Tavishi Chaturvedi
Tejas Kulkarni


---

## 🛠️ Installation & Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/Tooba-E131/CT-EV-Infrastructure-Energy-Capacity-Explorer.git
cd CT-EV-Infrastructure-Energy-Capacity-Explorer
