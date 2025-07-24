def step4_amoivaies_filies(df):
    """
    Βήμα 4 – Κατανομή Μη Τοποθετημένων Μαθητών βάσει Αμοιβαίας Φιλίας
    Τοποθετεί όσους δεν έχουν τοποθετηθεί ακόμα (ΤΜΗΜΑ κενό) στο ίδιο τμήμα με τον αμοιβαίο τους φίλο,
    αν ο φίλος έχει ήδη τοποθετηθεί σε τμήμα.
    
    Η συνθήκη για πλήρως αμοιβαία φιλία είναι:
    - Ο μαθητής Α έχει δηλώσει ως φίλο τον Β, και
    - Ο μαθητής Β έχει δηλώσει ως φίλο τον Α.
    """
    df = df.copy()

    # Φτιάχνουμε λεξικό με τους φίλους κάθε μαθητή
    friend_map = dict(zip(df['ΟΝΟΜΑ'], df['ΦΙΛΟΣ']))
    class_map = dict(zip(df['ΟΝΟΜΑ'], df['ΤΜΗΜΑ']))

    for index, row in df[df['ΤΜΗΜΑ'].isna()].iterrows():
        student = row['ΟΝΟΜΑ']
        friend = row['ΦΙΛΟΣ']

        # Έλεγχος πλήρους αμοιβαιότητας
        if friend in friend_map and friend_map[friend] == student:
            friend_class = class_map.get(friend)
            if pd.notna(friend_class):
                # Αν ο φίλος έχει ήδη τοποθετηθεί, τοποθέτηση στο ίδιο τμήμα
                df.at[index, 'ΤΜΗΜΑ'] = friend_class

    return df
