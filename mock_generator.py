import pandas as pd


def generate_mock_data():
    print("⏳ Creating safe, simulated testing datasets...")

    # 1. Simulate the P-Card Reconciliation Spreadsheet (with one deliberate typo/anomaly)
    pcard_data = {
        'Transaction ID': ['TXN1001', 'TXN1002', 'TXN1003', 'TXN1004'],
        'Amount': [250.50, 1200.00, 45.15, 310.20],
        'GL Account': ['100-4120-000', '200-4210-110', '100-4120-000', '999-9999-999'],  # 999 is invalid
        'Project Code': ['PRJ-A', 'PRJ-B', 'PRJ-A', 'PRJ-ERR']  # PRJ-ERR is invalid
    }

    # 2. Simulate the master budget system active account list
    gl_master_data = {
        'Active GL Account': ['100-4120-000', '200-4210-110', '300-4310-220'],
        'Active Project Code': ['PRJ-A', 'PRJ-B', 'PRJ-C']
    }

    # Output to clean CSVs
    pd.DataFrame(pcard_data).to_csv('mock_pcard_reconciliation.csv', index=False)
    pd.DataFrame(gl_master_data).to_csv('mock_gl_master.csv', index=False)

    print("✅ Success! Formatted mock files have been dropped into your workspace:")
    print("   👉 'mock_pcard_reconciliation.csv'")
    print("   👉 'mock_gl_master.csv'\n")


if __name__ == "__main__":
    generate_mock_data()
