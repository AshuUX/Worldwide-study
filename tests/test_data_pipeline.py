import pytest
import pandas as pd
import numpy as np
import os
from data_pipeline.clean import fill_discharge_from_precip

def test_maule_discharge_loads():
    df = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    assert "flow_m3s" in df.columns
    assert df["date"].min() <= pd.Timestamp("1965-01-01")
    assert df["date"].max() >= pd.Timestamp("2024-01-01")
    assert df["flow_m3s"].isna().mean() < 0.10

def test_enso_index_loads():
    df = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    assert "enso_mei" in df.columns
    assert df["enso_mei"].isna().mean() < 0.05
    assert df["enso_mei"].between(-4, 4).mean() > 0.99

def test_era5_coverage():
    df = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    assert "precip_mm" in df.columns
    assert "temp_c" in df.columns
    assert df["precip_mm"].isna().sum() == 0
    assert df["temp_c"].between(-20, 40).all()

def test_snowpack_data():
    df = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    assert "swe_mm" in df.columns
    aug_mean = df[df["date"].dt.month == 8]["swe_mm"].mean()
    feb_mean = df[df["date"].dt.month == 2]["swe_mm"].mean()
    assert aug_mean > feb_mean * 1.5

def test_gap_filling_r2():
    df = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    filled_df, r2 = fill_discharge_from_precip(df.copy())
    assert r2 > 0.60
