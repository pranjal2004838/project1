import sqlite3
import pandas as pd
conn = sqlite3.connect('outreach.db')
print("--- hyderabad_startups ---")
df = pd.read_sql("SELECT id, company_name, score, pass FROM hyderabad_startups", conn)
print(df)
print("--- opportunities (internships) ---")
df2 = pd.read_sql("SELECT id, name, company, score, pass FROM opportunities", conn)
print(df2)
print("--- cold_emails ---")
df3 = pd.read_sql("SELECT id, founder_name, company_name, score, pass FROM cold_emails", conn)
print(df3)
conn.close()
