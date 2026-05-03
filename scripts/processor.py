import os
import pandas as pd
import glob
import sqlite3

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT UNIQUE,
            category TEXT,
            area TEXT,
            rating TEXT,
            reviews INTEGER,
            website TEXT,
            phone TEXT,
            score INTEGER,
            why_good_lead TEXT,
            suggested_pitch TEXT,
            lagging_aspect TEXT,
            status TEXT DEFAULT 'New',
            date_added TEXT
        )
    ''')
    conn.commit()
    return conn

def process_leads():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    db_path = os.path.join(base_dir, 'data', 'history.db')
    
    conn = init_db(db_path)
    
    all_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    if not all_files:
        print("No raw data files found.")
        return pd.DataFrame()
        
    df_list = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Clean data
    combined_df = combined_df.drop_duplicates(subset=['business_name'])
    combined_df['business_name'] = combined_df['business_name'].astype(str).str.strip()
    
    # Filter out already processed leads
    existing_leads = pd.read_sql_query("SELECT business_name FROM leads", conn)
    new_leads_df = combined_df[~combined_df['business_name'].isin(existing_leads['business_name'])]
    
    print(f"Found {len(new_leads_df)} new unique leads out of {len(combined_df)} total.")
    return new_leads_df

def save_leads_to_db(scored_df, ai_results_list):
    if scored_df.empty:
        return
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    db_path = os.path.join(base_dir, 'data', 'history.db')
    conn = init_db(db_path)
    
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Map AI results by business_name for easy lookup
    ai_map = {item.get('business_name', ''): item for item in ai_results_list}
    
    for _, row in scored_df.iterrows():
        name = row['business_name']
        ai_data = ai_map.get(name, {})
        
        try:
            conn.execute('''
                INSERT INTO leads 
                (business_name, category, area, rating, reviews, website, phone, score, why_good_lead, suggested_pitch, lagging_aspect, date_added)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                row.get('category', ''),
                row.get('area', ''),
                str(row.get('rating', '')),
                int(row.get('reviews', 0)) if pd.notna(row.get('reviews')) else 0,
                str(row.get('website', '')),
                str(row.get('phone', '')),
                int(row.get('score', 0)),
                ai_data.get('why_good_lead', ''),
                ai_data.get('suggested_pitch', ''),
                ai_data.get('lagging_aspect', ''),
                date_str
            ))
        except sqlite3.IntegrityError:
            pass # already exists
    conn.commit()
    conn.close()

if __name__ == "__main__":
    df = process_leads()
    print(df.head())
