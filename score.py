# score.py

import pandas as pd

def calculate_score(df: pd.DataFrame, num_classes: int) -> int:
    score = 0

    # 🔴 External Conflicts (ΣΥΓΚΡΟΥΣΗ)
    for _, row in df.iterrows():
        name = row["ΟΝΟΜΑ"]
        tmima = row["ΤΜΗΜΑ"]
        conflicts = str(row.get("ΣΥΓΚΡΟΥΣΗ", "")).split(',')
        for c in conflicts:
            c = c.strip()
            if c and c in df["ΟΝΟΜΑ"].values:
                other_tmima = df[df["ΟΝΟΜΑ"] == c]["ΤΜΗΜΑ"].values[0]
                if other_tmima == tmima:
                    score += 10  # Conflict in same class

    # 🟠 Pedagogical Conflicts (ΖΩΗΡΟΣ & ΙΔΙΑΙΤΕΡΟΤΗΤΑ)
    for tmima in df["ΤΜΗΜΑ"].unique():
        students = df[df["ΤΜΗΜΑ"] == tmima]
        zoiroi = students[students["ΖΩΗΡΟΣ"] == "Ν"]
        idiotites = students[students["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"]
        both = pd.concat([zoiroi, idiotites])
        count = len(both)
        if count > 1:
            score += 3 * (count * (count - 1)) // 2  # all unique pairs

    # 🟡 Broken Fully Mutual Friendships
    friend_dict = dict(zip(df["ΟΝΟΜΑ"], df["ΦΙΛΟΣ"]))
    names = df["ΟΝΟΜΑ"].tolist()
    for name in names:
        declared = [f.strip() for f in str(friend_dict.get(name, "")).split(",") if f.strip()]
        for friend in declared:
            if friend in names:
                f_declared = [f.strip() for f in str(friend_dict.get(friend, "")).split(",") if f.strip()]
                if name in f_declared:
                    if df[df["ΟΝΟΜΑ"] == name]["ΤΜΗΜΑ"].values[0] != df[df["ΟΝΟΜΑ"] == friend]["ΤΜΗΜΑ"].values[0]:
                        score += 5

    # ⚖️ Gender Balance
    for tmima in df["ΤΜΗΜΑ"].unique():
        students = df[df["ΤΜΗΜΑ"] == tmima]
        boys = len(students[students["ΦΥΛΟ"] == "Α"])
        girls = len(students[students["ΦΥΛΟ"] == "Κ"])
        if abs(boys - girls) > 3:
            score += abs(boys - girls) - 3

    # ⚖️ Language Balance
    for tmima in df["ΤΜΗΜΑ"].unique():
        students = df[df["ΤΜΗΜΑ"] == tmima]
        good = len(students[students["ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"] == "Ν"])
        not_good = len(students[students["ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ"] == "Ο"])
        if abs(good - not_good) > 3:
            score += abs(good - not_good) - 3

    # 👥 Population Balance
    counts = df["ΤΜΗΜΑ"].value_counts().tolist()
    if max(counts) - min(counts) > 2:
        return 9999  # ❌ Reject scenarios with >2 diff
    elif max(counts) - min(counts) == 2:
        score += 2
    elif max(counts) - min(counts) == 1:
        score += 1

    return score
