import pandas as pd
import streamlit as st
import random

# Βήματα 7 & 8: Έλεγχος Ποιοτικών Χαρακτηριστικών & Διορθώσεις

def step7_8_quality_check(df, num_classes):
    st.subheader("🔍 Έλεγχος Ποιοτικών Χαρακτηριστικών")
    characteristics = ["ΦΥΛΟ", "ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ", "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ"]
    for char in characteristics:
        value_counts = {}
        for i in range(num_classes):
            class_id = f'T{i+1}'
            class_df = df[df['ΤΜΗΜΑ'] == class_id]
            count_N = (class_df[char] == 'Ν').sum()
            value_counts[class_id] = count_N

        max_diff = max(value_counts.values()) - min(value_counts.values())
        if max_diff > 3:
            st.warning(f"⚠️ Απόκλιση >3 στη στήλη '{char}': {value_counts}")

    return df

# Πίνακας Στατιστικών Ανά Τμήμα

def show_statistics_table(df, num_classes):
    summary = []
    for i in range(num_classes):
        class_id = f'T{i+1}'
        class_df = df[df['ΤΜΗΜΑ'] == class_id]
        total = class_df.shape[0]
        stats = {
            "ΤΜΗΜΑ": class_id,
            "Α (Αγόρια)": (class_df["ΦΥΛΟ"] == "Α").sum(),
            "Κ (Κορίτσια)": (class_df["ΦΥΛΟ"] == "Κ").sum(),
            "Παιδιά Εκπαιδευτικών (Ν)": (class_df["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν").sum(),
            "Ζωηροί (Ν)": (class_df["ΖΩΗΡΟΣ"] == "Ν").sum(),
            "Ιδιαιτερότητα (Ν)": (class_df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν").sum(),
            "Καλή Γνώση Ελληνικών (Ν)": (class_df["ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"] == "Ν").sum(),
            "Ικανοποιητική Μαθησιακή Ικανότητα (Ν)": (class_df["ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ"] == "Ν").sum(),
            "ΣΥΝΟΛΟ": total
        }
        summary.append(stats)

    stats_df = pd.DataFrame(summary)
    st.subheader("📊 Πίνακας Στατιστικών Ανά Τμήμα")
    st.dataframe(stats_df)

    if st.button("📤 Εξαγωγή Πίνακα Στατιστικών σε Excel"):
        output = pd.ExcelWriter("katanomi_output.xlsx", engine='xlsxwriter')
        df.to_excel(output, sheet_name='Κατανομή', index=False)
        stats_df.to_excel(output, sheet_name='Στατιστικά', index=False)
        output.close()
        with open("katanomi_output.xlsx", "rb") as f:
            st.download_button("⬇️ Λήψη Excel", data=f, file_name="katanomi_output.xlsx")

# --- Κλήση της συνάρτησης στα βήματα ---
# df = step7_8_quality_check(df, num_classes)
# show_statistics_table(df, num_classes)
