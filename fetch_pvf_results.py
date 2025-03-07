import json
import os
from fetch_pvf import PVF

def fetch_and_save_matches():
    # Create a LOVB instance
    pvf = PVF()
    
    # Get matches with logos
    matches_with_logos = pvf.fetch_schedule(when='past')
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Define the output filename
    output_file = os.path.join("data", "pvf_results.json")
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(matches_with_logos, f, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {output_file}")
    return matches_with_logos

if __name__ == "__main__":
    result = fetch_and_save_matches()
    print(f"Successfully processed {len(result)} matches")