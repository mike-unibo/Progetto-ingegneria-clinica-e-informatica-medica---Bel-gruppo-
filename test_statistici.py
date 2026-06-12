import streamlit as st
from scipy import stats

# Funzione riutilizzabile: riceve i due gruppi (PD e controlli) come array
# e una label di testo usata per il titolo dell'expander e per rendere unica la chiave del widget.
def esegui_test(grp_pd, grp_ctrl, label):
    # Shapiro-Wilk richiede almeno 3 osservazioni per gruppo
    if len(grp_pd) < 3 or len(grp_ctrl) < 3:
        st.warning("Dati insufficienti per eseguire i test statistici.")
        return

    # Test di normalità di Shapiro-Wilk su entrambi i gruppi
    _, p_shapiro_pd   = stats.shapiro(grp_pd)
    _, p_shapiro_ctrl = stats.shapiro(grp_ctrl)

    # p > 0.05: non si rifiuta l'ipotesi nulla di normalità
    normale_pd   = p_shapiro_pd   > 0.05
    normale_ctrl = p_shapiro_ctrl > 0.05
    all_normal   = normale_pd and normale_ctrl

    with st.expander(f"Test statistici · {label}"):

        # Risultati Shapiro-Wilk mostrati come metriche 
        c1, c2 = st.columns(2)
        c1.metric(
            label       = "Shapiro-Wilk PD",
            value       = f"p = {p_shapiro_pd:.4f}",
            delta       = "Normale" if normale_pd else "Non normale",
            delta_color = "normal" if normale_pd else "inverse",
        )
        c2.metric(
            label       = "Shapiro-Wilk Controls",
            value       = f"p = {p_shapiro_ctrl:.4f}",
            delta       = "Normale" if normale_ctrl else "Non normale",
            delta_color = "normal" if normale_ctrl else "inverse",
        )

        # Il test suggerito dipende dall'esito della normalità:
        # se entrambi i gruppi sono normali si usa il t-test di Welch (non assume varianze uguali),
        # altrimenti il Mann-Whitney U, che è non parametrico e lavora sui ranghi.
        if all_normal:
            st.success("Entrambi i gruppi sono normali → si consiglia **Student's t-test (Welch)**")
            default_test = "Student's t-test (Welch)"
        else:
            st.warning("Almeno un gruppo non è normale → si consiglia **Mann-Whitney U test**")
            default_test = "Mann-Whitney U test"

        # Selezione del test tramite controllo segmentato
        st.markdown("##### Visualizza risultato:")
        test = st.segmented_control(
            "Test",
            ["Student's t-test (Welch)", "Mann-Whitney U test"],
            default          = default_test,
            width            = "stretch",
            label_visibility = "collapsed",
            key              = f"test_seg_{label}",  # chiave univoca per evitare conflitti tra più istanze
        )

        # Risultati del test selezionato
        if test == "Student's t-test (Welch)":
            # equal_var=False: variante di Welch, robusta a campioni con varianze diverse
            t_stat, t_p = stats.ttest_ind(grp_pd, grp_ctrl, equal_var=False)
            r1, r2, r3 = st.columns(3)
            r1.metric("t-statistic (PD - Controlli)", f"{t_stat:.4f}")
            r2.metric("p-value", f"{t_p:.10f}")
            with r3:
                if t_p < 0.05:
                    st.success("Significativo (p < 0.05)")
                else:
                    st.info("Non significativo")

        elif test == "Mann-Whitney U test":
            # alternative="two-sided": ipotesi nulla che le due distribuzioni siano identiche
            u_stat, u_p = stats.mannwhitneyu(grp_pd, grp_ctrl, alternative="two-sided")
            r1, r2, r3 = st.columns(3)
            r1.metric("U-statistic", f"{u_stat:.4f}")
            r2.metric("p-value", f"{u_p:.10f}")
            with r3:
                if u_p < 0.05:
                    st.success("Significativo (p < 0.05)")
                else:
                    st.info("Non significativo")