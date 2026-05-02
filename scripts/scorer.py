import json
import os

def get_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def score_lead(row, config):
    score = 0
    
    # 1. No website -> +4
    website = str(row.get('website', ''))
    if website.lower() in ['nan', 'null', '', 'none']:
        score += 4
        
    # 2. Low rating and high reviews (active but bad reputation)
    try:
        rating = float(row.get('rating', 0.0))
        if rating > 0:
            if rating < 4.0:
                score += 3
            if rating < 3.5:
                score += 2
    except ValueError:
        pass
        
    try:
        reviews = int(row.get('reviews', 0))
        if reviews > 20:
            score += 3
        if reviews > 100:
            score += 2
    except ValueError:
        pass
        
    # 3. Category priority -> +3
    category = str(row.get('category', '')).lower()
    high_val_cats = config.get('high_value_categories', [])
    if any(c in category for c in high_val_cats):
        score += 3
        
    # 4. High-value areas -> +2
    area = str(row.get('area', '')).lower()
    high_val_areas = config.get('high_value_areas', [])
    if any(a in area for a in high_val_areas):
        score += 2
        
    return score

def score_leads(df):
    if df.empty:
        return df
        
    config = get_config()
    
    df['score'] = df.apply(lambda row: score_lead(row, config), axis=1)
    
    # Sort highest first
    df_sorted = df.sort_values(by='score', ascending=False)
    return df_sorted

if __name__ == "__main__":
    import processor
    df = processor.process_leads()
    scored_df = score_leads(df)
    print(scored_df[['business_name', 'score', 'category']].head())
