
import streamlit as st
import pandas as pd
import json

st.title("Faculty List Comparison Tool")

st.write("""
Upload two faculty lists to compare who to **add** and who to **remove**.
- You can upload **CSV or JSON** (like the UAFS directory export)
- Matching is based on the `EmailAddress` or `email` column
""")

# File uploaders
old_file = st.file_uploader("Upload OLD faculty list (CSV or JSON)", type=["csv", "json"])
new_file = st.file_uploader("Upload NEW faculty list (CSV or JSON)", type=["csv", "json"])

def load_file(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".json"):
        data = json.load(file)
        df = pd.DataFrame(data)
    else:
        return None
    return df

if old_file and new_file:
    old_df = load_file(old_file)
    new_df = load_file(new_file)

    if old_df is None or new_df is None:
        st.error("Error loading one of the files.")
    else:
        # Normalize column names
        old_df.rename(columns=lambda x: x.strip(), inplace=True)
        new_df.rename(columns=lambda x: x.strip(), inplace=True)

        # Normalize 'email' to 'EmailAddress'
        if 'email' in old_df.columns:
            old_df.rename(columns={'email': 'EmailAddress'}, inplace=True)
        if 'email' in new_df.columns:
            new_df.rename(columns={'email': 'EmailAddress'}, inplace=True)

        if 'EmailAddress' not in old_df.columns or 'EmailAddress' not in new_df.columns:
            st.error("Both files must contain an 'EmailAddress' column or 'email'.")
        else:
            to_add = new_df[~new_df['EmailAddress'].isin(old_df['EmailAddress'])]
            to_remove = old_df[~old_df['EmailAddress'].isin(new_df['EmailAddress'])]

            st.success(f"✅ Comparison complete. Found {len(to_add)} to add and {len(to_remove)} to remove.")

            st.subheader("➕ Faculty to Add")
            st.dataframe(to_add)
            st.download_button("Download Add List", to_add.to_csv(index=False), "faculty_to_add.csv", "text/csv")

            st.subheader("❌ Faculty to Remove")
            st.dataframe(to_remove)
            st.download_button("Download Remove List", to_remove.to_csv(index=False), "faculty_to_remove.csv", "text/csv")
