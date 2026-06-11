import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import ttest_ind

FS = 100

def dataset_analysis(task_fileC, task_filePD):
    
    #caricamento dei file

    df_C = pd.read_csv(task_fileC)
    df_PD = pd.read_csv(task_filePD)
    Dem_C = pd.read_csv("controls - demographic+clinical - datasetv1.csv", header=1)
    Dem_PD = pd.read_csv("pd - demographic+clinical - datasetv1.csv", header=1)
    Dem_C = Dem_C[["Subject ID", "Age", "Sex", "Height (in)", "Weight (kg)"]]
    Dem_PD = Dem_PD[["Subject ID", "Age (years)", "Sex", "Height (in)", "Weight (kg)"]]
    Dem_PD = Dem_PD.rename(columns={"Age (years)": "Age"})
    Dem_C = Dem_C.rename(columns={"Height (in)": "Height (cm)"})
    Dem_PD = Dem_PD.rename(columns={"Height (in)": "Height (cm)"})
    Dem_PD["Height (cm)"] = Dem_PD["Height (cm)"] * 2.54
    Dem_C["Height (cm)"] = Dem_C["Height (cm)"] * 2.54

    patients_C = sorted ({col.split("_")[0] for col in df_C.columns[1:] if "_balance_" in col})
    patients_PD = sorted({col.split("_")[0] for col in df_PD.columns[1:] if "_balance_" in col})
    #calcolo ellisse 95%
    def confidence_ellipse(x, y, n_std=2.4477): 

        x = np.array(x) 
        y = np.array(y)

        if len(x) < 2:
            return np.nan

        cov = np.cov(x, y)
        eigvals, eigvecs = np.linalg.eig(cov)
        eigvals = np.maximum(eigvals, 0)


        order = eigvals.argsort()[::-1]
        eigvals = eigvals[order]
        eigvecs = eigvecs[:, order]

        radii = n_std * np.sqrt(eigvals)

        area = np.pi * radii[0] * radii[1]

        return area
    #estrazione cop globale
    def extract_global_cop(df, pz):
        x_col = f"{pz}_balance_Walkway_X"
        y_col = f"{pz}_balance_Walkway_Y"
        p_col = f"{pz}_balance_WalkwayPressureLevel"

        SENSOR_CM = 1.27

        cop_x = []
        cop_y = []

        for i in range(len(df)):

            try:

                xs = [
                    float(v) * SENSOR_CM
                    for v in str(df[x_col].iloc[i]).split("|")
                    if v not in ("nan", "")
                ]

                ys = [
                    float(v) * SENSOR_CM
                    for v in str(df[y_col].iloc[i]).split("|")
                    if v not in ("nan", "")
                ]

                pressures = [
                    float(v)
                    for v in str(df[p_col].iloc[i]).split("|")
                    if v not in ("nan", "")
                ]

                n = min(len(xs), len(ys), len(pressures))

                xs = xs[:n]
                ys = ys[:n]
                pressures = pressures[:n]

                if n > 0 and np.sum(pressures) > 0:

                    cx = np.average(xs, weights=pressures)
                    cy = np.average(ys, weights=pressures)

                else:
                    cx = np.nan
                    cy = np.nan

            except:
                cx = np.nan
                cy = np.nan

            cop_x.append(cx)
            cop_y.append(cy)

        cop_x = pd.Series(cop_x).interpolate(limit_direction="both").values

        cop_y = pd.Series(cop_y).interpolate(limit_direction="both").values

        return cop_x, cop_y
    #calcolo features
    def compute_features(df, pz):
        rx = df[f"{pz}_balance_RCOPX"].values 
        ry = df[f"{pz}_balance_RCOPY"].values
        lx = df[f"{pz}_balance_LCOPX"].values
        ly = df[f"{pz}_balance_LCOPY"].values
        gx, gy = extract_global_cop(df, pz)

        # pulizia sincronizzata (IMPORTANTISSIMO)
        def clean(x, y):
            mask = ~np.isnan(x) & ~np.isnan(y) 
            return x[mask], y[mask]

        rx, ry = clean(rx, ry)
        lx, ly = clean(lx, ly)
        gx, gy = clean(gx, gy)

        if len(rx) < 2 or len(lx) < 2 or len(gx)<2: 
            return {
            "Subject ID": pz,
            "Invalid": True,
        }

        def path(x, y):
            return np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))

        def mean_vel(x, y):

            total_path = path(x, y)
            duration = (len(x)-1) / FS

            return total_path / duration
        def asymmetry_index():
            left_cols = [f"{pz}_balance_LP{i}" for i in range(1, 17)]
            right_cols = [f"{pz}_balance_RP{i}" for i in range(1, 17)]

            lp = df[left_cols].apply(pd.to_numeric, errors="coerce")
            rp = df[right_cols].apply(pd.to_numeric, errors="coerce")
            lp = lp.interpolate(method="linear", limit_direction="both").fillna(0)
            rp = rp.interpolate(method="linear", limit_direction="both").fillna(0)

            if len(left_cols) == 0 or len(right_cols) == 0:
                return np.nan

            # media di tutti i sensori nel tempo
            mean_l = lp.to_numpy(dtype=float).mean()
            mean_r = rp.to_numpy(dtype=float).mean()

            if mean_l + mean_r == 0:
                return np.nan

            return 100 * abs(mean_r - mean_l) / ((mean_r + mean_l))

            
        return {
        "Subject ID": pz,
        "Invalid": False,
        "R_path": path(rx, ry), 
        "L_path": path(lx, ly),
        "R_vel": mean_vel(rx, ry), 
        "L_vel": mean_vel(lx, ly),
        "R_std_x": np.std(rx), 
        "R_std_y": np.std(ry),
        "L_std_x": np.std(lx),
        "L_std_y": np.std(ly),
        "R_range_x": np.max(rx) - np.min(rx), 
        "R_range_y": np.max(ry) - np.min(ry), 
        "L_range_x": np.max(lx) - np.min(lx), 
        "L_range_y": np.max(ly) - np.min(ly), 
        "Asimmetria": asymmetry_index(), 
        "R_area": confidence_ellipse(rx, ry),
        "L_area": confidence_ellipse(lx, ly), 

        "global_path" : path(gx, gy),
        "sway_ml": np.std(gx),
        "sway_ap": np.std(gy),
        "velocity": mean_vel(gx,gy),
        "Area": confidence_ellipse(gx, gy),

    }

    # loop per estrarre le features da tutti i pazienti
    results = []

    for pz in patients_C:
        res = compute_features(df_C, pz)
        res["Group"] = "Control"
        results.append(res)

    for pz in patients_PD:
        res = compute_features(df_PD, pz)
        res["Group"] = "PD"
        results.append(res)

    df_features = pd.DataFrame(results)

    ## PULIZIA ID PAZIENTI  e INTEGRAZIONI FILE ANAGRAFICI##

    df_features["Subject ID"] = df_features["Subject ID"].astype(str).str.strip().str.upper().str.replace(" ", "")
    Dem_C["Subject ID"] = Dem_C["Subject ID"].astype(str).str.strip().str.upper().str.replace(" ", "")
    Dem_PD["Subject ID"] = Dem_PD["Subject ID"].astype(str).str.strip().str.upper().str.replace(" ", "")

    Dem_all = pd.concat([Dem_C, Dem_PD])
    df_final = df_features.merge(Dem_all, on="Subject ID", how="left")

    return df_final 


#scegli una tipologia di task

df_final = dataset_analysis("Task_6C.csv", "Task_6PD.csv") 

df_final.to_csv("T6_eyes_open_Lfoot_forward1.csv", index=False)

