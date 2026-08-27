from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime, timedelta

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
            # প্রথম সারি হেডার হলে স্কিপ করা
            if index == 0:
                continue
                
            cols = row.find_all(['td', 'th'])
            if not cols or len(cols) < 3:
                continue
                
            thumbnail_url = None
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = None
            
            # ১. লোগো বা থাম্বনেইল বের করা
            img_tag = row.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
                if img_src.startswith('/'):
                    thumbnail_url = BASE_URL + img_src
                elif not img_src.startswith('http'):
                    thumbnail_url = BASE_URL + '/' + img_src
                else:
                    thumbnail_url = img_src

            # ২. কলামের টেক্সটগুলো পরিষ্কার করে নেওয়া
            cell_texts = [col.text.strip().replace('\n', ' ').replace('\r', '') for col in cols]
            cell_texts = [" ".join(text.split()) for text in cell_texts]

            # ৩. সঠিক কলাম ম্যাপিং (যাতে কোনো ডেটা এলোমেলো বা শিফট না হয়)
            if len(cell_texts) >= 3:
                team_name = cell_texts[0]
                event_name = cell_texts[1]
                match_time = cell_texts[2]
            elif len(cell_texts) == 2:
                team_name = ""
                event_name = cell_texts[0]
                match_time = cell_texts[1]

            # ৪. লিংক সংগ্রহ করা
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

            # ৫. টাইমের ভেতর থেকে অতিরিক্ত \n বা জগাখিচুড়ি দূর করা
            if match_time:
                match_time = match_time.replace('\\n', ' ').strip()

            match_dict = {
                "Thumbnail": thumbnail_url,
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        # JSON ফাইলে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("সফলভাবে ডেটা আপডেট হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
