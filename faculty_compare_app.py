
import streamlit as st
import pandas as pd
import json

st.title("Faculty List Comparison Tool")

st.write("""
Upload two faculty lists (CSV or JSON) to compare who to **add**, **remove**, or whose details have **changed**.
- Matching is based on the `EmailAddress` or `email` column
- We'll also detect changes in: `GivenName`, `sn`, `Title`, `Department`, `TelephoneNumber`, `PhysicalDeliveryOfficeName`
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

            # Match on EmailAddress to detect updates
            shared_emails = new_df[new_df['EmailAddress'].isin(old_df['EmailAddress'])]
            merged = pd.merge(old_df, shared_emails, on='EmailAddress', suffixes=('_old', '_new'))

            # Columns to check for updates
            compare_cols = ['GivenName', 'sn', 'Title', 'Department', 'TelephoneNumber', 'PhysicalDeliveryOfficeName']
            changes = []

            for _, row in merged.iterrows():
                diffs = {}
                for col in compare_cols:
                    old_val = row.get(f"{col}_old", "")
                    new_val = row.get(f"{col}_new", "")
                    if pd.notna(old_val) and pd.notna(new_val) and str(old_val).strip() != str(new_val).strip():
                        diffs[col] = {"Old": old_val, "New": new_val}
                if diffs:
                    changes.append({
                        "EmailAddress": row["EmailAddress"],
                        "Changes": diffs
                    })

            st.success(f"✅ Comparison complete.")
            st.write(f"➕ {len(to_add)} to add")
            st.write(f"❌ {len(to_remove)} to remove")
            st.write(f"🔁 {len(changes)} with updated details")

            st.subheader("➕ Faculty to Add")
            st.dataframe(to_add)
            st.download_button("Download Add List", to_add.to_csv(index=False), "faculty_to_add.csv", "text/csv")

            st.subheader("❌ Faculty to Remove")
            st.dataframe(to_remove)
            st.download_button("Download Remove List", to_remove.to_csv(index=False), "faculty_to_remove.csv", "text/csv")

            if changes:
                st.subheader("🔁 Faculty with Updated Info")
                change_records = []
                for change in changes:
                    email = change["EmailAddress"]
                    for field, diff in change["Changes"].items():
                        change_records.append({
                            "EmailAddress": email,
                            "Field": field,
                            "Old Value": diff["Old"],
                            "New Value": diff["New"]
                        })
                changes_df = pd.DataFrame(change_records)
                st.dataframe(changes_df)
                st.download_button("Download Change List", changes_df.to_csv(index=False), "faculty_changes.csv", "text/csv")
