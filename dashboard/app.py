import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from hydrology_engine.runner import HydrologyRunner
from hydrology_engine.baseline import compute_baseline
from generation_translator.translator import flow_to_generation
from insurance_engine.trigger import design_trigger
from insurance_engine.pricing import illustrative_premium
import json

st.set_page_config(page_title="Chile Hydropower Insurance", layout="wide")

@st.cache_data
def load_data():
    master = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    with open("generation_translator/plants_chile.json", "r") as f:
        plants = json.load(f)["plants"]
    cne = pd.read_csv("data/raw/cne_generation.csv", parse_dates=["date"])
    return master, plants, cne

master, plants, cne = load_data()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Hydrology", "Generation", "Insurance"])

if page == "Hydrology":
    st.title("Basin Hydrology")

    col1, col2 = st.columns(2)
    basin = col1.selectbox("Basin", ["Maule", "Biobío", "Aysén"])
    year = col2.slider("Year", 1960, 2024, 2021)

    runner = HydrologyRunner()

    # Chart 1: Fan chart for selected year
    months = list(range(1, 13))
    p10, p50, p90 = [], [], []
    for m in months:
        res = runner.run(year, m)
        p10.append(res["p10"])
        p50.append(res["p50"])
        p90.append(res["p90"])

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=months, y=p90, fill=None, mode='lines', line_color='rgba(0,100,80,0.2)', name='P90'))
    fig1.add_trace(go.Scatter(x=months, y=p10, fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)', name='P10'))
    fig1.add_trace(go.Scatter(x=months, y=p50, mode='lines+markers', line_color='rgb(0,100,80)', name='Swarm P50'))

    # Add baseline
    bl = compute_baseline(master)
    fig1.add_trace(go.Scatter(x=months, y=bl["mean_m3s"], mode='lines', line_dash='dash', name='Baseline'))

    fig1.update_layout(title=f"Flow Probability for {year}", xaxis_title="Month", yaxis_title="Flow (m3/s)")
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Historical discharge
    fig2 = px.line(master, x="date", y="flow_m3s", title="Historical Discharge 1960-2024")
    # Highlight drought years
    drought_years = [2021, 2019, 2015, 1998]
    for dy in drought_years:
        fig2.add_vrect(x0=f"{dy}-01-01", x1=f"{dy}-12-31", fillcolor="red", opacity=0.2, layer="below", line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Generation":
    st.title("Plant Generation")

    plant_names = [p["name"] for p in plants]
    plant_name = st.selectbox("Select Plant", plant_names)
    plant = next(p for p in plants if p["name"] == plant_name)

    year_gen = st.slider("Year", 2000, 2024, 2021)
    month_gen = st.slider("Month", 1, 12, 10)

    runner = HydrologyRunner()
    flow_res = runner.run(year_gen, month_gen)
    gen_res = flow_to_generation(flow_res, plant)

    st.write(f"### {plant_name} Generation Distribution for {year_gen}-{month_gen:02d}")

    # PDF Curve
    samples = gen_res["samples"]
    fig = px.histogram(samples, nbins=50, histnorm='probability density', title="Generation Probability Density")
    st.plotly_chart(fig, use_container_width=True)

    st.metric("P50 Generation", f"{gen_res['p50_gwh']:.2f} GWh")

    # Actuals
    actual = cne[(cne["plant_name"] == plant_name) & (cne["date"].dt.year == year_gen) & (cne["date"].dt.month == month_gen)]
    if not actual.empty:
        st.write(f"Actual Generation: {actual['generation_gwh'].iloc[0]:.2f} GWh")

elif page == "Insurance":
    st.title("Insurance Triggers & Pricing")

    plant_name_ins = st.selectbox("Select Plant", [p["name"] for p in plants])
    plant_ins = next(p for p in plants if p["name"] == plant_name_ins)
    payout = st.number_input("Payout Amount (USD)", value=5000000)

    # For speed in dashboard, we'll run 12 months for 2023 as example
    runner = HydrologyRunner()
    monthly_gen_dists = []
    for m in range(1, 13):
        f_res = runner.run(2023, m)
        g_res = flow_to_generation(f_res, plant_ins)
        monthly_gen_dists.append(g_res)

    triggers = design_trigger(monthly_gen_dists, plant_ins)
    pricing = illustrative_premium(triggers, payout, calibration_error=0.15)

    st.table(pd.DataFrame(pricing).T)

    st.warning("ILLUSTRATIVE ONLY — not investable pricing")

    # Basis risk
    from generation_translator.basis_risk import compute_basis_risk
    # Mocking model outputs for basis risk calculation over a few years
    model_outputs = []
    for y in range(2020, 2024):
        for m in range(1, 13):
             f_res = runner.run(y, m)
             g_res = flow_to_generation(f_res, plant_ins)
             model_outputs.append({"year": y, "month": m, "p50_gwh": g_res["p50_gwh"]})

    br = compute_basis_risk(model_outputs, cne, plant_name_ins)
    if br["flag"] == "HIGH_BASIS_RISK":
        st.error(f"HIGH BASIS RISK: RMSE {br['rmse_pct']:.1f}%")
    else:
        st.success(f"ACCEPTABLE BASIS RISK: RMSE {br['rmse_pct']:.1f}%")
