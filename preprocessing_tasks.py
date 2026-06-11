import pandas as pd
import numpy as np
import os

# --- PARAMETRI ---
DURATION = 10
folder = "file_PD"
FS = 100

common_time = np.round(
    np.arange(0, DURATION + 1/FS, 1/FS),
    2
)

final_df = pd.DataFrame({"Time_s": common_time})

def align_nearest(df, col, t_common):

    t = df["Time"].values 
    x = df[col].values 
    idx = np.searchsorted(t, t_common) 

    idx = np.clip(idx, 1, len(t) - 1) 

    left = idx - 1 
    right = idx

    choose_left = np.abs(t_common - t[left]) < np.abs(t_common - t[right])

    idx_final = np.where(choose_left, left, right)

    return x[idx_final]


# --- PROCESS FILE ---
def process_file(filepath, n):

    df = pd.read_csv(filepath)

    required_cols = ["Time", 
                     "L Foot Pressure", "R Foot Pressure" , "Walkway_X" , "Walkway_Y" , "WalkwayPressureLevel",
                     "LPressure1", "LPressure2", "LPressure3", "LPressure4", "LPressure5","LPressure6" , "LPressure7" , "LPressure8" , "LPressure9" , "LPressure10" , "LPressure11" , "LPressure12" , "LPressure13" , "LPressure14" , "LPressure15" , "LPressure16",
                     "LCoP_X", "LCoP_Y", 
                     "RPressure1", "RPressure2", "RPressure3", "RPressure4", "RPressure5","RPressure6" , "RPressure7" , "RPressure8" , "RPressure9" , "RPressure10" , "RPressure11" , "RPressure12" , "RPressure13" , "RPressure14" , "RPressure15" , "RPressure16",
                     "RCoP_X", "RCoP_Y"
                     ]

    if not all(col in df.columns for col in required_cols):
        return None

    df["Time"] = df["Time"].astype(str).str.replace(" sec", "").astype(float)

    mask_event = [(df["GeneralEvent"] == "EO_FeetShoWidth"),
                  (df["GeneralEvent"] == "EC_FeetShoWidth"),
                  (df["GeneralEvent"] == "EO_FeetTogether"),
                  (df["GeneralEvent"] == "EC_FeetTogether"),
                  (df["GeneralEvent"] == "EO_RFootFront"),
                  (df["GeneralEvent"] == "EO_LFootFront")]

    

    # contatto con la pedana (Walkway_X non nullo)
    mask_walkway = df["Walkway_X"].notna()

    # maschera combinata
    mask = mask_walkway & mask_event[n]

    # trova dove iniziano i blocchi
    starts = mask & ~mask.shift(fill_value=False)

    start_indices = df.index[starts].tolist()

    if len(start_indices) < 1:
        start_idx = None
    else:
        start_idx = start_indices[0]  # prendo il primo blocco valido

    df = df.loc[start_idx:].copy()

    start_time = df["Time"].iloc[0]+1
    end_time = start_time + DURATION

    df = df[(df["Time"] >= start_time) & (df["Time"] <= end_time)]

    df["Time"] -= start_time

    return df

# --- LOOP FILE ---
scartati = []
for file in os.listdir(folder):

    if not file.endswith(".csv"):
        continue

    path = os.path.join(folder, file)
    df = process_file(path, n=0)  # n indica quale evento cercare (0-5)

    #---file scartati---

    if df is None:
            scartati.append(file)
            continue

    name = file.replace(".csv", "")

    # --- STRINGHE ---

    final_df[f"{name}_LPressure"] = align_nearest(df, "L Foot Pressure", common_time)
    final_df[f"{name}_RPressure"] = align_nearest(df, "R Foot Pressure", common_time)   
    final_df[f"{name}_WalkwayPressureLevel"]=align_nearest(df, "WalkwayPressureLevel", common_time)
    
    final_df[f"{name}_Walkway_X"] = align_nearest(df, "Walkway_X", common_time)
    final_df[f"{name}_Walkway_Y"] = align_nearest(df, "Walkway_Y", common_time)

    final_df[f"{name}_Foot"] = align_nearest(df, "WalkwayFoot", common_time)

    # --- NUMERICI ---
    for i in range(1, 17):
        final_df[f"{name}_LP{i}"] = align_nearest(df, f"LPressure{i}", common_time)

    final_df[f"{name}_LCOPX"] = align_nearest(df, "LCoP_X", common_time)
    final_df[f"{name}_LCOPY"] = align_nearest(df, "LCoP_Y", common_time)

    for i in range(1, 17): 
        final_df[f"{name}_RP{i}"] = align_nearest(df, f"RPressure{i}", common_time)

    final_df[f"{name}_RCOPX"] = align_nearest(df, "RCoP_X", common_time)
    final_df[f"{name}_RCOPY"] = align_nearest(df, "RCoP_Y", common_time)


# --- SALVATAGGIO ---
final_df.to_csv("_Task_1PD.csv", index=False)

# --- REPORT FILE SCARTATI ---
print("\n===== FILE SCARTATI =====")
print(f"Numero file scartati: {len(scartati)}")

if len(scartati) > 0:
    for f in scartati:
        print(f"- {f}")