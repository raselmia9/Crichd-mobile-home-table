from bs4 import BeautifulSoup
import requests
import json

BASE_URL = "https://crichd.mobile"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.5"
}

# টাইমআউট (timeout=10) যুক্ত করা হয়েছে যাতে সার্ভার স্লো থাকলেও স্ক্রিপ্ট আটকে না থাকে
response = requests.get(BASE_URL + "/", headers=headers, timeout=10)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table') 
    
    matches_list = []
    
    if table:
        # সরাসরি রো ফেচ করা (হেডার বাদ দিয়ে)
        rows = table.find_all('tr')[1:]
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 3:
                continue
                
            # ১. Team Name (প্রথম কলাম)
            team_name = cols[0].get_text(strip=True)
            
            # ২. Event Name & Watch Link (দ্বিতীয় কলাম - Title)
            title_col = cols[1]
            event_name = title_col.get_text(strip=True)
            
            match_link = BASE_URL
            link_tag = title_col.find('a')
            if link_tag and link_tag.get('href'):
                href = link_tag.get('href')
                if href.startswith('http'):
                    match_link = href
                else:
                    match_link = BASE_URL + ('/' if not href.startswith('/') else '') + href

            # ৩. Match Time (তৃতীয় কলাম এবং যদি চতুর্থ কলামে কাউন্টডাউন থাকে)
            match_time = cols[2].get_text(strip=True)
            if len(cols) > 3:
                extra_text = cols[3].get_text(strip=True)
                if extra_text:
                    match_time = f"{match_time} {extra_text}"

            matches_list.append({
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            })
            
        # ফাইল সেভ
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("খুব দ্রুত সফলভাবে ডেটা সেভ হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
