import os
import pandas as pd

def clean_username(u):
    u = str(u).strip()
    if "leetcode.com/u/" in u:
        return u.split("leetcode.com/u/")[-1].strip("/").split("/")[0]
    if "leetcode.com/" in u:
        return u.split("leetcode.com/")[-1].strip("/").split("/")[0]
    return u

def parse_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".xlsx":
        df = pd.read_excel(filepath)
    elif ext == ".csv":
        df = pd.read_csv(filepath)
    else:
        return [], f"Unsupported file type: {ext}"

    if len(df.columns) < 10:
        return [], f"File must have at least 10 columns (found {len(df.columns)})"

    name_col = df.iloc[:, 4]
    roll_col = df.iloc[:, 6]
    handle_col = df.iloc[:, 9]

    students = []
    for i in range(len(df)):
        name = str(name_col.iloc[i]).strip()
        roll = str(roll_col.iloc[i]).strip()
        username = clean_username(handle_col.iloc[i])

        if username and username.lower() not in ("nan", "none", "null", ""):
            students.append({
                "name": name,
                "roll_number": roll,
                "leetcode_username": username
            })

    return students, None
