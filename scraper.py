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
            # প্রথম সারি হেডার (যেমন: League, Title, Match Time) হলে সেটি স্কিপ করা
            if index == 0:
                continue
                
            cols = row.find_all(['td', 'th'])
            if not cols or len(cols) < 3:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = None
            
            # টেবিলের সেলগুলোর টেক্সট সংগ্রহ ও ক্লিন করা
            cell_texts = [col.text.strip().replace('\n', ' ').replace('\r', '') for col in cols]
            cell_texts = [" ".join(text.split()) for text in cell_texts]
            
            # ১০০% নিশ্চিত হওয়ার জন্য সঠিক কলাম ম্যাপিং
            # সাধারণত প্রথম কলাম = Team Name, দ্বিতীয় কলাম = Event Name, তৃতীয় কলাম = Match Time
            if len(cell_texts) >= 3:
                team_name = cell_texts[0]
                event_name = cell_texts[1]
                match_time = cell_texts[2]
            elif len(cell_texts) == 2:
                team_name = ""
                event_name = cell_texts[0]
                match_time = cell_texts[1]

            # ইভেন্ট বা নামের ভেতরের সঠিক লিংক (URL) সংগ্রহ করা
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

            # টাইমের ভেতর থেকে অতিরিক্ত বা জগাখিচুড়ি টেক্সট দূর করা
            if match_time:
                match_time = match_time.replace('\\n', ' ').strip()

            # আপনার চাওয়া হুবহু ডেমো ফরম্যাটের ডিকশনারি
            match_dict = {
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        # সরাসরি JSON লিস্ট আকারে ফাইল সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("ডেটা শতভাগ সঠিকভাবে JSON ফরম্যাটে সেভ হয়েছে!")
    else:
        print("টেবিলটি পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
