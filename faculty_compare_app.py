
import streamlit as st
import pandas as pd

st.title("Faculty CSV Comparison Tool")

st.write("""
Upload two CSV files to compare faculty records.

- The script will match on **EmailAddress**
- It will output:
  - A list of people to **add**
  - A list of people to **remove**
""")

old_file = st.file_uploader("Upload OLD faculty CSV", type="csv")
new_file = st.file_uploader("Upload NEW faculty CSV", type="csv")

if old_file and new_file:
    old_df = pd.read_csv(old_file)
    new_df = pd.read_csv(new_file)

    if 'EmailAddress' not in old_df.columns or 'EmailAddress' not in new_df.columns:
        st.error("Both files must contain an 'EmailAddress' column.")
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
