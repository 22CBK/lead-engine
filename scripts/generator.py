import os
import json
import requests
import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

def get_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def load_prompt(leads_data_str):
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'daily_agent.txt')
    with open(prompt_path, 'r') as f:
        template = f.read()
    return template.replace('{leads_data}', leads_data_str)

def generate_daily_plan(scored_df):
    if scored_df.empty:
        return []
        
    config = get_config()
    api_key = os.environ.get('GROQ_API_KEY', '')
    endpoint = config.get('api_endpoint', 'https://api.groq.com/openai/v1/chat/completions')
    model = config.get('ai_model', 'llama-3.1-8b-instant')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment.")
        return []
        
    # Process up to 100 leads in batches of 20
    top_leads = scored_df.head(100)
    chunk_size = 20
    chunks = [top_leads[i:i+chunk_size] for i in range(0, top_leads.shape[0], chunk_size)]
    
    all_ai_results = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processing AI batch {i+1}/{len(chunks)} ({len(chunk)} leads)...")
        
        leads_data = []
        for _, row in chunk.iterrows():
            leads_data.append({
                "business_name": row['business_name'],
                "category": row['category'],
                "rating": row['rating'],
                "reviews": row['reviews'],
                "score": row['score']
            })
            
        leads_str = json.dumps(leads_data, indent=2)
        prompt = load_prompt(leads_str)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a helpful sales AI. You MUST respond with ONLY a valid JSON object containing a key 'leads' that holds an array of lead objects. Example: {\"leads\": [{\"business_name\": \"...\", \"lagging_aspect\": \"...\", \"why_good_lead\": \"...\", \"suggested_pitch\": \"...\"}]}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            
            result_json = response.json()
            content = result_json['choices'][0]['message']['content']
            
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
                
            parsed = json.loads(content)
            leads = parsed.get("leads", [])
            all_ai_results.extend(leads)
            
        except Exception as e:
            print(f"Failed to generate plan for batch {i+1}: {e}")
            
    return all_ai_results

if __name__ == "__main__":
    import processor
    import scorer
    df = processor.process_leads()
    scored_df = scorer.score_leads(df)
    print(generate_daily_plan(scored_df))
