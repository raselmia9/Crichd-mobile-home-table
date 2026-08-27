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
            if index == 0:
                continue
                
            cols = row.find_all(['td', 'th'])
            if not cols or len(cols) < 2:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = BASE_URL
            
            col_texts = []
            for col in cols:
                txt = col.text.strip().replace('\n', ' ').replace('\r', '')
                txt = " ".join(txt.split())
                col_texts.append(txt)
            
            # --- ভ্যালিডেশন চেক করে টিম, ইভেন্ট ও টাইম বসানো ---
            for text in col_texts:
                if not text:
                    continue
                
                if re.search(r'\d{2}-\d{2}-\d{4}', text) or re.search(r'\d{2}:\d{2}', text) or "Today" in text or "PM" in text or "AM" in text:
                    if not match_time:
                        match_time = text
                        continue

                if ("vs" in text or "T20" in text or "League" in text or "Test" in text or len(text) < 15) and not team_name and text != match_time:
                    if len(text) < 20 and not event_name:
                        team_name = text
                        continue

                if not event_name and text != match_time and text != team_name:
                    event_name = text
                elif not team_name and text != match_time and text != event_name:
                    team_name = text

            if not team_name and len(col_texts) > 0:
                team_name = col_texts[0]
            if not event_name and len(col_texts) > 1:
                event_name = col_texts[1]
            if not match_time and len(col_texts) > 2:
                match_time = col_texts[2]

            # --- আপনার দেওয়া ফরম্যাট অনুযায়ী সঠিক ওয়াচ পেজ লিংক তৈরির স্মার্ট লজিক ---
            # অগ্রাধিকার ১: যদি টেবিলের ট্যাগ থেকে কোনো ভালো লিংক পাওয়া যায়, সেটিকে চেক করা
            extracted_slug = ""
            for col in cols:
                link_tag = col.find('a')
                if link_tag and link_tag.get('href'):
                    href = link_tag.get('href').strip('/')
                    # যদি লিংকের ভেতরে স্ল্যাশ বা বড় পাথ থাকে, শেষ অংশটি বা মূল স্লগটি নেওয়া
                    parts = href.split('/')
                    if parts:
                        extracted_slug = parts[-1]
                    break
            
            # অগ্রাধিকার ২: যদি ট্যাগ থেকে লিংক না মেলে, তবে 'Event Name' বা 'Team Name' থেকে স্লাগ তৈরি করা
            # যেমন: "India vs Sri Lanka" থেকে হবে "india-vs-sri-lanka"
            if not extracted_slug and event_name:
                extracted_slug = event_name.lower().replace(' vs ', '-vs-').replace(' ', '-')
                # অতিরিক্ত কোনো স্পেশাল ক্যারেক্টার বা ডাবল হাইফেন থাকলে পরিষ্কার করা
                extracted_slug = re.sub(r'[^a-z0-9\-]', '', extracted_slug)
                extracted_slug = re.sub(r'-+', '-', extracted_slug).strip('-')

            if extracted_slug:
                match_link = f"{BASE_URL}/{extracted_slug}"
            else:
                match_link = BASE_URL

            if match_time:
                match_time = match_time.replace('\\n', ' ').strip()

            match_dict = {
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("সঠিক ওয়াচ লিংক ফরম্যাট সহ ডেটা সেভ হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
