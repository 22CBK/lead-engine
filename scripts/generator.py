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

def generate_daily_plan(df):
    if df.empty:
        return "# No New Leads Today\n\nNo leads to process. Run scraper or add more data."
        
    config = get_config()
    
    # Take top 30 leads to give context to LLM
    top_leads = df.head(30)
    
    # Format data for LLM
    leads_str = ""
    for i, row in top_leads.iterrows():
        website = row.get('website', 'None')
        if pd.isna(website) or website == 'nan': website = 'None'
        
        rating = row.get('rating', 'None')
        if pd.isna(rating) or rating == 'nan': rating = 'None'
        
        reviews = row.get('reviews', 0)
        leads_str += f"- Name: {row.get('business_name')}\n"
        leads_str += f"  Category: {row.get('category')}\n"
        leads_str += f"  Area: {row.get('area')}\n"
        leads_str += f"  Rating: {rating} ({reviews} reviews)\n"
        leads_str += f"  Website: {website}\n"
        leads_str += f"  Score: {row.get('score')}\n\n"
        
    prompt = load_prompt(leads_str)
    
    api_key = os.environ.get('GROQ_API_KEY', '')
    endpoint = config.get('api_endpoint', 'https://api.groq.com/openai/v1/chat/completions')
    model = config.get('ai_model', 'llama-3.1-8b-instant')
    provider = config.get('ai_provider', 'groq')
    
    if not api_key:
        print(f"Error: Missing {provider.capitalize()} API Key")
        return []
    
    print(f"Sending data to {provider.capitalize()} API ({model}) at {endpoint}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You are a helpful sales AI. You MUST respond with ONLY a valid JSON object containing a key 'leads' that holds an array of lead objects. Example: {\"leads\": [{\"business_name\": \"...\", \"why_good_lead\": \"...\", \"suggested_pitch\": \"...\"}]}"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', "")
        
        import re
        import json as json_lib
        
        # Try to parse the json
        try:
            parsed = json_lib.loads(content)
            if 'leads' in parsed:
                return parsed['leads']
            elif isinstance(parsed, list):
                return parsed
            else:
                return []
        except:
            # Fallback regex extraction if the LLM surrounds it with ```json
            match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if match:
                parsed = json_lib.loads(match.group(1))
                if 'leads' in parsed:
                    return parsed['leads']
                elif isinstance(parsed, list):
                    return parsed
            return []
            
    except Exception as e:
        error_msg = f"Failed to generate plan with API: {e}"
        print(error_msg)
        return []

if __name__ == "__main__":
    import processor
    import scorer
    import pandas as pd
    df = processor.process_leads()
    scored_df = scorer.score_leads(df)
    print(generate_daily_plan(scored_df))
