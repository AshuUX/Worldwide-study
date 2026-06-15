def apply_interactions(agent_outputs: dict, year: int, month: int) -> dict:
    # Rule 1: ENSO × PDO amplification
    enso_phase = agent_outputs["enso"]["state"]["enso_phase"]
    pdo_phase = agent_outputs["pdo"]["state"]["pdo_phase"]
    enso_mult = agent_outputs["enso"]["contribution_multiplier"]
    pdo_mult = agent_outputs["pdo"]["contribution_multiplier"]

    if (enso_phase == "el_nino" and pdo_phase == "positive") or \
       (enso_phase == "la_nina" and pdo_phase == "negative"):
        combined_climate_mult = enso_mult * pdo_mult * 1.3
    else:
        combined_climate_mult = enso_mult * pdo_mult

    # Rule 2: Puelche accelerates snowmelt
    snowmelt_m3s = agent_outputs["snowpack"]["contribution_m3s"]
    puelche_melt_acc = agent_outputs["puelche"].get("melt_accelerator", 1.0)
    snowmelt_m3s_adjusted = snowmelt_m3s * puelche_melt_acc

    # Rule 3: Soil moisture determines runoff fraction of precipitation contribution
    runoff_frac = agent_outputs["soil_moisture"]["runoff_fraction"]
    precip_contrib_m3s = agent_outputs["precip_anomaly"]["contribution_m3s"]
    puelche_precip_supp = agent_outputs["puelche"].get("precip_suppressor", 1.0)
    precip_runoff_m3s = (precip_contrib_m3s * puelche_precip_supp) * runoff_frac

    # Rule 4: ENSO scales glacier melt (+20% El Niño, -5% La Niña)
    glacier_m3s = agent_outputs["glacier"]["contribution_m3s"]
    if enso_phase == "el_nino":
        glacier_m3s *= 1.20
    elif enso_phase == "la_nina":
        glacier_m3s *= 0.95

    # Rule 5: AAO suppresses precip contribution in winter
    aao_mult = agent_outputs["aao"]["contribution_multiplier"]
    precip_runoff_m3s *= aao_mult

    # Combine all contributions
    total_base_flow_m3s = snowmelt_m3s_adjusted + glacier_m3s + precip_runoff_m3s
    total_flow_m3s = total_base_flow_m3s * combined_climate_mult

    return {
        "total_flow_m3s": max(0.0, total_flow_m3s),
        "climate_multiplier": combined_climate_mult,
        "components": {
            "snowmelt": snowmelt_m3s_adjusted,
            "glacier": glacier_m3s,
            "precip_runoff": precip_runoff_m3s,
        }
    }
