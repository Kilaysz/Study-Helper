import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin

# NCKU CSIE Faculty Page
BASE_URL = "https://www.csie.ncku.edu.tw"
URL = f"{BASE_URL}/zh-hant/members/csie"

def scrape_ncku_professors():
    print(f"🕷️ Scraping {URL}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"❌ Failed to retrieve page (Status: {response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        professors = []

        # Find all potential blocks
        potential_blocks = soup.find_all("div", class_=re.compile(r"(row|item|col|d-flex)"))
        seen_names = set()

        for block in potential_blocks:
            raw_text = block.get_text(separator=" ", strip=True)
            
            # --- 🛡️ FILTER 1: Must look like a person ---
            if "@" not in raw_text and "教授" not in raw_text:
                continue

            # --- 🛡️ FILTER 2: Ignore Department Office ---
            if "em62500@email.ncku.edu.tw" in raw_text:
                continue

            # --- 🛡️ FILTER 3: Ignore Giant Containers (THE FIX) ---
            # If the text is massive (holds multiple people), skip it.
            # A normal profile is usually 200-400 chars.
            if len(raw_text) > 800:
                continue

            # Extract Name
            name = "Unknown"
            profile_url = "N/A"
            
            header_link = block.find(["h4", "h3", "h5", "strong"])
            
            if header_link:
                name = header_link.get_text(strip=True)
                a_tag = header_link.find("a") if not header_link.name == 'a' else header_link
                if not a_tag:
                    a_tag = block.find("a", href=True)
                if a_tag and a_tag.has_attr("href"):
                    profile_url = urljoin(BASE_URL, a_tag["href"])
            else:
                name = " ".join(raw_text.split()[:3])

            # --- 🛡️ FILTER 4: Ignore Junk Keywords ---
            junk_keywords = ["台南市", "交通資訊", "系所簡介", "檔案下載", "National", "Cheng", "Kung", "師資", "Faculty"]
            if any(k in name for k in junk_keywords):
                continue
            
            if name[0].isdigit():
                continue
                
            # Filter invalid header links
            if profile_url.strip().endswith("/members/csie"):
                continue

            # Deduplication
            if name in seen_names or len(name) > 30: continue
            seen_names.add(name)

            # Extract Details
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
            email = email_match.group(0) if email_match else "N/A"

            lab_match = re.search(r'(\S*實驗室)', raw_text)
            lab_name = lab_match.group(0) if lab_match else "N/A"

            if len(raw_text) > 20: 
                professors.append({
                    "name": name,
                    "email": email,
                    "lab": lab_name,
                    "profile_url": profile_url,
                    "raw_info": raw_text
                })

        # Save to JSON
        os.makedirs("data", exist_ok=True)
        with open("data/professors.json", "w", encoding="utf-8") as f:
            json.dump(professors, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(professors)} professors (Cleaned container issues).")
        return professors

    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []

if __name__ == "__main__":
    scrape_ncku_professors()