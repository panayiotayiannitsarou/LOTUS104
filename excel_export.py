
import pandas as pd
from io import BytesIO

def convert_multiple_dfs_to_excel(scenario_dfs, best_df):
    """
    Δημιουργεί Excel με μία γραμμή ανά μαθητή και στήλες για κάθε ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_X + τελικό ΤΜΗΜΑ.

    :param scenario_dfs: λίστα από DataFrames (ένα ανά σενάριο, με ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_X)
    :param best_df: DataFrame με το καλύτερο σενάριο (στήλη ΤΜΗΜΑ)
    :return: BytesIO με Excel αρχείο
    """
    # Ξεκινάμε με βασικό πίνακα (χωρίς τις στήλες ΤΜΗΜΑ_x)
    base_cols = [col for col in best_df.columns if not col.startswith("ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_") and col != "ΤΜΗΜΑ"]
    merged_df = best_df[base_cols].copy()

    # Προσθήκη στήλες ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_Χ
    for i, scenario_df in enumerate(scenario_dfs):
        col_name = f"ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_{i+1}"
        if col_name in scenario_df.columns:
            merged_df[col_name] = scenario_df[col_name]

    # Προσθήκη της τελικής στήλης ΤΜΗΜΑ (από το best_df)
    merged_df["ΤΜΗΜΑ"] = best_df["ΤΜΗΜΑ"]

    # Εξαγωγή σε Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        merged_df.to_excel(writer, index=False, sheet_name="Σενάρια & Τελικό")

    output.seek(0)
    return output
