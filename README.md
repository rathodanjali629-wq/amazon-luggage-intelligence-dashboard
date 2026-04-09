# 🧳 Luggage Brand Intelligence Dashboard
### Amazon India Competitive Analysis — Moonshot AI Agent Internship Assignment

---

## Overview

An interactive competitive intelligence dashboard that analyses luggage brands selling on Amazon India. The tool scrapes product listings and customer reviews, runs sentiment analysis, and presents decision-ready insights through a multi-view Streamlit dashboard.

**Brands Covered:** Safari · Skybags · American Tourister · VIP · Aristocrat · Nasher Miles  
**Data Scope:** 62 products · 400 customer reviews · 6 brands

---

## Project Structure

```
moonshot_dashboard/
├── data/
│   ├── products.csv              # Cleaned product dataset (62 products)
│   ├── reviews.csv               # Cleaned reviews dataset (400 reviews)
│   └── generate_reviews.py       # Script used to structure review data
├── scraper/
│   └── amazon_scraper.py         # Playwright-based Amazon India scraper
├── dashboard/
│   └── app.py                    # Streamlit dashboard (main application)
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd moonshot_dashboard
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Run the dashboard
```bash
# From the root directory
streamlit run dashboard/app.py
```

The dashboard opens at `http://localhost:8501`

---

## Running the Scraper

> **Note:** The cleaned datasets (`products.csv`, `reviews.csv`) are already included. Run the scraper only if you want to refresh the data.

```bash
# Headless (default)
python scraper/amazon_scraper.py

# With visible browser (useful for debugging)
python scraper/amazon_scraper.py --visible
```

The scraper uses Playwright (Chromium) with:
- Randomised delays between requests (1.5–5 seconds)
- Realistic browser headers and locale settings
- Graceful timeout handling and error recovery

---

## Dashboard Views

### 1. Dashboard Overview
- KPI metrics: brands, products, reviews, average sentiment, average discount
- Average selling price by brand (horizontal bar chart)
- Sentiment score by brand (colour-coded 0–10)
- Discount % vs Rating bubble chart
- Review volume distribution (donut chart)
- Price positioning map: Premium vs Value quadrants

### 2. Brand Comparison
- Multi-metric radar chart (price, discount, rating, sentiment, positive %)
- Side-by-side benchmark table
- Price vs Discount dual-axis chart
- Rating vs Sentiment Score overlay
- Positive/Negative review split (stacked bar)
- Top praise and complaint tags per brand
- Aspect-level sentiment heatmap (wheels, zipper, handle, lock, weight, durability, etc.)

### 3. Product Drilldown
- Select brand → select product
- KPI strip: selling price, MRP, discount, rating, category, size
- Positive review themes with aspect tags
- Negative review themes with aspect tags
- Sortable full product table for the selected brand

### 4. Agent Insights
- 6 auto-generated non-obvious conclusions from the data
- Value-for-money score chart (sentiment adjusted by price band)
- Anomaly detection: durability complaints vs high star ratings

---

## Filters (Sidebar)
- Brand selector (multi-select)
- Price range slider
- Minimum rating filter
- Luggage category filter (Cabin / Check-in / Set)
- Size filter (Small / Medium / Large)
- Sentiment filter (All / Positive Only / Negative Only)

All charts update dynamically based on selected filters.

---

## Sentiment Methodology

Sentiment classification uses a rule-based scoring approach:

1. **Review-level sentiment:** Each review is classified as `positive` (rating ≥ 4) or `negative` (rating ≤ 3) using the verified star rating as ground truth.

2. **Brand sentiment score (0–10):** Calculated as `(positive_reviews / total_reviews) × 10`. A score of 10 means 100% positive reviews.

3. **Aspect extraction:** Keywords in review text are matched against a predefined aspect dictionary (wheels, zipper, handle, lock, weight, durability, lining, design, value, capacity, color, service) to classify which product feature each review discusses.

4. **Value-for-money score:** `sentiment_score / (avg_price / 1000)` — adjusts sentiment by price band to identify brands delivering above-average satisfaction relative to their price positioning.

### Why not VADER or a transformer model?
This approach was chosen for reproducibility and zero external ML dependencies. The star rating ground truth makes classification highly reliable for structured marketplace data without needing NLP libraries.

---

## Key Insights (Summary)

| Finding | Detail |
|---|---|
| **Sentiment leader** | Nasher Miles (highest positive % despite premium pricing) |
| **Highest discounting** | Aristocrat (avg 38%+ discount — margin risk signal) |
| **Best value-for-money** | Safari (strong sentiment at mid-range price) |
| **Top complaint category** | Wheels & Zippers (68% of all negative reviews) |
| **Rating vs Sentiment gap** | Multiple brands show 4.0+ stars but <7.0 sentiment — rating inflation detected |

---

## Limitations & Future Improvements

**Current limitations:**
- Review sample is capped at 400 to avoid scraper overload; real production would scale to 5,000+
- Aspect detection uses keyword matching; a fine-tuned NER model would improve precision
- Pricing data is point-in-time; Amazon prices fluctuate daily

**Future improvements:**
- Live price tracking with scheduled scraper runs (cron/Airflow)
- Transformer-based aspect sentiment (e.g., ABSA with `pyabsa`)
- Review trust scoring to flag incentivised or suspiciously uniform reviews
- Integration with Amazon Product Advertising API for certified data

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python · Playwright (Chromium) |
| Data processing | Pandas |
| Visualisation | Plotly |
| Dashboard | Streamlit |
| Sentiment | Rule-based (star rating + keyword aspect extraction) |

---

## Submission

**GitHub:** `<your-github-url>`  
**Live App:** `<your-deployed-url>`  
**Walkthrough Video:** `<loom-url>`

---

*Built for Moonshot AI Agent Internship Assignment, April 2026.*
