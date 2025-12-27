import requests
from bs4 import BeautifulSoup
import json
import os

# NCKU CSIE Faculty Page
URL = "https://www.csie.ncku.edu.tw/zh-hant/members/csie"

def scrape_ncku_professors():
    """
    Scrapes NCKU CSIE faculty data and saves it to data/professors.json.
    """
    print(f"🕷️ Scraping {URL}...")
    try:
        response = requests.get(URL, timeout=15)
        if response.status_code != 200:
            print(f"❌ Failed to retrieve page (Status: {response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        professors = []

        teacher_blocks = soup.find_all("div", class_="member-list-item") 
        
        if not teacher_blocks:
            print("⚠️ specific HTML class not found. Using generic structure...")
            teacher_blocks = soup.find_all("div", class_="row") 

        for block in teacher_blocks:
            try:
                name = block.find("h4").get_text(strip=True) if block.find("h4") else "Unknown"
                # Extract email, often in an <a> tag with 'mailto:'
                email_tag = block.find("a", href=lambda x: x and "mailto:" in x)
                email = email_tag.get_text(strip=True) if email_tag else "N/A"
                
                # Extract research areas (usually in a paragraph or list)
                desc = block.get_text(strip=True)
                
                professors.append({
                    "name": name,
                    "email": email,
                    "raw_info": desc # Save raw text for vector embedding
                })
            except:
                continue

        # Save to JSON
        os.makedirs("data", exist_ok=True)
        with open("data/professors.json", "w", encoding="utf-8") as f:
            json.dump(professors, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully saved {len(professors)} professors to data/professors.json")
        return professors

    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []

if __name__ == "__main__":
    scrape_ncku_professors()