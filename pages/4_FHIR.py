import streamlit as st
import utilsm as u
from utilsm import PD_list, C_list   #importo le funzioni che ho scritto per generare le risorse e le liste contenenti gli id soggetto divisi in PD e controls
import time



def wait():
    st.session_state["generated"] = False

def select_all_biomec():
    for k in keys_biomec:
        st.session_state[k] = st.session_state["tutti_b"]

def select_all_clin():
    for k in keys_clinical:
        st.session_state[k] = st.session_state["tutti_c"]

def genera():
    with st.spinner("Recupero informazioni dal database..."):
        time.sleep(1.5)
    st.session_state["generated"] = True


if "generated" not in st.session_state:
    st.session_state["generated"] = False      #setto a falso i session state che mi servono per gestire i click del pulsante "genera risorse" e dei checkbox
if "tutti_c" not in st.session_state:
    st.session_state["tutti_c"] = False
if "tutti_b" not in st.session_state:
    st.session_state["tutti_b"] = False


st.set_page_config(page_title="WearGait-PD · FHIR resource builder",  layout='wide', page_icon="icon.png")

st.title('Mapping FHIR', text_alignment="center")

st.markdown('''Questa sezione permette di generare risorse FHIR contenenti metriche presenti all'interno del dataset weargait PD, mappate 
            tramite vocabolario LOINC e SNOMED (dove possibile) e CodeSystem locale.''')
st.badge("Per le risorse relative a variabili biomeccaniche sono stati utilizzati codici locali documentati all'interno del Code System biomeccanico", color='yellow')
st.page_link(r"pages\codesystem.py", label="Vai a Informazioni CodeSystem locale ->", icon=':material/dataset:', icon_position='right')
st.markdown('''E' sufficiente inserire l'ID del soggetto a cui si è interessati e spuntare le caselle sulle risorse che si vogliono generare: \
            l'applicazione restituirà le risorse conformi FHIR  nel formato selezionato, permettendone anche il download.''')
#st.header("", divider="violet")
st.markdown("<hr style='border-top: 3px solid #A024A7; margin-top: -5px;'>", unsafe_allow_html=True)


with st.sidebar:    #mostra la tendina di selezione del soggetto
    
    condd = {"Entrambi":PD_list+C_list, "PD":PD_list, "Controls":C_list}
    st.markdown("Inserisci ID soggetto di cui vuoi creare una o più risorse FHIR:")
    cond = st.radio("Mostra nella tendina:", (condd.keys()), index=0, on_change=wait)  #filtro per la tendina di selezione soggetto per visualizzare PD, controls o entrambi
    id = st.selectbox(" ", (condd[cond]), index=None, placeholder='Inserisci un ID paziente', label_visibility="collapsed", on_change=wait)   #tendina di selezione soggetto
    format = st.selectbox('Inserisci il formato in cui ti serve la risorsa: ', ('.JSON','.XML'))

if id:  #mostra un'overview dei dati del soggetto scelto e le tre risorse base: patient, condition, obs_age
    
    desc, score, sex, cond, age = u.overview(id)    
    st.markdown(f"Riepilogo informazioni relative al soggetto selezionato: :blue-badge[ID {id}]")

    with st.container(border=True):
        with st.container(horizontal=True, border=False):
            st.metric("Sesso:", sex, border=True)
            st.metric("Condizione:", cond, border=True)
            st.metric("Età:", age, border=True)
            st.metric(desc, score, border=True)

        with st.container(border=False):
            st.markdown(f"Risorse generali relative al soggetto selezionato: :blue-badge[ID {id}]")
            tab1, tab2, tab3 = st.tabs(['Preview risorsa "PATIENT"',  
                                        'Preview risorsa "CONDITION"', 
                                        'Preview risorsa "OBSERVATION: AGE"', 
                                        ])
        

            with tab1:
                r = u.serialize(u.create_fhir_patient(id), format)
                st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                if format==".XML":
                    st.code(r,language=format.lower()[1:])  
                else:
                    st.json(r)
                g = st.download_button(label='Scarica risorsa '+format, data=r, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Patient'+format, icon=":material/download:", key=0)

            with tab2:
                r1 = u.serialize(u.create_fhir_condition(id), format)
                st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                if format==".XML":
                    st.code(r1,language=format.lower()[1:])  
                else:
                    st.json(r1)
                st.download_button(label='Scarica risorsa '+format, data=r1, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Condition'+format, icon=":material/download:", key=1)
                
            with tab3:
                r2 = u.serialize(u.create_fhir_obs_age(id), format)
                st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                if format==".XML":
                    st.code(r2,language=format.lower()[1:])  
                else:
                    st.json(r2)            
                st.download_button(label='Scarica risorsa '+format, data=r2, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_Age'+format, icon=":material/download:", key=2)

if u.isPD(id) == 'err':
    st.markdown("<- Seleziona un ID soggetto dalla barra laterale") 
else:    
    with st.sidebar:

        st.markdown("Seleziona le variabili presenti nel database da mappare all'interno di risorse FHIR per il soggetto "+id.upper())
        

        #checkbox delle variabili clinche
        with st.container(border=True):
            keys_clinical = ["moca_on","HY_on","UPDRS_on"]
            for k in keys_clinical:
                if k not in st.session_state:
                    st.session_state[k] = False
            
            
            st.markdown("Variabili cliniche :material/Stethoscope_Check:")
            moca_on = st.checkbox('Punteggio test MoCa', label_visibility="visible", help="Il punteggio MoCa è disponibile nel database solo per alcuni dei soggetti di controllo (sani)", key=keys_clinical[0])
            HY_on = st.checkbox('Punteggio scala Hoen & Yahr', label_visibility="visible", help="Il punteggio Hoen & Yahr è disponibile soltanto per alcuni dei soggetti malati di Parkinson", key=keys_clinical[1])
            UPDRS_on = st.checkbox('Punteggio scala MDS-UPDRS', label_visibility="visible", help="Il punteggio MDS-UPDRS è disponibile soltanto per alcuni  dei soggetti, sani e malati", key=keys_clinical[2])
            st.divider()
            tutti_clinical = st.checkbox("Seleziona tutte le variabili cliniche", key="tutti_c", on_change=select_all_clin) #permette di far funzionare il checkbox "seleziona tutti" per spuntare effettivamente tutte le altre

            bundle_clinical_on = st.toggle("Genera anche risorsa Bundle variabili cliniche", label_visibility="visible", help='''Una risorsa Bundle comprende più risorse FHIR al suo interno,  
                                        in questo caso conterrà quelle disponibili tra le selezionate in precedenza''')
            entries=[]
            entries.append({"resource":u.create_fhir_patient(id)})
            entries.append({"resource":u.create_fhir_condition(id)})
            entries.append({"resource":u.create_fhir_obs_age(id)})

        
        #checkbox delle variabili biomeccaniche
        with st.container(border=True):
            keys_biomec = ["gaitv_on", "stepvar_on", "sway_on", "ell_on", "copv_on"]
            for k in keys_biomec:
                if k not in st.session_state:
                    st.session_state[k] = False

            st.markdown("Variabili biomeccaniche :material/Person_Play:")
            st.markdown("Task di cammino: :material/Directions_walk:", help='''Le metriche relative a parametri del passo sono calcolate dalla pedana sensorizzata utilizzata  
                        per le acquisizioni dei task self pace e hurried pace su alcuni dei soggetti, sani e malati.  
                        :small[https://www.synapse.org/Synapse:syn52540892/wiki/629567]''')
            gaitv_on = st.checkbox('Velocità media globale del passo', key=keys_biomec[0])
            stridew_on = st.checkbox("Larghezza media della base d'appoggio", key=keys_biomec[1])
            st.markdown("Task di balance: :material/Footprint:", help='''Le metriche relative ai parametri di equilibrio sono calcolate a partire da algoritmi di signal processing  
                        applicati ai dati della pedana sensorizzata usata nelle acquisizioni dei task di equilibrio su alcuni soggetti, sani e malati.  
                        :small[https://www.synapse.org/Synapse:syn52540892/wiki/629567]''')
            task = st.selectbox("Seleziona task:", ["Stazione eretta — occhi aperti, piedi alla larghezza delle spalle", 
                                                    "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle",
                                                    "Stazione eretta — occhi aperti, piedi uniti", 
                                                    "Stazione eretta — occhi chiusi, piedi uniti", 
                                                    "Stazione eretta — occhi aperti, tallone dx davanti a punta sx", 
                                                    "Stazione eretta — occhi aperti, tallone sx davanti a punta dx"], index=0)
            sway_on = st.checkbox('Sway (oscillazione) del COP', key=keys_biomec[2])
            ell_on = st.checkbox(r"Area dell'ellisse di confidenza al 95% del COP", label_visibility="visible", key=keys_biomec[3])
            copv_on = st.checkbox('Velocità media del COP', label_visibility="visible", key=keys_biomec[4])
            st.divider()
            tutti_biomec = st.checkbox("Seleziona tutte le variabili biomeccaniche", key="tutti_b", on_change=select_all_biomec) #permette di far funzionare il checkbox "seleziona tutti" per spuntare effettivamente tutte le altre

            bundle_biomec_on = st.toggle("Genera anche risorsa Bundle variabili biomeccaniche", label_visibility="visible", help='''Una risorsa Bundle comprende più risorse FHIR al suo interno,  
                                         in questo caso conterrà quelle disponibili tra le selezionate in precedenza''')
            entriesb=[]
            entriesb.append({"resource":u.create_fhir_patient(id)})
            entriesb.append({"resource":u.create_fhir_condition(id)})
            entriesb.append({"resource":u.create_fhir_obs_age(id)})



        st.button('Genera le risorse selezionate relative al soggetto '+id, icon=':material/clinical_notes:', on_click=genera)   #al click del pulsante "genera risorse" il valore di session state generated va a true


try:
    x = moca_on
except NameError:
    st.session_state.generated=False

if st.session_state.generated:    #se il session state generated è true (premuto il pulsante "genera") genera e mostra le risorse
    

#In base ai checkbox selezionati, creo le risorse chiamando le rispettive funzioni e le impagina, permettendo il download. 
#Se un dato non è disponibile viene visualizzato un warning che ne spiega il motivo

#tabs contenenti le risorse relative a variabili cliniche

    with st.expander("Risorse relative alle variabili cliniche", expanded=True):

        tab4, tab5, tab6, tab7 = st.tabs([
                                        'Preview risorsa "OBSERVATION: MoCa SCORE"', 
                                        'Preview risorsa "OBSERVATION: Hoen e Yahr SCORE"', 
                                        'Preview risorsa "MDS-UPDRS"', 
                                        'Preview risorsa "Bundle variabili cliniche"'])


        if moca_on:
            with tab4:
                r3 = u.serialize(u.create_fhir_obs_MoCa(id), format)
                if r3 == 'moca_inex_park':
                    st.warning("MoCa score non disponibile: l'ID inserito corrisponde ad un soggetto malato di Parkinson's")
                elif r3 == 'moca_ndisp':
                    st.error("MoCa score non disponibile nel database per questo soggetto")
                else:
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":u.create_fhir_obs_MoCa(id)})
                    if format==".XML":
                        st.code(r3,language=format.lower()[1:])  
                    else:
                        st.json(r3)
                    st.download_button(label='Scarica risorsa '+format, data=r3, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_MoCa'+format, icon=":material/download:", key=3)
                
                st.divider()
                with st.expander("Vedi spiegazione"):
                            st.write('''
                            Il Montreal Cognitive Assessment (MoCA) è un test di screening rapido (circa 10-15 minuti) 
                            per individuare il lieve deficit cognitivo (MCI) e declino cognitivo. Il punteggio totale è di 30 punti, con un punteggio 
                            considerato normale. Un punteggio di 25 o inferiore indica un potenziale declino. In questo studio è stato
                            effettuato solo su alcuni dei soggetti di controllo (sani).''')
                            st.image("https://otfocus.com/wp-content/uploads/2023/03/Online-MOCA-testing-services-to-screen-dementia-and-cognition-1024x570.jpeg", width=380)
                            st.markdown(''':small[immagine: https://otfocus.com/online-moca-testing-services-to-screen-dementia-and-cognition/
                                        info: https://otfocus.com/the-best-cognition-assessments-for-ot-that-are-quick/]''')
        else:
            with tab4:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')

        if HY_on:
            with tab5:
                r4 = u.serialize(u.create_fhir_obs_HY(id), format)
                if r4 == 'HY_inex_contr':
                    st.warning("Hoehn Yahr score non disponibile: l'ID inserito corrisponde ad un soggetto di controllo (sano)")
                elif r4 == 'HY_ndisp':
                    st.error("Hoehn Yahr score non disponibile nel database per questo soggetto")
                else:
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":u.create_fhir_obs_HY(id)})
                    if format==".XML":
                        st.code(r4,language=format.lower()[1:])  
                    else:
                        st.json(r4)
                    st.download_button(label='Scarica risorsa '+format, data=r4, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_HY'+format, icon=":material/download:", key=4)
                
                st.divider()
                with st.expander("Vedi spiegazione"):
                            st.write('''
                            La scala di Hoehn e Yahr è un sistema classico utilizzato per classificare la progressione della malattia 
                            di Parkinson in 5 stadi, basandosi sulla gravità dei sintomi motori e sulla compromissione funzionale. 
                            Va da 1 (malattia lieve/unilaterale) a 5 (confinamento a letto o sedia a rotelle), spesso utilizzata con stadi intermedi (1.5, 2.5).
                            In questo studio è stato effettuato solo su alcuni dei soggetti.  ''')
                            st.image("https://medrac.web.unc.edu/wp-content/uploads/sites/22579/2025/08/Untitled-presentation.png", width=380)
                            st.markdown(''':small[immagine: https://medrac.web.unc.edu/tag/deep-brain-stimulation/
                                        info: https://www.neuropsychology.it/voce_glossario.asp?idglossario=5]''')
        else:
            with tab5:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')

        if UPDRS_on:
            with tab6:
                if not u.isPD(id):
                    st.warning("Il soggetto selezionato non ha una diagnosi di Parkinson, ma è stato comunque sottoposto alla valutazione MDS-UPDRS in modo da " \
                    "poter paragonare eventuali sue criticità con un paziente.")
                st.divider()     
                r5 = u.create_fhir_obs_MDS_UPDRS_1(id)
                
                if r5 == False:
                        st.error(f"Punteggio del test MDS-UPDRS per la sezione 1: Mentation, Behavior and Mood non disponibile nel dataset per questo soggetto")
                else:
                    res = u.serialize(r5[1], format)
                    st.metric("punteggio totalizzato nella sezione 1:  Mentation, Behavior and Mood",  f"{int(r5[0])}/52")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":r5[1]})
                    if format==".XML":
                        st.code(res,language=format.lower()[1:])  
                    else:
                        st.json(res)
                    st.download_button(label='Scarica risorsa '+format, data=res, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_MDS_UPDRS_I'+format, icon=":material/download:", key=5)

                st.divider()
                r6 = u.create_fhir_obs_MDS_UPDRS_2(id)

                if r6 == False:
                        st.error(f"Punteggio del test MDS-UPDRS per la sezione 2: Activities of Daily Living non disponibile nel dataset per questo soggetto")
                else:
                    res = u.serialize(r6[1], format)
                    st.metric("punteggio totalizzato nella sezione 2: Activities of Daily Living",  f"{int(r6[0])}/52")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":r6[1]})
                    if format==".XML":
                        st.code(res,language=format.lower()[1:])  
                    else:
                        st.json(res)
                    st.download_button(label='Scarica risorsa '+format, data=res, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_MDS_UPDRS_II'+format, icon=":material/download:", key=6)            

                st.divider()
                r7 = u.create_fhir_obs_MDS_UPDRS_3(id)

                if r7 == False:
                        st.error(f"Punteggio del test MDS-UPDRS per la sezione 3: Motor Examination non disponibile nel dataset per questo soggetto")
                else:
                    res = u.serialize(r7[1], format)
                    st.metric("punteggio totalizzato nella sezione 3: Motor Examination",  f"{int(r7[0])}/132")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":r7[1]})
                    if format==".XML":
                        st.code(res,language=format.lower()[1:])  
                    else:
                        st.json(res) 
                    st.download_button(label='Scarica risorsa '+format, data=res, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_MDS_UPDRS_III'+format, icon=":material/download:", key=7)

                st.divider()
                r8 = u.create_fhir_obs_MDS_UPDRS_4(id)

                if r8 == False:
                        st.error(f"Punteggio del test MDS-UPDRS per la sezione 4: Dyskinesias and Clinical Fluctuations non disponibile nel dataset per questo soggetto")
                else:
                    res = u.serialize(r8[1], format)
                    st.metric("punteggio totalizzato nella sezione 4: Dyskinesias and Clinical Fluctuations",  f"{int(r8[0])}/24")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":r8[1]})
                    if format==".XML":
                        st.code(res,language=format.lower()[1:])  
                    else:
                        st.json(res)
                    st.download_button(label='Scarica risorsa '+format, data=res, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_MDS_UPDRS_IV'+format, icon=":material/download:", key=8)

                st.divider()
                r9 = u.create_fhir_obs_MDS_UPDRS_tot(id)
                
                if r9 == 'err_tot_NA':
                        st.error(f"Punteggio del test MDS-UPDRS totale non disponibile nel dataset per questo soggetto: parti mancanti")
                else:
                    res = u.serialize(r9[1], format)
                    st.metric("punteggio totale della scala MDS-UPDRS: ",  f"{int(r9[0])}/260")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entries.append({"resource":r9[1]})
                    if format==".XML":
                        st.code(res, language=format.lower()[1:])  
                    else:
                        st.json(res)
                    st.download_button(label='Scarica risorsa '+format, data=res, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_MDS_UPDRS_tot'+format, icon=":material/download:", key=9)
            
                st.divider()
                with st.expander("Vedi spiegazione"):
                                    st.write('''
                                    La MDS-UPDRS (Movement Disorder Society – Unified Parkinson’s Disease Rating Scale) è una scala clinica utilizzata per valutare
                                    la gravità e la progressione della malattia di Parkinson. Comprende quattro parti dedicate agli aspetti non motori,
                                    alle attività della vita quotidiana, all’esame motorio e alle complicanze motorie. Ogni item viene valutato con un punteggio da 0 a 4, 
                                    dove 0 indica assenza di sintomi, 1 sintomi lievi, 2 moderati, 3 marcati e 4 severi.  ''')
                                    st.image("https://movementdisordersinpsychiatry.org/wp-content/uploads/2022/06/MDS-UPDRS_English-1-pdf.jpg", width=380)
                                    st.markdown(''':small[immagine: https://movementdisordersinpsychiatry.org/unified-parkinson-disease-rating-scale-updrs/
                                                info: https://pubmed.ncbi.nlm.nih.gov/17115387/]''')
        else:
            with tab6:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')

        if bundle_clinical_on:
            with tab7:
                r10 = u.serialize(u.create_fhir_bundle(entries, True), format)
                st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                if format==".XML":
                    st.code(r10, language=format.lower()[1:])  
                else:
                    st.json(r10)
                    st.download_button(label='Scarica risorsa '+format, data=r10, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_bundle'+format, icon=":material/download:", key=10)
        else:
            with tab7:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')
                    


#tabs contenenti le risorse relative a variabili biomeccaniche (gait e balance)
    with st.expander("Risorse relative alle variabili biomeccaniche", expanded=True):

        tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs(['Preview risorsa OBSERVATION: "Mean gait speed"', 
                                                        'Preview risorsa: OBSERVATION: "Stride width"', 
                                                        'Preview risorsa OBSERVATION: "Sway COP"', 
                                                        'Preview risorsa OBSERVATION: "Area ellipse 95%"', 
                                                        'Preview risorsa OBSERVATION: "Mean velocity COP"', 
                                                        'Preview risorsa "Bundle variabili biomeccaniche"' ])

        if gaitv_on:
            with tab8:
                r10 = u.create_fhir_gait_velocity(id)
                if r10 == 'err_metric_NA':
                    st.error("Velocità media del passo non disponibile nel dataset per questo soggetto")
                else:
                    res_self = u.serialize(r10[1], format)
                    st.metric("Velocità media del passo nella camminata self pace:",  f"{r10[0]} m/sec")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r10[1]})
                    if format==".XML":
                        st.code(res_self,language=format.lower()[1:])  
                    else:
                        st.json(res_self)
                    st.download_button(label='Scarica risorsa '+format, data=res_self, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_vel_self'+format, icon=":material/download:", key=11)

                    st.divider()
                    res_hur = u.serialize(r10[3], format)
                    st.metric("Velocità media del passo nella camminata hurried pace:",  f"{r10[2]} m/sec")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r10[3]})
                    if format==".XML":
                        st.code(res_hur,language=format.lower()[1:])  
                    else:
                        st.json(res_hur)
                    st.download_button(label='Scarica risorsa '+format, data=res_hur, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_vel_hur'+format, icon=":material/download:", key=12)

                st.divider()
                with st.expander("Vedi spiegazione"):
                                    st.write('''
                                    La gait speed (velocità del cammino) è uno dei principali indicatori quantitativi della funzione motoria nei pazienti 
                                                con malattia di Parkinson. Una riduzione della velocità di cammino è associata a bradicinesia, instabilità posturale, 
                                                maggiore rischio di cadute e perdita di autonomia funzionale. Per questo motivo viene spesso utilizzata nei task di gait analysis
                                                come biomarcatore della progressione della malattia e dell’efficacia dei trattamenti riabilitativi o farmacologici. 
                                                Diversi studi mostrano inoltre che la gait speed correla con equilibrio, funzione cognitiva e qualità della vita del paziente. ''')
                                    st.image("https://www.ncbi.nlm.nih.gov/books/NBK534115/bin/shufflinggait.jpg", width=380)
                                    st.markdown(''':small[immagine: https://www.ncbi.nlm.nih.gov/books/NBK534115/
                                                info: https://www.nature.com/articles/s41531-021-00171-0]''')        
        else:
            with tab8:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')

        if stridew_on:
            with tab9:
                r11 = u.create_fhir_stride_width(id)
                if r11 == 'err_metric_NA':
                    st.error("Larghezza della base d'appoggio durante il passo non disponibile nel dataset per questo soggetto")
                else:
                    res_self = u.serialize(r11[1], format)
                    st.metric("Larghezza media della base d'appoggio nella camminata self pace:",  f"{r11[0]} cm")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r11[1]})
                    if format==".XML":
                        st.code(res_self,language=format.lower()[1:])  
                    else:
                        st.json(res_self)
                    st.download_button(label='Scarica risorsa '+format, data=res_self, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_var_self'+format, icon=":material/download:", key=13)

                    st.divider()
                    res_hur = u.serialize(r11[3], format)
                    st.metric("Larghezza media della base d'appoggio nella camminata hurried pace:",  f"{r11[2]} cm")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r11[3]})
                    if format==".XML":
                        st.code(res_hur,language=format.lower()[1:])  
                    else:
                        st.json(res_hur)
                    st.download_button(label='Scarica risorsa '+format, data=res_hur, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_var_hur'+format, icon=":material/download:", key=14)

                st.divider()
                with st.expander("Vedi spiegazione"):
                                    st.write('''
                                    La stride width (larghezza del passo) rappresenta la distanza laterale tra i piedi durante il cammino ed è un
                                    importante parametro biomeccanico della stabilità locomotoria. Nei pazienti con malattia di Parkinson, alterazioni 
                                    della stride width possono riflettere deficit del controllo posturale e strategie compensatorie per mantenere 
                                    l’equilibrio durante la deambulazione. Una maggiore variabilità o un aumento anomalo della larghezza del passo sono 
                                    spesso associati a instabilità del gait, freezing of gait e aumentato rischio di cadute. Per questo motivo la stride 
                                    width viene frequentemente analizzata negli studi di gait analysis come indicatore quantitativo della compromissione 
                                    motoria e della progressione della malattia. ''')
                                    st.image("https://o.quizlet.com/8Yl12NYC0mDlprlfez8sWw.jpg", width=380)
                                    st.markdown(''':small[immagine: https://link.springer.com/chapter/10.1007/978-981-96-0586-6_3,  
                                                info: https://pmc.ncbi.nlm.nih.gov/articles/PMC12268306/]''')        
        else:
            with tab9:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')
                
        if sway_on:
            with tab10:
                r12 = u.create_fhir_sway(id, task)
                if r12 == 'err_metric_NA':
                    st.error("Sway del COP durante i task di equilibrio non disponibile nel dataset per questo soggetto")
                else:
                    res_ap = u.serialize(r12[1], format)
                    st.metric(f"Sway anteroposteriore del COP durante il task {task}:",  f"{r12[0]} cm")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r12[1]})
                    if format==".XML":
                        st.code(res_ap,language=format.lower()[1:])  
                    else:
                        st.json(res_ap)
                    st.download_button(label='Scarica risorsa '+format, data=res_ap, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_sway_ap'+format, icon=":material/download:", key=15)

                    st.divider()
                    res_ml = u.serialize(r12[3], format)
                    st.metric(f"Sway mediolaterale del COP durante il task {task}:",  f"{r12[2]} cm")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r12[3]})
                    if format==".XML":
                        st.code(res_ml,language=format.lower()[1:])  
                    else:
                        st.json(res_ml)
                    st.download_button(label='Scarica risorsa '+format, data=res_ml, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_sway_ml'+format, icon=":material/download:", key=16)

                st.divider()
                with st.expander("Vedi spiegazione"):
                                    st.write('''
                                    Il sway del Center of Pressure (COP sway) rappresenta l’oscillazione del centro di pressione durante il mantenimento
                                    della postura eretta ed è uno dei principali indicatori della stabilità posturale. Nei pazienti con malattia di Parkinson, 
                                    un aumento del COP sway è associato a deficit del controllo motorio, instabilità posturale e maggiore rischio di cadute. 
                                    L’analisi delle oscillazioni del COP, in particolare nelle direzioni antero-posteriore (AP) e medio-laterale (ML), 
                                    viene ampiamente utilizzata nella gait e balance analysis come biomarcatore quantitativo della compromissione motoria e 
                                    della progressione della malattia. ''')
                                    st.image("https://deborahapthorp.com/project/postural-sway/featured.jpg", width=380)
                                    st.markdown(''':small[immagine: https://www.deborahapthorp.com/project/postural-sway/,  
                                                info: https://pubmed.ncbi.nlm.nih.gov/29869975/]''')        
        else:
            with tab10:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')               
                                
        if ell_on:
            with tab11:
                r13 = u.create_fhir_ellipse95(id, task)
                if r13 == 'err_metric_NA':
                    st.error("Area dell'ellisse di confidenza del COP al 95% nei task di equilibrio non disponibile nel dataset per questo soggetto")
                else:
                    res_ell = u.serialize(r13[1], format)
                    st.metric(f"Area dell'ellisse di confidenza al 95% nel task {task}:",  f"{r13[0]} cm2")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r13[1]})
                    if format==".XML":
                        st.code(res_ell,language=format.lower()[1:])  
                    else:
                        st.json(res_ell)
                    st.download_button(label='Scarica risorsa '+format, data=res_ell, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_COP_ell_95'+format, icon=":material/download:", key=17)

                st.divider()
                with st.expander("Vedi spiegazione"):
                                    st.write(r'''
                                    L’area dell’ellisse di confidenza al 95% (95% Confidence Ellipse Area) è una misura biomeccanica utilizzata per quantificare
                                    la dispersione delle oscillazioni del Center of Pressure (COP) durante il mantenimento della postura. Essa rappresenta l’area dell’ellisse 
                                    che contiene il 95% dei punti della traiettoria del COP ed è considerata un indicatore sintetico della stabilità posturale. 
                                    Nei pazienti con malattia di Parkinson, valori elevati della confidence ellipse area sono associati a maggiore instabilità, peggior controllo 
                                    dell’equilibrio e aumentato rischio di cadute, rendendola una metrica frequentemente utilizzata negli studi di posturografia e gait analysis. ''')
                                    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxEz0tgMsFluNcI-XARISLmk_xQbkhsG3myg&s", width=380)
                                    st.markdown(''':small[immagine: https://www.researchgate.net/figure/Illustration-of-the-calculation-of-the-95-confidence-ellipse-The-feature-is-equal-to_fig1_356574189,  
                                                info: https://pubmed.ncbi.nlm.nih.gov/30118638/]''')        
        else:
            with tab11:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')

        if copv_on:
            with tab12:
                r14 = u.create_fhir_copvel(id, task)
                if r14 == 'err_metric_NA':
                    st.error("Velocità media di spostamento del COP nei task di equilibrio non disponibile nel dataset per questo soggetto")
                else:
                    res_copv = u.serialize(r14[1], format)
                    st.metric(f"Velocità media di spostamento del COP nel task {task}:",  f"{r14[0]} cm/sec")
                    st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                    entriesb.append({"resource":r14[1]})
                    if format==".XML":
                        st.code(res_copv,language=format.lower()[1:])  
                    else:
                        st.json(res_copv)
                    st.download_button(label='Scarica risorsa '+format, data=res_copv, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_Obs_COP_vel'+format, icon=":material/download:", key=18)

                st.divider()
                with st.expander("Vedi spiegazione"):
                                    st.write('''
                                    La velocità media del Center of Pressure (Mean COP Velocity) rappresenta la velocità media con cui il centro di pressione si sposta durante 
                                    il mantenimento della postura. È considerata uno degli indicatori più sensibili del controllo posturale, poiché riflette la quantità di 
                                    correzioni neuromuscolari necessarie per mantenere l’equilibrio. Nei pazienti con malattia di Parkinson, un aumento della velocità media del 
                                    COP è frequentemente associato a instabilità posturale, peggior controllo motorio e maggiore rischio di cadute. Per questo motivo viene 
                                    ampiamente utilizzata negli studi di posturografia e balance assessment come biomarcatore quantitativo della compromissione dell’equilibrio. ''')
                                    st.image("https://www.mdpi.com/jcm/jcm-15-02588/article_deploy/html/images/jcm-15-02588-g002.png", width=380)
                                    st.markdown(''':small[immagine: https://www.mdpi.com/2077-0383/15/7/2588,  
                                                info: https://pmc.ncbi.nlm.nih.gov/articles/PMC3412413/]''')        
        else:
            with tab12:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')

        if bundle_biomec_on:
            with tab13:
                r15 = u.serialize(u.create_fhir_bundle(entriesb, False), format)
                st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
                if format==".XML":
                    st.code(r15, language=format.lower()[1:])  
                else:
                    st.json(r15)
                    st.download_button(label='Scarica risorsa '+format, data=r15, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name=id.upper()+'_bundle_biomec'+format, icon=":material/download:", key=19)
        else:
            with tab13:
                st.badge('Non selezionata', icon=':material/checklist:', color='orange')         


