from bs4 import BeautifulSoup
import requests
import json

BASE_URL = "https://crichd.mobile"
url = BASE_URL + "/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table') 
    
    matches_list = []
    
    if table:
        rows = table.find_all('tr')
        
        for index, row in enumerate(rows):
            # প্রথম সারিটি হেডার হওয়ায় সেটি স্কিপ করা হচ্ছে
            if index == 0:
                continue
                
            cols = row.find_all(['td', 'th'])
            if not cols or len(cols) < 4:
                continue
                
            # ১. Thumbnail (বাম পাশের লোগো বা আইকন) সংগ্রহ করা
            thumbnail_url = None
            img_tag = cols[0].find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
                if img_src.startswith('/'):
                    thumbnail_url = BASE_URL + img_src
                elif not img_src.startswith('http'):
                    thumbnail_url = BASE_URL + '/' + img_src
                else:
                    thumbnail_url = img_src
            
            # ২. Team Name (পূর্বের League)
            team_name = cols[0].text.strip()
            
            # ৩. Event Name (পূর্বের Title এবং এর ভেতরকার লিংক) সংগ্রহ করা
            event_name = ""
            match_link = None
            
            title_col = cols[1] if len(cols) > 1 else None
            if title_col:
                event_name = title_col.text.strip()
                link_tag = title_col.find('a')
                if link_tag and link_tag.get('href'):
                    href = link_tag.get('href')
                    if href.startswith('/'):
                        match_link = BASE_URL + href
                    elif not href.startswith('http'):
                        match_link = BASE_URL + '/' + href
                    else:
                        match_link = href
            
            # যদি অন্য কোনো কলামেও লিংক থাকে সেটি চেক করা
            if not match_link:
                for col in cols:
                    link_tag = col.find('a')
                    if link_tag and link_tag.get('href'):
                        href = link_tag.get('href')
                        if href.startswith('/'):
                            match_link = BASE_URL + href
                        elif not href.startswith('http'):
                            match_link = BASE_URL + '/' + href
                        else:
                            match_link = href
                        break

            # ৪. Match Time সংগ্রহ করা
            match_time = cols[2].text.strip() if len(cols) > 2 else ""
            
            # ডিকশনারি তৈরি
            match_dict = {
                "Thumbnail": thumbnail_url,
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        # সরাসরি JSON লিস্ট আকারে ফাইল সেভ করা (Timestamp বা অতিরিক্ত কিছু থাকবে না)
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("ডেটা সফলভাবে JSON ফরম্যাটে সেভ করা হয়েছে!")
    else:
        print("টেবিলটি পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা সম্ভব হয়নি।")
