import pandas as pd
from collections import defaultdict
import random

def step3_idiaiterotites(df, num_classes):
    """
    Κατανομή Παιδιών με Ιδιαιτερότητες (Βήμα 3) για κάθε σενάριο.
    Τοποθετούνται όσοι έχουν ΙΔΙΑΙΤΕΡΟΤΗΤΑ = 'Ν', λαμβάνοντας υπόψη όσους έχουν ήδη τοποθετηθεί.
    """

    scenarios = [col for col in df.columns if col.startswith("ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_")]
    if not scenarios:
        return df

    for scenario in scenarios:
        scenario_df = df.copy()

        # Βρες τους ήδη τοποθετημένους μαθητές
        placed_students = scenario_df[scenario].notna()

        # Υπολογισμός υπάρχουσας κατανομής ιδιαιτεροτήτων
        special_counts = defaultdict(int)
        class_rosters = defaultdict(list)
        class_zohiroi = defaultdict(int)
        class_genders = defaultdict(lambda: {"Α": 0, "Κ": 0})

        for _, row in scenario_df[placed_students].iterrows():
            cls = row[scenario]
            if row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν':
                special_counts[cls] += 1
            if row['ΖΩΗΡΟΣ'] == 'Ν':
                class_zohiroi[cls] += 1
            class_rosters[cls].append(row['ΟΝΟΜΑ'])
            if row['ΦΥΛΟ'] in ('Α', 'Κ'):
                class_genders[cls][row['ΦΥΛΟ']] += 1

        # Αναγνώριση υποψηφίων για τοποθέτηση
        candidates = scenario_df[(scenario_df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & scenario_df[scenario].isna()]

        for _, row in candidates.iterrows():
            name = row['ΟΝΟΜΑ']
            gender = row['ΦΥΛΟ']
            filoi = set(str(row['ΦΙΛΟΙ']).split(',')) if pd.notna(row['ΦΙΛΟΙ']) else set()
            sygkrouseis = set(str(row['ΣΥΓΚΡΟΥΣΗ']).split(',')) if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else set()

            # Ταξινόμηση τάξεων με βάση αριθμό ζωηρών
            sorted_classes = sorted(range(1, num_classes + 1), key=lambda c: class_zohiroi.get(c, 0))
            placed = False

            for c in sorted_classes:
                # Έλεγχος εξωτερικών συγκρούσεων
                if any(friend in sygkrouseis for friend in class_rosters[c]):
                    continue

                # Έλεγχος παιδαγωγικών συγκρούσεων
                conflict = False
                for student in class_rosters[c]:
                    student_row = scenario_df[scenario_df['ΟΝΟΜΑ'] == student].iloc[0]
                    if (student_row['ΖΩΗΡΟΣ'] == 'Ν' and row['ΖΩΗΡΟΣ'] == 'Ν') or \
                       (student_row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν' and row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') or \
                       ((student_row['ΖΩΗΡΟΣ'] == 'Ν' and row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') or
                        (student_row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν' and row['ΖΩΗΡΟΣ'] == 'Ν')):
                        conflict = True
                        break
                if conflict:
                    continue

                # Αν υπάρχει πλήρως αμοιβαία φιλία με μαθητή στο τμήμα, προτιμάται
                mutual_friend = False
                for f in filoi:
                    f = f.strip()
                    f_row = scenario_df[scenario_df['ΟΝΟΜΑ'] == f]
                    if not f_row.empty and f_row.iloc[0][scenario] == c:
                        f_friends = set(str(f_row.iloc[0]['ΦΙΛΟΙ']).split(',')) if pd.notna(f_row.iloc[0]['ΦΙΛΟΙ']) else set()
                        if name in f_friends:
                            mutual_friend = True
                            break

                # Ελέγχει και ισορροπία φύλου (προτιμάται πιο ισορροπημένη τάξη)
                gender_diff = abs(class_genders[c]['Α'] - class_genders[c]['Κ'])
                if mutual_friend or gender_diff <= 3:
                    # Τοποθέτηση
                    scenario_df.loc[scenario_df['ΟΝΟΜΑ'] == name, scenario] = c
                    class_rosters[c].append(name)
                    class_genders[c][gender] += 1
                    special_counts[c] += 1
                    placed = True
                    break

            if not placed:
                # Αν δεν βρέθηκε ιδανικό, βάλε στο τμήμα με τους λιγότερους με ιδιαιτερότητα
                fallback_class = min(range(1, num_classes + 1), key=lambda c: special_counts.get(c, 0))
                scenario_df.loc[scenario_df['ΟΝΟΜΑ'] == name, scenario] = fallback_class
                class_rosters[fallback_class].append(name)
                class_genders[fallback_class][gender] += 1
                special_counts[fallback_class] += 1

        df[scenario] = scenario_df[scenario]

    return df
