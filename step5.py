
import pandas as pd
from collections import defaultdict
from itertools import combinations

def step5_filikoi_omades(df, num_classes):
    df = df.copy()
    df["ΟΜΑΔΑ"] = None

    # ---------------- Μέρος Α – Δημιουργία Ομάδων ----------------
    def is_fully_mutual_friend(row, df):
        friend = row["ΦΙΛΟΣ"]
        if pd.isna(friend):
            return False
        friend_row = df[df["ΟΝΟΜΑ"] == friend]
        if friend_row.empty:
            return False
        return friend_row.iloc[0]["ΦΙΛΟΣ"] == row["ΟΝΟΜΑ"]

    def form_groups(df):
        not_assigned = df[df["ΤΜΗΜΑ"].isna()].copy()
        groups = []
        assigned = set()

        for _, row in not_assigned.iterrows():
            name = row["ΟΝΟΜΑ"]
            if name in assigned or pd.isna(row["ΦΙΛΟΣ"]):
                continue
            friend = row["ΦΙΛΟΣ"]
            friend_row = df[df["ΟΝΟΜΑ"] == friend]
            if friend_row.empty or not is_fully_mutual_friend(row, df):
                continue
            if friend in assigned:
                continue
            group = {name, friend}

            # Δυνατότητα σχηματισμού τριάδας
            third = None
            for possible_third in not_assigned["ΟΝΟΜΑ"]:
                if possible_third in group or possible_third in assigned:
                    continue
                third_row = df[df["ΟΝΟΜΑ"] == possible_third].iloc[0]
                if (third_row["ΦΙΛΟΣ"] in group and
                    df[df["ΟΝΟΜΑ"] == third_row["ΦΙΛΟΣ"]].iloc[0]["ΦΙΛΟΣ"] == possible_third):
                    third = possible_third
                    break

            if third:
                group.add(third)

            groups.append(list(group))
            assigned.update(group)

        # Μονήρεις που δεν μπήκαν σε καμία ομάδα
        for name in not_assigned["ΟΝΟΜΑ"]:
            if name not in assigned:
                groups.append([name])
                assigned.add(name)

        return groups

    groups = form_groups(df)

    # Ανάθεση ΟΜΑΔΑ
    for i, group in enumerate(groups):
        for student in group:
            df.loc[df["ΟΝΟΜΑ"] == student, "ΟΜΑΔΑ"] = f"ΟΜΑΔΑ_{i+1}"

    # ---------------- Μέρος Α – Κατηγοριοποίηση Ομάδων ----------------
    categories = defaultdict(list)

    for group in groups:
        members = df[df["ΟΝΟΜΑ"].isin(group)]
        genders = members["ΦΥΛΟ"].unique()
        greek_levels = members["ΓΝΩΣΗ_ΕΛ"].unique()

        if len(genders) > 1:
            categories["Μικτού Φύλου"].append(group)
        elif len(greek_levels) > 1:
            if genders[0] == "Α":
                categories["Μικτής Γνώσης (Ομάδες Αγοριών)"].append(group)
            else:
                categories["Μικτής Γνώσης (Ομάδες Κοριτσιών)"].append(group)
        else:
            level = "Καλή Γνώση" if greek_levels[0] == "Ν" else "Όχι Καλή Γνώση"
            gender = "Αγόρια" if genders[0] == "Α" else "Κορίτσια"
            categories[f"{level} ({gender})"].append(group)

    # ---------------- Μέρος Β – Τοποθέτηση Ομάδων ----------------
    class_assignments = defaultdict(list)

    def count_category(df, category, cls):
        return sum([
            1 for student in class_assignments[cls]
            if df[df["ΟΝΟΜΑ"] == student]["ΟΜΑΔΑ"].values[0] in [
                df[df["ΟΝΟΜΑ"] == s]["ΟΜΑΔΑ"].values[0] for s in categories[category]
            ]
        ])

    for category, group_list in categories.items():
        for i, group in enumerate(group_list):
            # Υπολογισμός αριθμού ανά τμήμα
            counts = {cls: sum(df[df["ΟΝΟΜΑ"].isin(class_assignments[cls])]["ΟΜΑΔΑ"].isin([f"ΟΜΑΔΑ_{i+1}" for i in range(len(groups))])) for cls in range(num_classes)}
            min_class = min(counts, key=counts.get)
            for student in group:
                df.loc[df["ΟΝΟΜΑ"] == student, "ΤΜΗΜΑ"] = min_class
                class_assignments[min_class].append(student)

    return df
