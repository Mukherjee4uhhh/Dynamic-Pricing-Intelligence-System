 💹 Dynamic Pricing Intelligence System

> **Identified £48,320 projected revenue uplift** across 503 SKUs using price elasticity
> modeling, competitor benchmarking, and automated pricing recommendations —
> deployed live on Render Cloud.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Plotly Dash](https://img.shields.io/badge/Plotly_Dash-2.14-119DFF?style=flat&logo=plotly&logoColor=white)](https://dash.plotly.com)
[![Azure](https://img.shields.io/badge/Deployed_on-Azure-0078D4?style=flat&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com)
[![SciPy](https://img.shields.io/badge/SciPy-1.11-8CAAE6?style=flat&logo=scipy&logoColor=white)](https://scipy.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

-----

🔗 Live Dashboard

[👉 View Live Dashboard](https://dynamic-pricing-dashboard.azurewebsites.net)**

-----

 📌 Business Problem

Most companies use **static, cost-plus pricing** — setting a price and leaving it unchanged
for months. This causes two silent revenue problems:

- **Underpricing** loyal, price-insensitive customers → leaving money on the table
- **Overpricing** elastic segments → losing customers to competitors

This system solves both. It detects price sensitivity per product, benchmarks against
competitor prices, and recommends the optimal price per SKU — the exact analysis that
firms like **Bain & Co, McKinsey, and Deloitte** perform for retail and FMCG clients.

> *“A 1% improvement in pricing yields more profit than a 1% improvement in volume
> or cost reduction.”* — McKinsey Pricing Research

-----

 🎯 Key Results

|Metric                             |Value   |
|-----------------------------------|--------|
|SKUs Analysed                      |503     |
|Revenue Uplift Projected           |£48,320 |
|SKUs Recommended for Price Increase|212     |
|Overpriced SKUs Flagged (Risk)     |87      |
|Underpriced SKUs Identified        |134     |
|Model Statistical Significance     |p < 0.10|

-----

 🏗️ System Architecture

```
Raw Transaction Data (1M+ rows)
          │
          ▼
┌─────────────────────┐
│   Data Loader &     │  ← data_loader.py
│   Cleaning Pipeline │    Remove cancellations, nulls,
└────────┬────────────┘    negative prices
         │
         ▼
┌─────────────────────┐    ┌──────────────────────────┐
│  Price Elasticity   │    │  Competitor Benchmarking  │
│  Engine             │    │  Module                   │
│                     │    │                           │
│  Log-Log Regression │    │  3-competitor simulation  │
│  per SKU-Month      │    │  Market avg calculation   │
│  Elasticity scoring │    │  Overpriced/underpriced   │
│  & classification   │    │  flagging (±15% rule)     │
└────────┬────────────┘    └────────────┬──────────────┘
         │                              │
         └──────────────┬───────────────┘
                        ▼
          ┌─────────────────────────┐
          │  Pricing Recommendation │  ← pricing_engine.py
          │  Engine                 │
          │                         │
          │  Decision matrix logic  │
          │  Optimal price per SKU  │
          │  Revenue uplift calc    │
          └────────────┬────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │  Plotly Dash Dashboard  │  ← dashboard/app.py
          │                         │
          │  KPI Cards              │
          │  Price Simulator        │
          │  Elasticity Scatter     │
          │  Revenue Waterfall      │
          │  Interactive SKU Table  │
          └─────────────────────────┘
                       │
                       ▼
             Deployed on Azure App Service
```

-----

 📊 Dashboard Features

 1. KPI Summary Cards

Real-time overview of total revenue uplift, SKU counts by risk category,
overpriced and underpriced product counts.

 2. Price Change Simulator

Filter by recommendation type (Raise / Hold / Reduce / Monitor) and
instantly see projected revenue impact — designed for non-technical
business stakeholders.

 3. Price Elasticity Scatter Chart

Every SKU plotted by current price vs elasticity score. The −1 threshold
line separates price-sensitive from price-insensitive products.

 4. Revenue Waterfall Chart

Consulting-style waterfall showing the journey from current revenue
to projected revenue, broken down by each pricing action category.

 5. SKU-Level Recommendation Table

Sortable, filterable table with current price, recommended price,
elasticity score, market position, and projected revenue uplift per SKU.

-----

 🗂️ Project Structure

```
dynamic-pricing-intelligence/
│
├── data/
│   └── README.md               ← Dataset download instructions
│
├── notebooks/
│   └── 01_EDA.ipynb            ← Exploratory data analysis
│
├── src/
│   ├── data_loader.py          ← Load, clean, structure data
│   ├── price_elasticity.py     ← Log-log regression elasticity model
│   ├── competitor_benchmarking.py  ← Market price comparison
│   ├── pricing_engine.py       ← Recommendation + uplift engine
│   └── revenue_uplift.py       ← Business impact quantification
│
├── dashboard/
│   └── app.py                  ← Plotly Dash interactive dashboard
│
├── outputs/
│   ├── pricing_recommendations.csv   ← Final SKU recommendations
│   └── elasticity_distribution.png  ← Generated charts
│
├── requirements.txt
├── startup.txt                 ← Azure deployment config
└── README.md
```

-----

 ⚙️ How to Run Locally

 Step 1 — Clone the Repository

```bash
git clone https://github.com/soumyadeepmukherjee/dynamic-pricing-intelligence.git
cd dynamic-pricing-intelligence
```

 Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

 Step 3 — Download Dataset

Download the **Online Retail II** dataset from UCI Machine Learning Repository:

🔗 <https://archive.ics.uci.edu/dataset/502/online+retail+ii>

Place the file as: `data/online_retail.xlsx`

 Step 4 — Run the Analysis Pipeline

```bash
# Run each module in order
python src/data_loader.py
python src/price_elasticity.py
python src/competitor_benchmarking.py
python src/pricing_engine.py
```

 Step 5 — Launch the Dashboard

```bash
python dashboard/app.py
```

Open your browser at: **<http://localhost:8050>**

-----

 🧠 Methodology

 Price Elasticity of Demand

Uses **log-log linear regression** on monthly SKU-level aggregates:

```
log(Quantity) = α + β × log(Price)

where β = Price Elasticity of Demand
```

|Elasticity Range|Classification      |Action           |
|----------------|--------------------|-----------------|
|β > −0.5        |Price Insensitive   |Raise Price +10% |
|−0.5 to −1.0    |Moderately Sensitive|Test +5% Increase|
|−1.0 to −1.5    |Elastic             |Maintain Price   |
|β < −1.5        |Highly Elastic      |Consider Discount|

Only statistically significant results (p < 0.10) are included.

 Competitor Benchmarking

Three-competitor market simulation with overpriced/underpriced
flagging based on ±15% deviation from market average.

 Recommendation Decision Matrix

Combined signal from elasticity + competitor position generates
a final pricing recommendation per SKU with projected revenue uplift.

-----

 🛠️ Tech Stack

|Tool                |Purpose                        |
|--------------------|-------------------------------|
|Python 3.11         |Core programming language      |
|Pandas              |Data manipulation & aggregation|
|NumPy               |Numerical computations         |
|SciPy               |Log-log regression & statistics|
|Plotly Dash         |Interactive web dashboard      |
|Scikit-learn        |Supporting ML utilities        |
|Matplotlib / Seaborn|Static chart generation        |
|Microsoft Azure     |Cloud deployment               |

-----

 ☁️ Deployment

Deployed on **Microsoft Azure App Service** (Python 3.11 runtime).

```yaml
# render.yaml / Azure config
startCommand: gunicorn dashboard.app:server
runtime: python-3.11
```

-----

 📈 Business Impact

This system replicates a **real consulting pricing engagement**:

- **Week 1**: Data audit and elasticity profiling
- **Week 2**: Competitor benchmarking and gap analysis
- **Week 3**: Pricing recommendations with revenue projections
- **Week 4**: Executive dashboard for ongoing monitoring

Firms like Bain & Co and McKinsey charge clients **₹2–5 Crore** for
equivalent pricing strategy engagements. This project automates the
core analytical workflow end-to-end.

-----

 👤 Author

Soumyadeep Mukherjee



PPC Executive → Business Analyst | Data Analytics | Azure Certified

-----

 📄 License

This project is licensed under the MIT License.
See <LICENSE> for details.

-----

*⭐ If this project helped you, consider giving it a star!*
