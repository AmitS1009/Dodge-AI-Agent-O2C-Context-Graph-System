import os
import json
import sqlite3
import pandas as pd
from pathlib import Path

def build_database():
    db_path = 'o2c.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    data_dir = Path('sap-o2c-data')

    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist.")
        return

    for folder in data_dir.iterdir():
        if folder.is_dir():
            table_name = folder.name
            dfs = []
            for file in folder.glob('*.jsonl'):
                try:
                    df = pd.read_json(file, lines=True)
                    # Convert nested dicts/lists to JSON strings
                    for col in df.columns:
                        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                            df[col] = df[col].apply(json.dumps)
                    dfs.append(df)
                except Exception as e:
                    print(f'Error reading {file}: {e}')
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                combined_df.to_sql(table_name, conn, index=False, if_exists='replace')
                print(f'Imported {len(combined_df)} rows into {table_name}')

    conn.close()
    print('✅ Database built successfully as o2c.db')

if __name__ == '__main__':
    build_database()
