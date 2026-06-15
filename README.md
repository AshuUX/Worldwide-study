# Chile Hydropower Parametric Insurance Platform

An open-source pipeline from Andean hydrology to parametric insurance
trigger design, validated against 60 years of DGA discharge data.

## What this does
1. Models monthly flow probability distributions for Chilean river basins
   using a 10-agent physically-informed swarm model
2. Benchmarks against historical climatology
3. Translates flow distributions to plant-level generation probability curves
4. Designs parametric insurance triggers with calibrated breach probabilities
5. Computes illustrative premium ranges with explicit loading assumptions

## Key results
- Maule basin, 1960-2024
- Skill score: improvement over naive baseline (see validation_suite/skill_score.py)
- 2021 megadrought: actual generation within P10-P90 interval ✓
- Basis risk: assessed for run-of-river and storage plants

## Quickstart
```bash
git clone https://github.com/[username]/chile-hydro-insurance
cd chile-hydro-insurance
pip install -r requirements.txt
# set up data accounts (see docs/data_sources.md)
python data_pipeline/fetch_noaa.py  # no account needed
python data_pipeline/fetch_era5.py  # needs free Copernicus account
python data_pipeline/clean.py
export PYTHONPATH=$PYTHONPATH:.
python hydrology_engine/runner.py
```

## Interactive dashboard
Run locally using Streamlit:
```bash
streamlit run dashboard/app.py
```

## Nepal adapter
See nepal_adapter/ — same methodology adapted to Himalayan basins
using DHM data parameters.

## License
MIT — free to use, modify, and distribute with attribution.
