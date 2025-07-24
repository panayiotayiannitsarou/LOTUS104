
import pandas as pd
from collections import Counter

def step7_final_check_and_fix(df, num_classes):
    # Βοηθητικές συναρτήσεις
    def count_features(df, group_col, value_col):
        result = {i: Counter() for i in range(1, num_classes + 1)}
        for _, row in df.iterrows():
            if pd.notna(row[group_col]):
                result[int(row['ΤΜΗΜΑ'])][row[value_col]] += 1
        return result

    def get_class_counts(df):
        return df['ΤΜΗΜΑ'].value_counts().to_dict()

    def find_swap_candidates(df, feature_col, value1, value2, step_col, target_step, same_gender=True):
        candidates1, candidates2 = [], []
        for _, row in df.iterrows():
            if row[step_col] == target_step:
                if row[feature_col] == value1:
                    candidates1.append(row)
                elif row[feature_col] == value2:
                    candidates2.append(row)
        return candidates1, candidates2

    def swap(df, id1, id2):
        t1 = df.loc[df['ID'] == id1, 'ΤΜΗΜΑ'].values[0]
        t2 = df.loc[df['ID'] == id2, 'ΤΜΗΜΑ'].values[0]
        df.loc[df['ID'] == id1, 'ΤΜΗΜΑ'] = t2
        df.loc[df['ID'] == id2, 'ΤΜΗΜΑ'] = t1
        return df

    warnings = []

    # 1. Κατηγοριοποίηση & Μετρήσεις
    class_counts = get_class_counts(df)

    # 2. Ποιοτικά Χαρακτηριστικά: Ισορροπία Φύλου και Γλώσσας
    gender_counts = count_features(df, 'ΤΜΗΜΑ', 'ΦΥΛΟ')
    greek_counts = count_features(df, 'ΤΜΗΜΑ', 'ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ')

    for feature, counts in [('ΦΥΛΟ', gender_counts), ('ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ', greek_counts)]:
        for val in set(v for d in counts.values() for v in d):
            values = [counts[i][val] for i in range(1, num_classes + 1)]
            if max(values) - min(values) > 3:
                # Προσπάθεια Ανταλλαγής
                for i in range(1, num_classes):
                    for j in range(i + 1, num_classes + 1):
                        diff = counts[i][val] - counts[j][val]
                        if abs(diff) > 3:
                            opposite_val = 'Ν' if val == 'Ο' else 'Ο' if val in ['Ν', 'Ο'] else 'ΑΓΟΡΙ' if val == 'ΚΟΡΙΤΣΙ' else 'ΚΟΡΙΤΣΙ'
                            cands1, _ = find_swap_candidates(df[(df['ΤΜΗΜΑ'] == i)], feature, val, opposite_val, 'ΒΗΜΑ', 5)
                            cands2, _ = find_swap_candidates(df[(df['ΤΜΗΜΑ'] == j)], feature, opposite_val, val, 'ΒΗΜΑ', 5)
                            for c1 in cands1:
                                for c2 in cands2:
                                    if c1['ΦΥΛΟ'] == c2['ΦΥΛΟ']:  # ίδιο φύλο
                                        df = swap(df, c1['ID'], c2['ID'])
                                        break

    # 3. Ποσοτική Ισορροπία Πληθυσμού (max diff = 2)
    class_counts = get_class_counts(df)
    max_size = max(class_counts.values())
    min_size = min(class_counts.values())
    if max_size - min_size > 2:
        warnings.append("⚠️ Δεν είναι δυνατή η πληθυσμιακή ισορροπία μεταξύ των τμημάτων (διαφορά > 2 μαθητές).")

    # 4. Επιστροφή DataFrame και Προειδοποιήσεων
    return df, warnings
