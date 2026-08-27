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
            
            # টেবিলের কলামগুলো থেকে সুনির্দিষ্টভাবে ডাটা বের করা
            for i, col in enumerate(cols):
                text = col.text.strip()
                
                # ১. প্রথম কলাম: লোগো (Thumbnail) এবং Team Name
                if i == 0:
                    team_name = text
                    img_tag = col.find('img')
                    if img_tag and img_tag.get('src'):
                        img_src = img_tag.get('src')
                        if img_src.startswith('/'):
                            thumbnail_url = BASE_URL + img_src
                        elif not img_src.startswith('http'):
                            thumbnail_url = BASE_URL + '/' + img_src
                        else:
                            thumbnail_url = img_src
                            
                # ২. দ্বিতীয় কলাম: Event Name এবং Link
                elif i == 1:
                    event_name = text
                    link_tag = col.find('a')
                    if link_tag and link_tag.get('href'):
                        href = link_tag.get('href')
                        if href.startswith('/'):
                            match_link = BASE_URL + href
                        elif not href.startswith('http'):
                            match_link = BASE_URL + '/' + href
                        else:
                            match_link = href
                            
                # ৩. তৃতীয় কলাম: Match Time
                elif i == 2:
                    match_time = text

            # যদি অন্য কোনো কলামে লিংক থাকে এবং কলাম ২ এ না পাওয়া যায়
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
            
        print("সঠিক ফরম্যাটে ডেটা সেভ হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
