import os
import pandas as pd


def get_user_file(prompt_text):
    """Prompts user for a valid file path and handles basic validation."""
    while True:
        file_path = input(prompt_text).strip().strip('"')  # Strip out dragged quotes
        if os.path.exists(file_path):
            return file_path
        print(f"❌ File not found at: {file_path}. Please try again.")


def main():
    print("==============================================")
    print("      AUTOMATED EXPENSE AUDITOR PIPELINE      ")
    print("==============================================\n")

    # 1. User Ingestion Prompts
    pcard_path = get_user_file("👉 Enter path to the P-Card Reconciliation Spreadsheet (CSV): ")
    gl_path = get_user_file("👉 Enter path to the Active GL & Project Master List (CSV): ")

    print("\n⏳ Ingesting and parsing data streams via Pandas...")
    df_pcard = pd.read_csv(pcard_path)
    df_gl_master = pd.read_csv(gl_path)

    # Standardizing column names for clean mapping
    # Expected columns in P-Card: 'Transaction ID', 'Amount', 'GL Account', 'Project Code'
    # Expected columns in Master List: 'Active GL Account', 'Active Project Code'
    
    # 2. Data Integrity Auditing (Account Check)
    print("🔍 Auditing account code integrity...")
    active_gls = set(df_gl_master['Active GL Account'].astype(str).str.strip())
    active_projects = set(df_gl_master['Active Project Code'].astype(str).str.strip())

    # Create mask vectors to find anomalies
    df_pcard['GL_Valid'] = df_pcard['GL Account'].astype(str).str.strip().isin(active_gls)
    df_pcard['Project_Valid'] = df_pcard['Project Code'].astype(str).str.strip().isin(active_projects)

    anomalies = df_pcard[(df_pcard['GL_Valid'] == False) | (df_pcard['Project_Valid'] == False)]
    valid_records = df_pcard[(df_pcard['GL_Valid'] == True) & (df_pcard['Project_Valid'] == True)].copy()

    if not anomalies.empty:
        print(f"⚠️ Found {len(anomalies)} account structure discrepancies! Logging error reports...")
        anomalies.to_csv("account_discrepancy_log.csv", index=False)
        print("📁 Saved anomalies to 'account_discrepancy_log.csv'")
    else:
        print("✅ All transaction accounts verified successfully against budget systems.")

    if valid_records.empty:
        print("❌ No valid records left to aggregate. Pipeline stopping.")
        return

    # 3. Aggregation & Fund Accounting
    print("📊 Aggregating transaction balances by Fund allocations...")
    
    # Extract Fund ID (e.g., matching '100' out of a '100-4120-000' sequence)
    valid_records['Fund ID'] = valid_records['GL Account'].astype(str).apply(lambda x: x.split('-')[0])

    # Build the standard Journal Entry rows
    je_rows = []
    
    # Group by Fund to summarize expenses (Debits)
    fund_groups = valid_records.groupby('Fund ID')['Amount'].sum().reset_index()

    for _, row in fund_groups.iterrows():
        fund = row['Fund ID']
        total_expense = row['Amount']

        # Add the aggregated Debit line item for the fund expenses
        je_rows.append({
            'Fund': fund,
            'Account Type': 'Debit (Expense Allocation)',
            'Amount': total_expense,
            'Description': f"Aggregated P-Card Expenditures Fund {fund}"
        })

        # 4. Compute Fund-Specific Cash Offsets (Credits)
        je_rows.append({
            'Fund': fund,
            'Account Type': 'Credit (Cash Offset)',
            'Amount': total_expense,  # Balancing out the debit entry
            'Description': f"Fund {fund} P-Card Cash Offset Balance"
        })

    # 5. Export Journal Entry Upload Spreadsheet
    df_journal_entry = pd.DataFrame(je_rows)
    output_filename = "final_journal_entry_upload.csv"
    df_journal_entry.to_csv(output_filename, index=False)

    print(f"\n🚀 SUCCESS: Balanced upload file generated with total offsets calculated.")
    print(f"📁 Output file exported cleanly to: '{output_filename}'")
    print("==============================================")


if __name__ == "__main__":
    main()
