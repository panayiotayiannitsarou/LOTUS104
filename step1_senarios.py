import pandas as pd
from itertools import permutations
from collections import defaultdict


def check_conflicts(pair, df):
    df = df.set_index("ΟΝΟΜΑ")
    p1, p2 = pair

    # Εξωτερική σύγκρουση
    conflict_1 = str(df.loc[p1, "ΣΥΓΚΡΟΥΣΗ"]).split(',') if pd.notna(df.loc[p1, "ΣΥΓΚΡΟΥΣΗ"]) else []
    conflict_2 = str(df.loc[p2, "ΣΥΓΚΡΟΥΣΗ"]).split(',') if pd.notna(df.loc[p2, "ΣΥΓΚΡΟΥΣΗ"]) else []
    if p2 in [c.strip() for c in conflict_1] or p1 in [c.strip() for c in conflict_2]:
        return True

    # Παιδαγωγική σύγκρουση
    def is_zoiros(x): return str(df.loc[x, "ΖΩΗΡΟΣ"]).strip().upper() == 'Ν'
    def is_idiaterotita(x): return str(df.loc[x, "ΙΔΙΑΙΤΕΡΟΤΗΤΑ"]).strip().upper() == 'Ν'

    if (is_zoiros(p1) and is_zoiros(p2)) or (is_idiaterotita(p1) and is_idiaterotita(p2)) or        (is_zoiros(p1) and is_idiaterotita(p2)) or (is_zoiros(p2) and is_idiaterotita(p1)):
        return True

    return False


def get_fully_mutual_friends(df):
    mutual = defaultdict(list)
    names = df["ΟΝΟΜΑ"].tolist()
    friends_dict = dict(zip(df["ΟΝΟΜΑ"], df["ΦΙΛΟΣ"]))
    for name in names:
        declared_friends = [f.strip() for f in str(friends_dict.get(name, "")).split(",") if f.strip() in names]
        for friend in declared_friends:
            friends_of_friend = [f.strip() for f in str(friends_dict.get(friend, "")).split(",") if f.strip() in names]
            if name in friends_of_friend:
                mutual[name].append(friend)
    return dict(mutual)


def step1_katanomi_paidia_ekpaideutikon(df: pd.DataFrame, num_classes: int):
    df = df.copy()
    df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""

    df_teachers = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"].copy()
    teacher_names = df_teachers["ΟΝΟΜΑ"].tolist()

    if not teacher_names:
        return [df], ["Δεν υπάρχουν παιδιά εκπαιδευτικών"]

    all_class_labels = [f"Α{i+1}" for i in range(num_classes)]

    permutations_set = set()
    scenario_data = []
    MAX_VALID_SCENARIOS = 5
    MAX_TOTAL_SCENARIOS = 30

    mutual = get_fully_mutual_friends(df)

    for perm in permutations(all_class_labels * ((len(teacher_names) + num_classes - 1) // num_classes), len(teacher_names)):
        class_counts = defaultdict(int)
        scenario = df.copy()
        teacher_assignment = {}

        for i, name in enumerate(teacher_names):
            assigned_class = perm[i]
            class_counts[assigned_class] += 1
            teacher_assignment[name] = assigned_class

        counts = list(class_counts.values())
        if max(counts) - min(counts) > 1:
            continue

        group_signature = tuple(sorted([tuple(sorted([k for k,v in teacher_assignment.items() if v == cl])) for cl in all_class_labels]))
        if group_signature in permutations_set:
            continue
        permutations_set.add(group_signature)

        # Έλεγχος εξωτερικών και παιδαγωγικών συγκρούσεων
        conflict_found = False
        for i, name1 in enumerate(teacher_names):
            for j, name2 in enumerate(teacher_names):
                if i >= j:
                    continue
                if teacher_assignment[name1] == teacher_assignment[name2]:
                    if check_conflicts((name1, name2), scenario):
                        conflict_found = True
                        break
            if conflict_found:
                break
        if conflict_found:
            continue

        # Υπολογισμός σπασμένων πλήρως αμοιβαίων φιλιών μεταξύ παιδιών εκπαιδευτικών
        broken_friendships = 0
        for name in teacher_names:
            for friend in mutual.get(name, []):
                if friend in teacher_names and teacher_assignment[name] != teacher_assignment[friend]:
                    broken_friendships += 1

        # Απόρριψη σεναρίων όπου όλα τα παιδιά πάνε στο ίδιο τμήμα
        if len(set(teacher_assignment.values())) == 1:
            continue

        for name, assigned_class in teacher_assignment.items():
            scenario.loc[scenario["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = assigned_class
            scenario.loc[scenario["ΟΝΟΜΑ"] == name, "ΤΜΗΜΑ"] = assigned_class

        scenario_data.append((scenario.copy(), broken_friendships))

        if len(scenario_data) >= MAX_TOTAL_SCENARIOS:
            break

    if not scenario_data:
        return [df], ["Δεν βρέθηκαν έγκυρα σενάρια"]

    min_broken = min(b for _, b in scenario_data)
    best_scenarios = [(s, b) for s, b in scenario_data if b == min_broken]
    best_scenarios = best_scenarios[:MAX_VALID_SCENARIOS]

    final_scenarios = []
    final_descriptions = []

    for i, (scenario, broken_friendships) in enumerate(best_scenarios):
        col_to_fill = f"ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ_ΣΕΝΑΡΙΟ_{i+1}"
        scenario[col_to_fill] = scenario["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        final_scenarios.append(scenario)
        final_descriptions.append(f"Σενάριο {i+1} – Παιδιά εκπαιδευτικών, σπασμένες φιλίες: {broken_friendships}")

    return final_scenarios, final_descriptions
