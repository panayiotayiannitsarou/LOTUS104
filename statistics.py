
import pandas as pd
import streamlit as st

# ✅ Βήματα 7 & 8: Έλεγχος Ποιοτικών Χαρακτηριστικών

def step7_8_quality_check(df, num_classes):
    st.subheader("🔍 Έλεγχος Ποιοτικών Χαρακτηριστικών")
    characteristics = ["ΦΥΛΟ", "ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ", "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ"]
    for char in characteristics:
        value_counts = {}
        for i in range(num_classes):
            class_id = f'Α{i+1}'  # ✅ changed from T{i+1}
            class_df = df[df['ΤΜΗΜΑ'] == class_id]
            count_N = (class_df[char] == 'Ν').sum()
            value_counts[class_id] = count_N

        max_diff = max(value_counts.values()) - min(value_counts.values())
        if max_diff > 3:
            st.warning(f"⚠️ Απόκλιση >3 στη στήλη '{char}': {value_counts}")

    return df

# ✅ Πίνακας Στατιστικών Ανά Τμήμα

def show_statistics_table(df, num_classes):
    summary = []
    for i in range(num_classes):
        class_id = f'Α{i+1}'  # ✅ changed from T{i+1}
        class_df = df[df['ΤΜΗΜΑ'] == class_id]
        total = class_df.shape[0]
        stats = {
            "ΤΜΗΜΑ": class_id,
            "Α (Αγόρια)": (class_df.get("ΦΥΛΟ", "") == "Α").sum(),
            "Κ (Κορίτσια)": (class_df.get("ΦΥΛΟ", "") == "Κ").sum(),
            "Παιδιά Εκπαιδευτικών (Ν)": (class_df.get("ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ", "") == "Ν").sum(),
            "Ζωηροί (Ν)": (class_df.get("ΖΩΗΡΟΣ", "") == "Ν").sum(),
            "Ιδιαιτερότητα (Ν)": (class_df.get("ΙΔΙΑΙΤΕΡΟΤΗΤΑ", "") == "Ν").sum(),
            "Καλή Γνώση Ελληνικών (Ν)": (class_df.get("ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ", "") == "Ν").sum(),
            "Ικανοποιητική Μαθησιακή Ικανότητα (Ν)": (class_df.get("ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ", "") == "Ν").sum(),
            "ΣΥΝΟΛΟ": total
        }
        summary.append(stats)

    stats_df = pd.DataFrame(summary)
    st.subheader("📊 Πίνακας Στατιστικών Ανά Τμήμα")
    st.dataframe(stats_df)
