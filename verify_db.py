from database.db_client import DatabaseClient
import os

def test_db():
    print("[*] Testing Database Initialization...")
    db = DatabaseClient()
    db_path = db.db_path
    if os.path.exists(db_path):
        print(f"[+] Database file found at: {db_path}")
        # Check tables
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [row['name'] for row in tables]
        required_tables = ['leads', 'opportunities', 'cold_emails', 'hyderabad_startups', 'scans']
        for table in required_tables:
            if table in table_names:
                print(f"[+] Table '{table}' exists.")
            else:
                print(f"[-] Table '{table}' is MISSING.")
    else:
        print("[-] Database file NOT found.")

if __name__ == "__main__":
    test_db()
