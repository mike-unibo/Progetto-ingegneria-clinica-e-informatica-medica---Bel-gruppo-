import pandas as pd
from xml.dom import minidom
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition
from fhir.resources.observation import Observation  #importo le classi corrispondenti a risorse fhir che servono
from fhir.resources.bundle import Bundle
from fhir.resources.codesystem import CodeSystem
from fhir.resources.conceptmap import ConceptMap


#leggo i due dataset come dataframes pandas, imposto come colonna indici quella degli id soggetto
PD = pd.read_excel(r"dataset\PD - Demographic+Clinical - datasetV1_mike.xlsx")
PD.set_index('Subject_ID',inplace=True)

controls = pd.read_excel(r"dataset\CONTROLS - Demographic+Clinical - datasetV1_mike.xlsx")
controls.set_index('Subject_ID',inplace=True)

walk = pd.read_excel(r"dataset\walkway_e_demografiche_mike.xlsx")
walk.set_index('Participant_ID', inplace=True)

bal_eo = pd.read_excel(r"dataset\T1_eyes_open_feet_shoulder.xlsx")
bal_eo.set_index("Subject ID", inplace=True)

bal_ec = pd.read_excel(r"dataset\T2_eyes_close_feet_shoulder.xlsx")
bal_ec.set_index("Subject ID", inplace=True)

bal_eoc = pd.read_excel(r"dataset\T3_eyes_open_feet_together.xlsx")
bal_eoc.set_index("Subject ID", inplace=True)

bal_ecc = pd.read_excel(r"dataset\T4_eyes_close_feet_together.xlsx")
bal_ecc.set_index("Subject ID", inplace=True)

bal_rff = pd.read_excel(r"dataset\T5_eyes_open_Rfoot_forward.xlsx")
bal_rff.set_index("Subject ID", inplace=True)

bal_lff = pd.read_excel(r"dataset\T6_eyes_open_Lfoot_forward.xlsx")
bal_lff.set_index("Subject ID", inplace=True)

disp = {"Stazione eretta — occhi aperti, piedi alla larghezza delle spalle":" COP sway: eyes open wide stance", 
        "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle":" COP sway: eyes closed wide stance",
        "Stazione eretta — occhi aperti, piedi uniti":" COP sway: eyes open narrow stance",
        "Stazione eretta — occhi chiusi, piedi uniti":" COP sway: eyes closed narrow stance",
        "Stazione eretta — occhi aperti, tallone dx davanti a punta sx":" COP sway: eyes open right-foot tandem stance",
        "Stazione eretta — occhi aperti, tallone sx davanti a punta dx":" COP sway: eyes open left-foot tandem stance"}

codes = {"Stazione eretta — occhi aperti, piedi alla larghezza delle spalle":["LOC-BAL-SWAY-AP-EO-WIDE", "LOC-BAL-SWAY-ML-EO-WIDE", "LOC-BAL-ELL95-EO-WIDE", "LOC-BAL-COPV-EO-WIDE"], 
        "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle":["LOC-BAL-SWAY-AP-EC-WIDE", "LOC-BAL-SWAY-ML-EC-WIDE", "LOC-BAL-ELL95-EC-WIDE", "LOC-BAL-COPV-EC-WIDE"],
        "Stazione eretta — occhi aperti, piedi uniti":["LOC-BAL-SWAY-AP-EO-NARR", "LOC-BAL-SWAY-ML-EO-NARR", "LOC-BAL-ELL95-EO-NARR", "LOC-BAL-COPV-EO-NARR"],
        "Stazione eretta — occhi chiusi, piedi uniti":["LOC-BAL-SWAY-AP-EC-NARR", "LOC-BAL-SWAY-ML-EC-NARR", "LOC-BAL-ELL95-EC-NARR", "LOC-BAL-COPV-EC-NARR"],
        "Stazione eretta — occhi aperti, tallone dx davanti a punta sx":["LOC-BAL-SWAY-AP-EO-RTAND", "LOC-BAL-SWAY-ML-EO-RTAND", "LOC-BAL-ELL95-EO-RTAND", "LOC-BAL-COPV-EO-RTAND"],
        "Stazione eretta — occhi aperti, tallone sx davanti a punta dx":["LOC-BAL-SWAY-AP-EO-LTAND", "LOC-BAL-SWAY-ML-EO-RTAND", "LOC-BAL-ELL95-EO-LTAND", "LOC-BAL-COPV-EO-LTAND"]}

PD_list = ['NLS139','NLS140','NLS056','NLS124',
        'NLS035','NLS069','NLS189','NLS190',
        'NLS191','NLS192','NLS101','NLS194',
        'NLS195','NLS196','NLS033','NLS197',
        'NLS198','NLS201','NLS208','NLS209',
        'NLS210','NLS211','WPD012','WPD013',
        'WPD014','WPD015','WPD016','WPD017',
        'WPD018','WPD019','WPD020','WPD021',
        'WPD022','WPD023','WPD024','WPD025',
        'WPD026','WPD027','WPD029','NLS127',
        'NLS177','NLS179','NLS182','NLS183',
        'NLS184','NLS185','NLS186','NLS187',
        'NLS188','WPD002','WPD003','WPD004',
        'WPD005','WPD006','WPD007','WPD008',
        'WPD009','WPD010','WPD011','NLS002',
        'NLS005','NLS022','NLS036','NLS102',
        'NLS121','NLS130','NLS135','NLS141',
        'NLS142','NLS143','NLS144','NLS146',
        'NLS147','NLS148','NLS149','NLS150',
        'NLS151','NLS152','NLS153','NLS154',
        'NLS155','NLS157','NLS158','NLS159',
        'NLS160','NLS161','NLS162','NLS163',
        'NLS164','NLS165','NLS166','NLS167',
        'NLS169','NLS170','NLS172','NLS173',
        'NLS174','NLS175','NLS176','WPD001'
        ]

C_list = ['NLS145', 'NLS193','NLS207','WHC015','WHC016',
        'WHC017','WHC018','WHC019','WHC020','WHC021',
        'WHC022','WHC024','WHC025','WHC026','WHC027',
        'WHC029','WHC030','WHC031','WHC032','WHC033',
        'HC124','HC125','HC126','HC127','HC128',
        'HC129','HC130','HC132','HC133','HC134',
        'HC135','HC136','HC137','HC138','HC139',
        'HC140','HC141','HC142','HC143','HC144',
        'HC145','HC147','HC148','HC149','HC150',
        'HC151','HC153','HC154','WHC007','WHC008',
        'WHC009','WHC010','WHC011','WHC012','WHC013',
        'WHC014','HC100','HC101','HC102','HC104',
        'HC103','HC105','HC106','HC108','HC107',
        'HC109','HC110','HC111','HC112','HC113',
        'HC114','HC115','HC116','HC117','HC118',
        'HC120','HC121','HC122','HC123','WHC001',
        'WHC002','WHC003','WHC004','WHC005','WHC006'
        ]

def serialize(resource, format_flag):
#Questa funzione prende in ingresso una risorsa fhir e il formato desiderato, e restituisce il file xml o json indentato correttamente

    if type(resource) == str or type(resource) == bool:
        return resource
    else:
        if format_flag == '.XML':
            xml_res = resource.model_dump_xml(pretty_print=True)
            parsed = minidom.parseString(xml_res)
            xml_res_pretty = parsed.toprettyxml(indent="  ")
            xml_res_pretty = "\n".join([line for line in xml_res_pretty.split("\n") if line.strip()])
            return xml_res_pretty
        
        elif format_flag == '.JSON':
            json_res = resource.model_dump_json(indent=2)
            return json_res 
        
        

def isPD(id_pat):
    #accetta come parametro un id paziente, restituisce 1 se è PD, 0 se è controls e 'err_pat_inex' se l'id è errato 
    if id_pat is None:
        id_pat = " "

    if id_pat.upper() in PD_list:
        return 1
    elif id_pat.upper() in C_list:
        return 0
    else:
        return 'err'

def overview(id_pat):
#questa funzione prende in ingresso l'id soggetto e restituisce una lista contenente i dati principali del soggetto

    if isPD(id_pat):
        df_ad = PD
        desc = "Punteggio Hoen e Yahr:"
        score = str(df_ad.at[id_pat, 'Modified _Hoehn_&_Yahr_Score'])+"/5"
    elif not isPD(id_pat):
        df_ad = controls
        desc = "Punteggio MoCa:"
        score = str(df_ad.at[id_pat, 'MoCA_Score'])+"/30"
    else:
        return 'err_pat_inex'
    

    sex = "Maschio" if df_ad.at[id_pat, 'Sex'].lower()=='male' else "Femmina"
    cond = " Malato di Parkinson " if isPD(id_pat) else " Sano (gruppo di controllo)"
    age = str(int(df_ad.at[id_pat, 'Age']))+" anni"

    return [desc, score, sex, cond, age]

def create_fhir_patient(id_pat):
#prendendo come parametro l'id soggetto, va a recuperare i dati disponibili nel dataset e li inserisce
#nei rispettivi campi della risorsa fhir 'paziente' che crea come oggetto fhir.resource


    if isPD(id_pat):
        df_ad = PD 
    elif not isPD(id_pat):
        df_ad = controls 
    else:
        return 'err_pat_inex'
    

    sex = df_ad.at[id_pat, 'Sex'].lower()
    
    patient = Patient(
        id = id_pat.upper(),
        gender = sex
        
    )
    return patient

def create_fhir_obs_age(id_pat):    
#prendendo come parametro l'id soggetto, va a recuperare i dati disponibili nel dataset e li inserisce
#nei rispettivi campi della risorsa fhir 'observation': età che crea come oggetto fhir.resource


    if isPD(id_pat):
        df_ad = PD 
    elif not isPD(id_pat):
        df_ad = controls 
    else:
        return 'err_pat_inex'
    

    age = df_ad.at[id_pat, 'Age']
    

    observation_age = Observation(
        status="final",
        id="obs-age",
        category= [{
            "coding": [{
                "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "survey",
            }],
        }],

        subject={"reference": f"Patient/{id_pat}"},
        code={"coding": [{      #è codeable concept, non stringa semplice
            "system": "http://loinc.org",
            "code": "30525-0",  #codice loinc per l'età
            "display": "Age"
            }]
        },

        valueQuantity={
            "value": str(age),
            "unit": "years",
            "system":"http://unitsofmeasure.org",
            "code":"a"
        }
    )
    return observation_age    

def create_fhir_condition(id_pat):
#prendendo come parametro l'id soggetto, va a recuperare i dati disponibili nel dataset e li inserisce
#nei rispettivi campi della risorsa fhir 'condition' che crea come oggetto fhir.resource
        

    if isPD(id_pat):
        c = "Parkinson's disease"
        code = "32798002"    #codice snomed per il Parkinson
    elif not isPD(id_pat):
        c = 'Control subject (Healthy)'
        code = None

    else:
        return 'err_pat_inex'
    
    condition = Condition(
        clinicalStatus={"coding": [{ 
            "system":"http://terminology.hl7.org/CodeSystem/condition-clinical",    #è un codeable concept, non stringa semplice
            "code": "active",
            },]
        },
        subject={"reference": f"Patient/{id_pat}"},
        code={"coding":[{        #è un codeable concept, non stringa semplice
                "system": "http://snomed.info/sct" if code else None,  
                "code": code,
                "display": c
        }]},

    )

    return condition 

def create_fhir_obs_MoCa(id_pat):
#prendendo come parametro l'id soggetto, va a recuperare i dati disponibili nel dataset e li inserisce
#nei rispettivi campi della risorsa fhir 'observation': moca score che crea come oggetto fhir.resource

    if isPD(id_pat):
        return "moca_inex_park"
    elif not isPD(id_pat):
        df_ad = controls
    else:
        return 'err_pat_inex'
    
    
    score = df_ad.at[id_pat, 'MoCA_Score']
    if pd.isna(score) or score=='-':
        return 'moca_ndisp'
    else:
        observation_moca = Observation(
            status="final",
            id="obs-MoCa",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],

            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "72172-0",
                "display": "Total score [MoCA]"
            }]}, 

            valueQuantity={
                "value": str(score),
                "unit": "{score}",
                "system":"http://unitsofmeasure.org",
                "code":"{score}"
            }
        )
    
    return observation_moca

def create_fhir_obs_HY(id_pat):
#prendendo come parametro l'id soggetto, va a recuperare i dati disponibili nel dataset e li inserisce
#nei rispettivi campi della risorsa fhir 'observation': Hoen e Yahr che crea come oggetto fhir.resource

    if isPD(id_pat):
        df_ad = PD
    elif not isPD(id_pat):
        return "HY_inex_contr"
    else:
        return 'err_pat_inex'
    
    
    score = df_ad.at[id_pat, 'Modified _Hoehn_&_Yahr_Score']

    if pd.isna(score) or score=='-':
        return 'HY_ndisp'
    else:
        observation_HY = Observation(
            status="final",
            id="obs-HoenYahr",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],  

            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "77714-4",
                "display": "Modified Hoen and Yahr stage [UPDRS]"
            }]},    

            valueQuantity={
                "code": "stage "+str(score),
            }
        )
    
    return observation_HY

def create_fhir_obs_MDS_UPDRS_1(id_pat):
#prendendo come parametro l'id soggetto, va a recuperare i dati disponibili nel dataset e li inserisce
#nei rispettivi campi della risorsa fhir 'observation': UPDRS I che crea come oggetto fhir.resource

    if isPD(id_pat):        
        df_ad = PD
    elif not isPD(id_pat):
        df_ad = controls
    else:
        return 'err_pat_inex'
    

    part1 = df_ad.loc[id_pat, "COGNITIVE_IMPAIRMENT":"FATIGUE"].drop("Daily_Living_Questions") #slicing dataframe
    c = pd.to_numeric(part1, errors='coerce').sum() #somma punteggi del updrs, se non sono presenti nel database (-) li conta come zeri
    if "-" in part1.values:      #se il punteggio di una sezione intera è zero, significa che quella sezione non è disponibile per quel soggetto
        return False
    else:
        observation_UPDRS1 = Observation(
            status="final",
            id="obs-UPDRS1",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "77718-5",                        
                "display": "Mentation, Behavior and Mood panel [UPDRS]"
                }]},      

                valueQuantity={
                    "value": str(c),
                    "unit": "{score}",
                    "system":"http://unitsofmeasure.org",
                    "code":"{score}"
                }
            )   
         
    return (c, observation_UPDRS1)  

def create_fhir_obs_MDS_UPDRS_2(id_pat):

    if isPD(id_pat):        
        df_ad = PD
    elif not isPD(id_pat):
        df_ad = controls
    else:
        return 'err_pat_inex'
    

    part2 = df_ad.loc[id_pat, "SPEECH":"FREEZING"]
    c = pd.to_numeric(part2, errors='coerce').sum()
    if "-" in part2.values:
        return False
    else:
        observation_UPDRS2 = Observation(
            status="final",
            id="obs-UPDRS2",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],

            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "77719-3",                        
                "display": "Activities of Daily Living panel [UPDRS]"
                }]},    

            valueQuantity={
                "value": str(c),
                "unit": "{score}",
                "system":"http://unitsofmeasure.org",
                "code":"{score}"
            }
        )
    
    return (c, observation_UPDRS2)
    
def create_fhir_obs_MDS_UPDRS_3(id_pat):

    if isPD(id_pat):        #a seconda che il soggetto sia PD o meno, apre il corrispondente dataset
        df_ad = PD
    elif not isPD(id_pat):
        df_ad = controls
    else:
        return 'err_pat_inex'
    

    part3 = df_ad.loc[id_pat,"SPEECH_1":"CONSTANCY_OF_REST_TREMOR"]
    c = pd.to_numeric(part3, errors='coerce').sum()
    if "-" in part3.values:
        return False
    else:
        observation_UPDRS3 = Observation(
            status="final",
            id="obs-UPDRS3",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],

            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "77720-1",                        
                "display": "Motor Examination panel [UPDRS]"
                }]},    

            valueQuantity={
                "value": str(c),
                "unit": "{score}",
                "system":"http://unitsofmeasure.org",
                "code":"{score}"
            }
        )
    
    return (c, observation_UPDRS3)

def create_fhir_obs_MDS_UPDRS_4(id_pat):

    if isPD(id_pat):        #a seconda che il soggetto sia PD o meno, apre il corrispondente dataset
        df_ad = PD
    elif not isPD(id_pat):
        df_ad = controls
    else:
        return 'err_pat_inex'
    

    part4 = df_ad.loc[id_pat, "TIME_SPENT_WITH_DYSKINESIAS":"PAINFUL_OFF-STATE_DYSTONIA"]
    c = pd.to_numeric(part4, errors='coerce').sum()
    if "-" in part4.values:
        return False
    else:
        observation_UPDRS4 = Observation(
            status="final",
            id="obs-UPDRS4",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],

            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "77722-7",                        
                "display": "Dyskinesia panel [UPDRS]"
                }]},    

            valueQuantity={
                "value": str(c),
                "unit": "{score}",
                "system":"http://unitsofmeasure.org",
                "code":"{score}"
            }
        )
    
    return (c, observation_UPDRS4)

def create_fhir_obs_MDS_UPDRS_tot(id_pat):


    if isPD(id_pat) == 'err':
        return 'err_pat_inex'    
    else:    
        a = create_fhir_obs_MDS_UPDRS_1(id_pat)
        b = create_fhir_obs_MDS_UPDRS_2(id_pat)
        c = create_fhir_obs_MDS_UPDRS_3(id_pat)
        d = create_fhir_obs_MDS_UPDRS_4(id_pat)
    

    if not (a and b and c and d):
        return "err_tot_NA"
    else:
        t = create_fhir_obs_MDS_UPDRS_1(id_pat)[0] + create_fhir_obs_MDS_UPDRS_2(id_pat)[0] + create_fhir_obs_MDS_UPDRS_3(id_pat)[0] + create_fhir_obs_MDS_UPDRS_4(id_pat)[0]

        observation_UPDRStot= Observation(
            status="final",
            id="obs-UPDRStot",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                }],
            }],

            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system": "http://loinc.org",
                "code": "77717-7",
                "display": "Unified Parkinson's Disease Rating Scale (UPDRS)"
            }]},        

            valueQuantity={
                "value": str(t),
                "unit": "{score}",
                "system":"http://unitsofmeasure.org",
                "code":"{score}"
            }
        )

    return (t, observation_UPDRStot)

def create_fhir_bundle(entries, clin):

    bu = Bundle(
        id="bundle-clinical" if clin else "bundle-biomechanics",
        type='collection',
        entry=entries
    )

    return bu

def create_fhir_gait_velocity(id_pat):

    if (id_pat not in walk.index) or (walk.at[id_pat, 'Velocity_(cm./sec.)'].size < 2):
        return 'err_metric_NA'
    else:
        vself = round(float((walk.at[id_pat, 'Velocity_(cm./sec.)']).iloc[1]/10), 2)
        vhur = round(float((walk.at[id_pat, 'Velocity_(cm./sec.)']).iloc[0]/10), 2)

        observation_vel_self = Observation(
            status="final",
            id="obs-gaitspeed-sp",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code":"LOC-GAIT-SPD-SELF",
                "display":"Mean gait speed: self-paced walk",
                }],        
            },
            valueQuantity={
                "value": str(vself),
                "unit": "meter per second",
                "system":"http://unitsofmeasure.org",
                "code":"m/s"
            
            }
        )

        observation_vel_hur = Observation(
            status="final",
            id="obs-gaitspeed-hp",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                    "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                    "code":"LOC-GAIT-SPD-HUR",
                    "display":"Mean gait speed: hurried-pace walk",
                }],        
            },
            valueQuantity={
                "value": str(vhur),
                "unit": "meter per second",
                "system":"http://unitsofmeasure.org",
                "code":"m/s"
            
            }
        
        ) 

    return [vself, observation_vel_self, vhur, observation_vel_hur]

def create_fhir_stride_width(id_pat):

    if (id_pat not in walk.index) or (walk.at[id_pat, 'Stride_Width_(cm.).1'].size < 2):
        return 'err_metric_NA'
    else:
        swself = round(float((walk.at[id_pat, 'Stride_Width_(cm.).1']).iloc[1]),2)
        swhur = round(float((walk.at[id_pat, 'Stride_Width_(cm.).1']).iloc[0]),2)

        observation_stridew_self = Observation(
            status="final",
            id="obs-stridewidth-sp",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code":"LOC-GAIT-SW-SELF",
                "display":"Mean stride width: self-paced walk",
                }],
            },
            valueQuantity={
                "value": str(swself),
                "unit": "centimeter",
                "system":"http://unitsofmeasure.org",
                "code":"cm"
            }
        )

        observation_stridew_hur = Observation(
            status="final",
            id="obs-stridewidth-hp",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code":"LOC-GAIT-SW-HURR",
                "display":"Mean stride width: hurried-paced walk",
                }],
            },
            valueQuantity={
                "value": str(swself),
                "unit": "centimeter",
                "system":"http://unitsofmeasure.org",
                "code":"cm"
            }
        ) 

    return [swself, observation_stridew_self, swhur, observation_stridew_hur]

def create_fhir_sway(id_pat, task):
    
    match task:
        case "Stazione eretta — occhi aperti, piedi alla larghezza delle spalle":
            df_ad = bal_eo
        case "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle":
            df_ad = bal_ec
        case "Stazione eretta — occhi aperti, piedi uniti":
            df_ad = bal_eoc
        case "Stazione eretta — occhi chiusi, piedi uniti":
            df_ad = bal_ecc
        case "Stazione eretta — occhi aperti, tallone dx davanti a punta sx":
            df_ad = bal_rff
        case "Stazione eretta — occhi aperti, tallone sx davanti a punta dx":
            df_ad = bal_lff
    
    if (id_pat not in df_ad.index) or (df_ad.at[id_pat, "Invalid"]):
        return "err_metric_NA"
    else:
        sway_ap = round(df_ad.at[id_pat, "sway_ap"], 2)
        sway_ml = round(df_ad.at[id_pat, "sway_ml"], 2)

        observation_sway_ap = Observation(
            status="final",
            id="obs-sway-ap",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],            
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code": codes[task][0],
                "display":f"Anteroposterior {disp[task]}",
                }],
            },
            valueQuantity={
                "value": str(sway_ap),
                "unit": "centimeter",
                "system":"http://unitsofmeasure.org",
                "code":"cm"
            }
        )

        observation_sway_ml = Observation(
            status="final",
            id="obs-swayml",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],            
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code": codes[task][1],
                "display":f"Mediolateral {disp[task]}",
                }],
            },
            valueQuantity={
                "value": str(sway_ap),
                "unit": "centimeter",
                "system":"http://unitsofmeasure.org",
                "code":"cm"
            }
        ) 

    return [sway_ap, observation_sway_ap, sway_ml, observation_sway_ml]

def create_fhir_ellipse95(id_pat, task):
    
    match task:
        case "Stazione eretta — occhi aperti, piedi alla larghezza delle spalle":
            df_ad = bal_eo
        case "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle":
            df_ad = bal_ec
        case "Stazione eretta — occhi aperti, piedi uniti":
            df_ad = bal_eoc
        case "Stazione eretta — occhi chiusi, piedi uniti":
            df_ad = bal_ecc
        case "Stazione eretta — occhi aperti, tallone dx davanti a punta sx":
            df_ad = bal_rff
        case "Stazione eretta — occhi aperti, tallone sx davanti a punta dx":
            df_ad = bal_lff
    
    if (id_pat not in df_ad.index) or (df_ad.at[id_pat, "Invalid"]):
        return "err_metric_NA"
    else:
        area = round(df_ad.at[id_pat, "Area"], 2)

        observation_ell95 = Observation(
            status="final",
            id="obs-95confidenceCOPellipse",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],            
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code": codes[task][2],
                "display":f"95% confidence ellipse COP area: {disp[task]}",
                }],
            },
            valueQuantity={
                "value": str(area),
                "unit": "square centimeter",
                "system":"http://unitsofmeasure.org",
                "code":"cm2"
            }
        ) 

    return [area, observation_ell95]

def create_fhir_copvel(id_pat, task):
    
    match task:
        case "Stazione eretta — occhi aperti, piedi alla larghezza delle spalle":
            df_ad = bal_eo
        case "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle":
            df_ad = bal_ec
        case "Stazione eretta — occhi aperti, piedi uniti":
            df_ad = bal_eoc
        case "Stazione eretta — occhi chiusi, piedi uniti":
            df_ad = bal_ecc
        case "Stazione eretta — occhi aperti, tallone dx davanti a punta sx":
            df_ad = bal_rff
        case "Stazione eretta — occhi aperti, tallone sx davanti a punta dx":
            df_ad = bal_lff
    
    if (id_pat not in df_ad.index) or (df_ad.at[id_pat, "Invalid"]):
        return "err_metric_NA"
    else:
        vel = round(df_ad.at[id_pat, "velocity"], 2)

        observation_vel = Observation(
            status="final",
            id="obs-COPvelocity",
            category= [{
                "coding": [{
                    "system":"http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "activity",
                }],
            }],            
            subject={"reference": f"Patient/{id_pat}"},
            code={"coding": [{
                "system":"https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
                "code": codes[task][3],
                "display":f"Mean COP velocity: {disp[task]}",
                }],
            },
            valueQuantity={
                "value": str(vel),
                "unit": "centimeter per second",
                "system":"http://unitsofmeasure.org",
                "code":"cm/s"
            }
        ) 

    return [vel, observation_vel]        


cs = pd.read_excel(r"dataset\codesystem_biomech.xlsx", dtype={"target_code": str}, skiprows=range(1,6))
cs["target_code"].replace("nan", "")
cs.set_index("metric", inplace=True)

def create_fhir_codesystem():

    CODE_SYSTEM = CodeSystem(
        url="https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
        version="1.0",
        name="BiomechanicalMetricsWeargaitPD",
        status="active",
        content="complete",
        concept=[{
            "code":cs.at[m, "local_code"].strip(),
            "display":cs.at[m, "display"],
            "definition":cs.at[m, "definition"] if pd.notna(cs.at[m, "definition"]) else None
        } for m in cs.index]
    
    )
    return CODE_SYSTEM


def create_fhir_conceptmap():

    CONCEPT_MAP = ConceptMap(

        url="https://infom.lab.unibo.it/fhir/ConceptMap/weargait-biomechanics",
        version="1.0",
        status="active",
        sourceScopeUri="https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
        targetScopeUri="http://snomed.info/sct",
        group= [{
            "source": "https://infom.lab.unibo.it/fhir/CodeSystem/weargait-biomechanics",
            "target": "http://snomed.info/sct",
            "element": [{
                "code": cs.at[m, "local_code"].strip(),
                "target": [{
                    "code": str(cs.at[m, "target_code"]) if pd.notna(cs.at[m, "target_code"]) else None,
                    "relationship": cs.at[m, "equivalence"],
                    "comment":cs.at[m, "comment"].strip() if pd.notna(cs.at[m, "comment"]) else None
                }]
            } for m in cs.index]
        }]
    )    
  
    return CONCEPT_MAP




