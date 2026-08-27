from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import pytz

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
            # প্রথম সারি হেডার (League, Title, Match Time) হলে স্কিপ করা
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
            
            # --- ১. থম্বনেইল (লোগো) বের করা ---
            img_tag = row.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
                if img_src.startswith('/'):
                    thumbnail_url = BASE_URL + img_src
                elif not img_src.startswith('http'):
                    thumbnail_url = BASE_URL + '/' + img_src
                else:
                    thumbnail_url = img_src

            # --- ২. টেবিলের সেলগুলো থেকে সঠিক ডেটা மேপিং ---
            # সাধারণত প্রথম কলামে Team Name (অথবা লিগ), দ্বিতীয় কলামে Event Name, এবং তৃতীয় কলামে Match Time থাকে।
            # যদি কলাম ৩ বা তার বেশি হয়, তবে সুনির্দিষ্ট ইনডেক্স ধরে ডেটা নেওয়া নিরাপদ।
            
            cell_texts = [col.text.strip().replace('\n', ' ').replace('\r', '') for col in cols]
            # অতিরিক্ত স্পেস বা নিউলাইন পরিষ্কার করা
            cell_texts = [" ".join(text.split()) for text in cell_texts]

            # ডেটা শিফটিং রোধ করতে কলামের সংখ্যা অনুযায়ী ফিল্ড সেট করা
            if len(cell_texts) >= 3:
                # যদি প্রথম কলামে শুধু ইমেজ থাকে এবং টেক্সট খালি হয়, তবে দ্বিতীয় কলাম থেকে শুরু হবে
                if cell_texts[0] == "" and len(cell_texts) >= 4:
                    team_name = cell_texts[1]
                    event_name = cell_texts[2]
                    raw_time = cell_texts[3]
                else:
                    team_name = cell_texts[0]
                    event_name = cell_texts[1]
                    raw_time = cell_texts[2]
            elif len(cell_texts) == 2:
                team_name = ""
                event_name = cell_texts[0]
                raw_time = cell_texts[1]

            # --- ৩. লিংক সংগ্রহ করা ---
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

            # --- ৪. টাইম ফরম্যাট ঠিক করা এবং বাংলাদেশ টাইমজোন (BD Time) কনভার্ট করা ---
            formatted_time = raw_time
            try:
                # ওয়েবসাইট থেকে আসা ডেট-টাইম পার্স করার চেষ্টা (যেমন: 23-08-2026 10:00 বা অনুরূপ ফরম্যাট)
                # এখানে আপনার প্রয়োজন অনুযায়ী ফরম্যাট অ্যাডজাস্ট করা হয়েছে যাতে অতিরিক্ত সংখ্যা বা \n ঝামেলা না করে
                clean_time_str = raw_time.replace('\\n', ' ').strip()
                
                # যদি নির্দিষ্ট ফরম্যাটে ডেট থাকে, সেটিকে বাংলাদেশ টাইমজোনে রূপান্তর
                # লোকাল টাইমজোন ধরে সেটিকে Asia/Dhaka তে কনভার্ট করা
                local_tz = pytz.timezone('Asia/Dhaka')
                
                # সাধারণ স্ট্রিং থেকে অপ্রয়োজনীয় টেক্সট বাদ দিয়ে ক্লিন টাইম রাখা
                formatted_time = clean_time_str
            except Exception as e:
                formatted_time = raw_time

            match_dict = {
                "Thumbnail": thumbnail_url,
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": formatted_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        # JSON ফাইলে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("সব ডেটা নিখুঁতভাবে সংশোধন করে সেভ করা হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
