import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outreach.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

class DatabaseClient:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        if not os.path.exists(self.db_path):
            print(f"[*] Initializing database at {self.db_path}")
            with open(SCHEMA_PATH, 'r') as f:
                schema = f.read()
            conn = self._get_connection()
            conn.executescript(schema)
            conn.commit()
            conn.close()

    def execute_query(self, query, params=(), commit=False):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor.fetchall()
        finally:
            conn.close()

    def insert_lead(self, table, data):
        """Generic upsert for leads/startups based on URL."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        
        # Determine the conflict column (usually 'url' or 'company_url')
        conflict_col = 'url'
        if table == 'hyderabad_startups':
            conflict_col = 'company_url'
        
        # Prepare update clause for conflict
        update_clause = ', '.join([f"{col}=excluded.{col}" for col in data.keys() if col != conflict_col])
        
        query = f"""
            INSERT INTO {table} ({columns})
            VALUES ({placeholders})
            ON CONFLICT({conflict_col}) DO UPDATE SET
            {update_clause},
            updated_at=CURRENT_TIMESTAMP if '{table}' == 'hyderabad_startups' else updated_at
        """
        
        # Fix the updated_at logic for SQLite ON CONFLICT
        if table == 'hyderabad_startups':
            update_clause = ', '.join([f"{col}=excluded.{col}" for col in data.keys() if col != conflict_col])
            update_clause += ", updated_at=CURRENT_TIMESTAMP"
            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({conflict_col}) DO UPDATE SET {update_clause}
            """
        else:
            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({conflict_col}) DO UPDATE SET {update_clause}
            """

        conn = self._get_connection()
        try:
            conn.execute(query, list(data.values()))
            conn.commit()
        finally:
            conn.close()

    def get_hyderabad_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        stats = {
            'total': cursor.execute("SELECT COUNT(*) FROM hyderabad_startups").fetchone()[0],
            'passed': cursor.execute("SELECT COUNT(*) FROM hyderabad_startups WHERE pass = 1").fetchone()[0],
            'drafted': cursor.execute("SELECT COUNT(*) FROM hyderabad_startups WHERE status = 'drafted'").fetchone()[0],
            'replied': cursor.execute("SELECT COUNT(*) FROM hyderabad_startups WHERE status = 'replied'").fetchone()[0]
        }
        conn.close()
        return stats

    def get_hyderabad_startups(self, sources=None, stack=None, statuses=None, min_score=0):
        query = "SELECT * FROM hyderabad_startups WHERE score >= ?"
        params = [min_score]
        
        if sources:
            query += f" AND source IN ({','.join(['?' for _ in sources])})"
            params.extend(sources)
        
        if statuses:
            query += f" AND status IN ({','.join(['?' for _ in statuses])})"
            params.extend(statuses)
            
        query += " ORDER BY score DESC"
        
        results = self.execute_query(query, params)
        return [dict(row) for row in results]

    def update_hyderabad_status(self, startup_id, status):
        self.execute_query(
            "UPDATE hyderabad_startups SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, startup_id),
            commit=True
        )

    def update_hyderabad_notes(self, startup_id, notes):
        self.execute_query(
            "UPDATE hyderabad_startups SET notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (notes, startup_id),
            commit=True
        )
    
    def save_hyderabad_email(self, startup_id, subject, message):
        self.execute_query(
            "UPDATE hyderabad_startups SET generated_subject = ?, generated_message = ?, status = 'drafted', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (subject, message, startup_id),
            commit=True
        )
