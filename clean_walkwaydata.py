import pandas as pd
import numpy as np


# df_walk = pd.read_csv(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset\PKMAS Walkway Gait Metrics - HP+SP.csv")  
# df_demo_PD = pd.read_csv(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset\PD - Demographic+Clinical - datasetV1.csv")
# df_demo_contr = pd.read_csv(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset\CONTROLS - Demographic+Clinical - datasetV1.csv")

df_demo_controls = pd.read_excel(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset_xlsx\CONTROLS - Demographic+Clinical - datasetV1_mike.xlsx") 
df_demo_controls.columns = [c.replace(' ', '_') for c in df_demo_controls.columns]
df_demo_controls.rename(columns= {'Age_(years)':'Age'}, inplace=True)
df_demo_controls.to_excel(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset_xlsx\CONTROLS - Demographic+Clinical - datasetV1_mike.xlsx")

df_demo_PD = pd.read_excel(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset_xlsx\PD - Demographic+Clinical - datasetV1_mike.xlsx")
df_demo_PD.columns = [c.replace(' ', '_') for c in df_demo_PD.columns]
df_demo_PD.rename(columns= {'Age_(years)':'Age'}, inplace=True)
df_demo_PD.to_excel(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset_xlsx\PD - Demographic+Clinical - datasetV1_mike.xlsx")

df_walk = pd.read_excel(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset_xlsx\PKMAS Walkway Gait Metrics - HP+SP_mike.xlsx")
df_walk.columns = [c.replace(' ', '_') for c in df_walk.columns]



df_walk.insert(3, 'Age', np.zeros(df_walk['Participant_ID'].size))
df_walk.insert(4, 'Height', np.zeros(df_walk['Participant_ID'].size))
df_walk.insert(5, 'Weight', np.zeros(df_walk['Participant_ID'].size))
df_walk.insert(6, 'Sex', np.zeros(df_walk['Participant_ID'].size))


subset_PD = df_demo_PD[['Subject_ID', 'Height_(in)', 'Age', 'Weight_(kg)', 'Sex']]
subset_PD.dropna()
subset_controls = df_demo_controls[['Subject_ID', 'Height_(in)', 'Age', 'Weight_(kg)', 'Sex']]
subset_controls.dropna()


for row in df_walk.index:
    if df_walk.at[row, 'PD_vs_Control'] == 'PD':
        for rowcheck in subset_PD.index:
            if df_walk.at[row, 'Participant_ID'] == subset_PD.at[rowcheck, 'Subject_ID']:
                df_walk.at[row, 'Height'] = subset_PD.at[rowcheck, 'Height_(in)']
                df_walk.at[row, 'Age'] = subset_PD.at[rowcheck, 'Age']
                df_walk.at[row, 'Weight'] = subset_PD.at[rowcheck, 'Weight_(kg)']
                df_walk.at[row, 'Sex'] = subset_PD.at[rowcheck, 'Sex']
    else:
        for rowcheck in subset_controls.index:
            if df_walk.at[row, 'Participant_ID'] == subset_controls.at[rowcheck, 'Subject_ID']:
                df_walk.at[row, 'Height'] = subset_controls.at[rowcheck, 'Height_(in)']
                df_walk.at[row, 'Age'] = subset_controls.at[rowcheck, 'Age']
                df_walk.at[row, 'Weight'] = subset_controls.at[rowcheck, 'Weight_(kg)']
                df_walk.at[row, 'Sex'] = subset_controls.at[rowcheck, 'Sex']           


#df_walk.set_index('Participant_ID',inplace=True)

df_walk.to_excel(r"C:\Users\miche\Desktop\uni\ing_clinica_progetto\dataset_xlsx\walkway_e_demografiche_mike.xlsx")




 



