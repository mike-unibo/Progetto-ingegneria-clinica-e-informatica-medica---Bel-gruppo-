import streamlit as st
from scipy import stats


def esegui_test(grp_pd, grp_ctrl, label):
    if len(grp_pd) < 3 or len(grp_ctrl) < 3:
        st.warning("Dati insufficienti per eseguire i test statistici.")
        return

    _, p_shapiro_pd   = stats.shapiro(grp_pd)
    _, p_shapiro_ctrl = stats.shapiro(grp_ctrl)

    normale_pd   = p_shapiro_pd   > 0.05
    normale_ctrl = p_shapiro_ctrl > 0.05
    all_normal   = normale_pd and normale_ctrl

    # Chiave di sessione per ricordare quale test è attivo per questa metrica
    key = f"test_attivo_{label}"
    if key not in st.session_state:
        st.session_state[key] = None

    # Callback: impostano lo stato prima del rerun
    def _set_ttest():
        st.session_state[key] = "ttest"

    def _set_mwu():
        st.session_state[key] = "mwu"

    with st.expander(f"Test statistici · {label}"):

        # Shapiro-Wilk
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

        if all_normal:
            st.success("Entrambi i gruppi sono normali → si consiglia **Student's t-test (Welch)**")
        else:
            st.warning("Almeno un gruppo non è normale → si consiglia **Mann–Whitney U test**")

        # Bottoni con stile primario/secondario in base allo stato
        st.markdown("##### Visualizza risultato:")
        btn_col1, btn_col2 = st.columns(2)

        btn_col1.button(
            "Student's t-test (Welch)",
            use_container_width = True,
            type                = "primary" if st.session_state[key] == "ttest" else "secondary",
            key                 = f"btn_ttest_{label}",
            on_click            = _set_ttest,
        )
        btn_col2.button(
            "Mann–Whitney U test",
            use_container_width = True,
            type                = "primary" if st.session_state[key] == "mwu" else "secondary",
            key                 = f"btn_mwu_{label}",
            on_click            = _set_mwu,
        )

        # Risultati
        if st.session_state[key] == "ttest":
            t_stat, t_p = stats.ttest_ind(grp_pd, grp_ctrl, equal_var=False)
            r1, r2, r3 = st.columns(3)
            r1.metric("t-statistic (PD − Controlli)", f"{t_stat:.4f}")
            r2.metric("p-value", f"{t_p:.10f}")
            with r3:
                if t_p < 0.05:
                    st.success("Significativo (p < 0.05)")
                else:
                    st.info("Non significativo")

        if st.session_state[key] == "mwu":
            u_stat, u_p = stats.mannwhitneyu(grp_pd, grp_ctrl, alternative="two-sided")
            r1, r2, r3 = st.columns(3)
            r1.metric("U-statistic", f"{u_stat:.4f}")
            r2.metric("p-value", f"{u_p:.10f}")
            with r3:
                if u_p < 0.05:
                    st.success("Significativo (p < 0.05)")
                else:
                    st.info("Non significativo")