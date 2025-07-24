# Βήμα 2 – Κατανομή Ζωηρών Μαθητών για όλα τα σενάρια
import pandas as pd
from collections import defaultdict


def step2_zoiroi(df, num_classes, senario_col):
    df = df.copy()

    # Εντοπίζουμε όλους τους ζωηρούς μαθητές
    zoiroi = df[df['ΖΩΗΡΟΣ'] == 'Ν']
    if zoiroi.empty:
        return df  # Αν δεν υπάρχουν, επιστρέφουμε αμέσως το αρχικό df

    # Εντοπίζουμε τους ζωηρούς που έχουν ήδη τοποθετηθεί στο σενάριο
    zoiroi_protou_vimatos = zoiroi[~df[senario_col].isna()]
    zoiroi_neoi = zoiroi[df[senario_col].isna()]  # Παιδιά που θα τοποθετηθούν τώρα

    # Αρχικοποίηση κατανομής ζωηρών
    zoiroi_ana_tmima = defaultdict(int)
    for _, row in zoiroi_protou_vimatos.iterrows():
        tmima = row[senario_col]
        if pd.notna(tmima):
            zoiroi_ana_tmima[tmima] += 1

    # Εντοπίζουμε υφιστάμενες συγκρούσεις
    synolo_tmimaton = list(range(1, num_classes + 1))

    for _, row in zoiroi_neoi.iterrows():
        mathitis = row['ΟΝΟΜΑ']
        fylo = row['ΦΥΛΟ']
        sygkrousi = str(row['ΣΥΓΚΡΟΥΣΗ']).split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else []
        idiaiterotita = row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν'
        filoi = str(row['ΦΙΛΟΙ']).split(',') if pd.notna(row['ΦΙΛΟΙ']) else []

        best_choice = None
        min_zoiroi = float('inf')
        for tmima in synolo_tmimaton:
            # 1. Ισοκατανομή Ζωηρών
            arithmos_zoiroi = zoiroi_ana_tmima[tmima]
            if arithmos_zoiroi > min_zoiroi:
                continue  # Θέλουμε να γεμίσουμε πρώτα τμήματα με λιγότερους ζωηρούς

            # 2. Αποφυγή Εξωτερικών Συγκρούσεων
            mathites_tmimatos = df[df[senario_col] == tmima]['ΟΝΟΜΑ'].tolist()
            if any(s in mathites_tmimatos for s in sygkrousi):
                continue

            # 3. Παιδαγωγικές Συγκρούσεις
            for m in df[df[senario_col] == tmima].itertuples():
                if m.ΖΩΗΡΟΣ == 'Ν' or m.ΙΔΙΑΙΤΕΡΟΤΗΤΑ == 'Ν':
                    if idiaiterotita or row['ΖΩΗΡΟΣ'] == 'Ν':
                        break  # Παιδαγωγική σύγκρουση
            else:
                # 4. Πλήρως Αμοιβαία Φιλία (εφόσον δεν υπάρχουν συγκρούσεις)
                if any((f.strip() in mathites_tmimatos) and (df.loc[df['ΟΝΟΜΑ'] == f.strip(), 'ΦΙΛΟΙ'].str.contains(mathitis).any()) for f in filoi):
                    best_choice = tmima
                    break

                # 5. Ισορροπία φύλου (δεύτερο κριτήριο)
                if arithmos_zoiroi < min_zoiroi:
                    min_zoiroi = arithmos_zoiroi
                    best_choice = tmima

        if best_choice is not None:
            df.loc[df['ΟΝΟΜΑ'] == mathitis, senario_col] = best_choice
            zoiroi_ana_tmima[best_choice] += 1

    return df
