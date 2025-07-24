
import pandas as pd

def step6_ypolipoi_xwris_filies(df: pd.DataFrame, num_classes: int) -> pd.DataFrame:
    """
    Βήμα 6 – Κατανομή Υπολοίπων Μαθητών Χωρίς Φιλίες

    Τοποθετεί μαθητές που:
    - Δεν έχουν δηλώσει φίλους, ή
    - Έχουν μη αμοιβαίες φιλίες, ή
    - Δεν τοποθετήθηκαν στα προηγούμενα βήματα.

    Προτεραιότητες:
    1. Μικρότερος αριθμός μαθητών ανά τμήμα
    2. Ισορροπία φύλου (σε περίπτωση ισοπαλίας)

    :param df: DataFrame με όλους τους μαθητές
    :param num_classes: Συνολικός αριθμός τμημάτων
    :return: Ενημερωμένο df με τιμές στη στήλη "ΤΜΗΜΑ"
    """
    df = df.copy()
    df["ΦΙΛΟΙ"] = df["ΦΙΛΟΙ"].fillna("")
    unassigned = df[df["ΤΜΗΜΑ"].isna()]
    remaining_students = []

    for _, row in unassigned.iterrows():
        name = row["ΟΝΟΜΑ"]
        friends = [f.strip() for f in str(row["ΦΙΛΟΙ"]).split(",") if f.strip()]
        is_mutual = any(
            df[(df["ΟΝΟΜΑ"] == f) & (df["ΦΙΛΟΙ"].str.contains(name))].shape[0] > 0
            for f in friends
        )
        if not friends or not is_mutual:
            remaining_students.append(name)

    for name in remaining_students:
        gender = df.loc[df["ΟΝΟΜΑ"] == name, "ΦΥΛΟ"].values[0]
        counts = df["ΤΜΗΜΑ"].value_counts().to_dict()
        for i in range(1, num_classes + 1):
            counts.setdefault(f"A{i}", 0)
        min_val = min(counts.values())
        candidates = [k for k, v in counts.items() if v == min_val]

        best_class = None
        min_gender_diff = float("inf")

        for cls in candidates:
            cls_df = df[df["ΤΜΗΜΑ"] == cls]
            boys = (cls_df["ΦΥΛΟ"] == "Α").sum()
            girls = (cls_df["ΦΥΛΟ"] == "Κ").sum()
            future_boys = boys + (1 if gender == "Α" else 0)
            future_girls = girls + (1 if gender == "Κ" else 0)
            diff = abs(future_boys - future_girls)
            if diff < min_gender_diff:
                min_gender_diff = diff
                best_class = cls

        df.loc[df["ΟΝΟΜΑ"] == name, "ΤΜΗΜΑ"] = best_class

    return df
