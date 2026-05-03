import os
from datetime import datetime
import scraper_maps
import processor
import scorer
import generator
import status_tracker

def main():
    print("=== Lead Engine: Daily Run Started ===")
    status_tracker.update_status("running", "Initializing engine...", 5)
    
    # 1. Scrape new leads
    print("\n--- Step 1: Scraping Google Maps ---")
    status_tracker.update_status("running", "Scraping Google Maps...", 10)
    scraper_maps.run_scraper()
    
    # 2. Process and Deduplicate
    print("\n--- Step 2: Processing Data ---")
    status_tracker.update_status("running", "Processing and deduplicating data...", 40)
    df = processor.process_leads()
    
    if df.empty:
        print("No new leads to process today. Exiting.")
        status_tracker.update_status("done", "No new leads found today.", 100)
        return
        
    # 3. Score Leads
    print("\n--- Step 3: Scoring Leads ---")
    status_tracker.update_status("running", "Scoring leads...", 45)
    scored_df = scorer.score_leads(df)
    
    # 4. Generate AI Outreach Plan
    print("\n--- Step 4: Generating AI Outreach Plan ---")
    status_tracker.update_status("running", "Analyzing leads with AI...", 50)
    ai_results_list = generator.generate_daily_plan(scored_df)
    
    # 5. Save to Database
    print("\n--- Step 5: Updating Database ---")
    status_tracker.update_status("running", "Saving pitches to database...", 90)
    processor.save_leads_to_db(scored_df, ai_results_list)
    
    # Optional: Write a simple trigger file so the dashboard knows a run finished
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    with open(os.path.join(outputs_dir, f"{date_str}.md"), 'w') as f:
        f.write("# Run Complete\nData is now in the dashboard.")
    
    print(f"\n=== Run Complete! Output saved to outputs/{date_str}.md ===")
    print("Run `python app.py` to view the dashboard.")
    status_tracker.update_status("done", "Run complete!", 100)

if __name__ == "__main__":
    main()
