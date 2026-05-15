import os
import sys


def menu():
    while True:
        print("\n=== DevPresence CLI ===")
        print("1. Initialize Database")
        print("2. Run Lead Research")
        print("3. Start Scheduler (Background)")
        print("4. Start Dashboard (Streamlit)")
        print("5. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            os.system("python devpresence/database.py")
        elif choice == '2':
            from devpresence.lead_finder import run_lead_research
            run_lead_research()
        elif choice == '3':
            os.system("python devpresence/scheduler.py")
        elif choice == '4':
            os.system("streamlit run devpresence/dashboard.py")
        elif choice == '5':
            sys.exit(0)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    # Fix python path if running directly
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    if len(sys.argv) > 1 and sys.argv[1] == '--init':
        import database
        database.init_db()
        sys.exit(0)
        
    menu()