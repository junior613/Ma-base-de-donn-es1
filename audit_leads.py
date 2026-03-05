import pandas as pd
import re

def audit_data(file_path):
    df = pd.read_excel(file_path)
    print(f"Audit of {file_path}")
    print("-" * 30)
    
    # Check Columns
    print("Columns found:", df.columns.tolist())
    
    # Check for potential duplicates (Case insensitive name + Phone)
    if 'Noms' in df.columns:
        df['norm_name'] = df['Noms'].astype(str).str.lower().str.strip()
        dupes = df[df.duplicated(subset=['norm_name'], keep=False)]
        if not dupes.empty:
            print("\nPotential Name Duplicates (first 5):")
            print(dupes[['Noms', 'Téléphone']].head(10))
    
    # Check Phone Numbers
    if 'Téléphone' in df.columns:
        invalid_phones = df[df['Téléphone'].astype(str).str.len() < 5]
        if not invalid_phones.empty:
            print("\nShort/Invalid Phone Numbers (first 5):")
            print(invalid_phones[['Noms', 'Téléphone']].head(5))
            
    # Check Emails
    if 'Email' in df.columns:
        invalid_emails = df[~df['Email'].astype(str).str.contains('@').fillna(False) & df['Email'].notnull() & (df['Email'] != 'Inconnu')]
        if not invalid_emails.empty:
            print("\nInvalid Email Formats:")
            print(invalid_emails[['Noms', 'Email']].head(5))

    # Check for value clusters (potential inconsistencies in Ville/Source)
    for col in ['Ville', 'Source', 'Status', 'Quartiers']:
        if col in df.columns:
            print(f"\nValue clusters for {col}:")
            print(df[col].value_counts().head(10))

if __name__ == "__main__":
    audit_data('Leads-consolidés-propre.xlsx')
