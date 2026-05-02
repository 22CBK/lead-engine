import os
from datetime import datetime
import scraper_maps
import processor
import scorer
import generator

def main():
    print("=== Lead Engine: Daily Run Started ===")
    
    # 1. Scrape new leads
    print("\n--- Step 1: Scraping Google Maps ---")
    scraper_maps.run_scraper()
    
    # 2. Process and Deduplicate
    print("\n--- Step 2: Processing Data ---")
    df = processor.process_leads()
    
    if df.empty:
        print("No new leads to process today. Exiting.")
        return
        
    # 3. Score Leads
    print("\n--- Step 3: Scoring Leads ---")
    scored_df = scorer.score_leads(df)
    
    # 4. Generate AI Outreach Plan
    print("\n--- Step 4: Generating AI Outreach Plan ---")
    ai_results_list = generator.generate_daily_plan(scored_df)
    
    # 5. Save to Database
    print("\n--- Step 5: Updating Database ---")
    processor.save_leads_to_db(scored_df, ai_results_list)
    
    # Optional: Write a simple trigger file so the dashboard knows a run finished
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    with open(os.path.join(outputs_dir, f"{date_str}.md"), 'w') as f:
        f.write("# Run Complete\nData is now in the dashboard.")
    
    print(f"\n=== Run Complete! Output saved to outputs/{date_str}.md ===")
    print("Run `python app.py` to view the dashboard.")

if __name__ == "__main__":
    main()
