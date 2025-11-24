# Genshin Impact Banner Sales & Perception Dataset + ETL

This repository accompanies the research project:

**“Do pre-banner player perceptions affect Genshin Impact banner sales?”**

It provides:
1. A reproducible ETL pipeline to assemble a banner-level panel dataset.
2. Pre-banner *perception* proxies (demand-side signals).
3. Structural *in-game* controls (supply-side features).
4. Analysis notebooks for baseline and robustness models.

---

## Research Question

After controlling for structural banner features (new vs rerun, double banners, meta role, etc.),  
**do pre-banner perception signals independently predict banner revenue?**

---

## Data Overview

### Unit of observation
**One row = one 5★ banner run, phase-level (Phase 1 or Phase 2).**

Time span: **Version 1.0 → latest patch available at run-time.**

### Dependent variable
- `revenue_cn_ios_usd`  
  Estimated CN-iOS banner revenue at phase level, exported from GenshinLab.
- `log_revenue`  
  Natural log transform for skewness.

### Structural covariates (S)
Examples:
- `is_new`, `is_rerun`, `rerun_count`
- `days_since_last_run`
- `is_double_banner`
- `element`, `weapon_type`
- `role_at_launch`, `meta_tier_at_launch`
- `archon_flag`, `harbinger_flag`
- patch controls (`new_region_patch`, etc.)

### Perception covariates (P)
Pre-banner demand-side signals:
- YouTube demo/teaser views + engagement (7-day pre-banner window)
- Reddit buzz + sentiment (14-day pre-banner window)
- Twitter/X buzz + sentiment (14-day pre-banner window)
- Google Trends mean/peak (14-day pre-banner window)
- Influencer hype (optional module)

---

## Repository Layout

- `etl/`  
  Modular scripts to scrape/collect raw data and merge into final panel.

- `data_raw/`  
  Raw inputs (some scraped, some manually exported).  
  **Do not edit scraped raw files.** Add new exports here.

- `data_out/`  
  Final merged datasets ready for analysis.

- `notebooks/`  
  Exploratory analysis, baseline model, robustness checks.

- `paper/`  
  Methods section + codebook for journal submission.

---

## Setup

### 1. Clone
```bash
git clone https://github.com/<your-username>/genshin-banner-perception.git
cd genshin-banner-perception
