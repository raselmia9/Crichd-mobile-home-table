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
            # প্রথম সারি হেডার (League, Title, Match Time) হলে স্কিপ করা
            if index == 0:
                continue
                
            cols = row.find_all(['td', 'th'])
            if not cols or len(cols) < 3:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = None
            
            # ১. প্রথম কলাম থেকে Team Name (League) নেওয়া
            team_name = cols[0].text.strip().replace('\n', ' ').strip()
            team_name = " ".join(team_name.split())
            
            # ২. দ্বিতীয় কলাম থেকে Event Name (Title) এবং আসল ওয়াচ পেজ লিংক (href) নেওয়া
            title_col = cols[1]
            event_name = title_col.text.strip().replace('\n', ' ').strip()
            event_name = " ".join(event_name.split())
            
            # Title কলামের ভেতরে থাকা <a> ট্যাগ থেকে সরাসরি আসল লিংক সংগ্রহ করা
            link_tag = title_col.find('a')
            if link_tag and link_tag.get('href'):
                href = link_tag.get('href')
                if href.startswith('/'):
                    match_link = BASE_URL + href
                elif not href.startswith('http'):
                    match_link = BASE_URL + '/' + href
                else:
                    match_link = href
            
            # যদি Title কলামে লিংক না পাওয়া যায়, পুরো সারির যেকোনো <a> ট্যাগ থেকে খোঁজা
            if not match_link:
                for col in cols:
                    l_tag = col.find('a')
                    if l_tag and l_tag.get('href'):
                        href = l_tag.get('href')
                        if href.startswith('/'):
                            match_link = BASE_URL + href
                        elif not href.startswith('http'):
                            match_link = BASE_URL + '/' + href
                        else:
                            match_link = href
                        break
            
            # যদি তবুও লিংক না থাকে, ফলব্যাক হিসেবে বেস ইউআরএল বা ডামি রাখা
            if not match_link:
                match_link = BASE_URL

            # ৩. তৃতীয় কলাম থেকে Match Time নেওয়া (কাউন্টডাউন বা আসল সময় সহ)
            match_time = cols[2].text.strip().replace('\n', ' ').strip()
            match_time = " ".join(match_time.split())
            
            # যদি চতুর্থ কলামে অতিরিক্ত সময় বা কাউন্টডাউন থাকে
            if len(cols) > 3:
                extra_col = cols[3].text.strip().replace('\n', ' ').strip()
                extra_col = " ".join(extra_col.split())
                if extra_col:
                    match_time = f"{match_time} {extra_col}".strip()

            match_dict = {
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            }
            
            matches_list.append(match_dict)
            
        # সরাসরি সঠিক JSON লিস্ট আকারে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("টাইটেল কলামের আসল লিংকসহ ডেটা সফলভাবে সেভ হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
