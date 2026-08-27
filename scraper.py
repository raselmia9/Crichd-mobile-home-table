from bs4 import BeautifulSoup
import requests
import json
import re

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
            if not cols or len(cols) < 2:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = None
            
            # সারির সমস্ত কলাম থেকে ক্লিন টেক্সটগুলো সংগ্রহ করা
            col_texts = []
            for col in cols:
                txt = col.text.strip().replace('\n', ' ').replace('\r', '')
                txt = " ".join(txt.split())
                col_texts.append(txt)
            
            # --- লজিক্যাল ভ্যালিডেশন চেক এবং সঠিক জায়গায় মান বসানো ---
            for text in col_texts:
                if not text:
                    continue
                
                # ১. টাইম চেক করার লজিক (যদি লেখায় তারিখ বা সময়ের প্যাটার্ন যেমন ড্যাশ '-' বা কোলন ':' থাকে)
                # যেমন: 23-08-2026 বা 10:00 বা Today ইত্যাদি থাকলে সেটি Match Time হবে
                if re.search(r'\d{2}-\d{2}-\d{4}', text) or re.search(r'\d{2}:\d{2}', text) or "Today" in text or "PM" in text or "AM" in text:
                    if not match_time:
                        match_time = text
                        continue

                # ২. টিম নেম চেক করার লজিক (সাধারণত ছোট হয় বা বনাম "vs" থাকে, যেমন: IND vs SL, CPL T20)
                if ("vs" in text or "T20" in text or "League" in text or "Test" in text or len(text) < 15) and not team_name and text != match_time:
                    # যদি এটি ইভেন্টের নাম না হয়ে ছোট শর্ট ফরম্যাট হয়
                    if len(text) < 20 and not event_name:
                        team_name = text
                        continue

                # ৩. ইভেন্ট নেম চেক করার লজিক (বড় নাম, যেমন: India vs Sri Lanka, Caribbean Premier League)
                if not event_name and text != match_time and text != team_name:
                    event_name = text
                elif not team_name and text != match_time and text != event_name:
                    team_name = text

            # ফলব্যাক সেফটি: যদি কোনো কারণে টিম বা ইভেন্ট ফাঁকা থাকে, কলামের পজিশন অনুযায়ী বসবে
            if not team_name and len(col_texts) > 0:
                team_name = col_texts[0]
            if not event_name and len(col_texts) > 1:
                event_name = col_texts[1]
            if not match_time and len(col_texts) > 2:
                match_time = col_texts[2]

            # লিংক (URL) সংগ্রহ করা
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

            # অতিরিক্ত ক্লিনিং
            if match_time:
                match_time = match_time.replace('\\n', ' ').strip()

            match_dict = {
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        # JSON ফাইলে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("লজিক চেক করে সফলভাবে ডেটা সেভ করা হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
