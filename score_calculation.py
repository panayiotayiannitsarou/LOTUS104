# 🔁 Εκτέλεση Εναλλακτικών Σεναρίων Κατανομής
# Αν στο Βήμα 1 δημιουργηθούν πολλαπλά έγκυρα σενάρια για την τοποθέτηση των παιδιών εκπαιδευτικών, τότε:
# • Για κάθε σενάριο ξεχωριστά, εκτελούνται αυτόνομα τα Βήματα 2 έως 7.
# • Η μόνη διαφορά μεταξύ των σεναρίων είναι η κατανομή των παιδιών εκπαιδευτικών (Βήμα 1).
# • Όλα τα υπόλοιπα βήματα εφαρμόζονται κανονικά και ανεξάρτητα για κάθε διαφορετικό σενάριο.

import streamlit as st
import pandas as pd
import math
from io import BytesIO
from step1_senarios import step1_katanomi_paidia_ekpaideutikon
from step2 import step2_zoiroi
from step3 import step3_idiaiterotites
from step4 import step4_amivaia_filia
from step5 import step5_filikoi_omades
from step6 import step6_ypolipoi_xwris_filies
from step7 import step7_telikes_diorthoseis
from score import calculate_score  # ✅ Εισαγωγή score

# ➕ Ενδεικτική ροή εκτέλεσης για όλα τα σενάρια

def apply_all_steps_for_senario(df, num_classes):
    df = step2_zoiroi(df, num_classes)
    df = step3_idiaiterotites(df, num_classes)
    df = step4_amivaia_filia(df)
    df = step5_filikoi_omades(df, num_classes)
    df = step6_ypolipoi_xwris_filies(df, num_classes)
    df = step7_telikes_diorthoseis(df, num_classes)
    return df

uploaded_file = st.file_uploader("⬆️ Μεταφόρτωση Excel Μαθητών", type=[".xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    num_classes = st.number_input("📌 Πόσα τμήματα;", min_value=2, max_value=10, step=1)

    if st.button("🏁 Τελική Κατανομή"):
        scenarios = step1_katanomi_paidia_ekpaideutikon(df.copy(), num_classes)
        final_scenario_dfs = []
        scores = []

        for i, scenario_df in enumerate(scenarios):
            scenario_df = apply_all_steps_for_senario(scenario_df.copy(), num_classes)
            score = calculate_score(scenario_df, num_classes)
            scenario_df["SCORE"] = score
            scores.append(score)
            final_scenario_dfs.append(scenario_df)

        best_index = None
        best_score = float('inf')
        for i, s in enumerate(scores):
            if s < best_score:
                best_score = s
                best_index = i

        if best_index is not None:
            best_df = final_scenario_dfs[best_index]
            st.session_state["best_df"] = best_df  # ✅ Αποθήκευση
            st.session_state["scores"] = scores
            st.session_state["all_scenarios"] = final_scenario_dfs

            st.success(f"🏆 Προτεινόμενο Σενάριο: {best_index+1} με Score {best_score}")

            for c in range(num_classes):
                tmima_df = best_df[best_df['ΤΜΗΜΑ'] == f'Α{c+1}']
                st.markdown(f"**Τμήμα Α{c+1}**")
                st.dataframe(tmima_df[['ΟΝΟΜΑ', 'ΦΥΛΟ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ']])

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                best_df.to_excel(writer, index=False, sheet_name='Τελική Κατανομή')
            st.download_button("📥 Κατέβασε Τελική Κατανομή (Excel)", data=output.getvalue(), file_name="teliki_katanomi.xlsx")

    if st.button("📚 Κατέβασε Όλα τα Σενάρια (Excel)"):
        # ✅ Αν έχουν ήδη αποθηκευτεί, μην τα υπολογίσεις ξανά
        if "all_scenarios" in st.session_state and "scores" in st.session_state:
            final_scenario_dfs = st.session_state["all_scenarios"]
            scores = st.session_state["scores"]
        else:
            scenarios = step1_katanomi_paidia_ekpaideutikon(df.copy(), num_classes)
            final_scenario_dfs = []
            scores = []
            for i, scenario_df in enumerate(scenarios):
                scenario_df = apply_all_steps_for_senario(scenario_df.copy(), num_classes)
                score = calculate_score(scenario_df, num_classes)
                scenario_df["SCORE"] = score
                scores.append(score)
                final_scenario_dfs.append(scenario_df)

        all_output = BytesIO()
        with pd.ExcelWriter(all_output, engine='xlsxwriter') as writer:
            for i, df_s in enumerate(final_scenario_dfs):
                df_s.to_excel(writer, index=False, sheet_name=f"Σενάριο_{i+1}")
            summary = pd.DataFrame({"Σενάριο": [f"Σενάριο_{i+1}" for i in range(len(scores))], "Score": scores})
            summary.to_excel(writer, index=False, sheet_name="Scores_Overview")
        st.download_button("📥 Κατέβασε Όλα τα Σενάρια (Excel)", data=all_output.getvalue(), file_name="ola_ta_senaria.xlsx")
