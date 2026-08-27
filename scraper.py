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
            
            # ১. Thumbnail (লোগো) এবং Team Name বের করা (সাধারণত প্রথম কলামে থাকে)
            first_col = cols[0]
            img_tag = first_col.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
                if img_src.startswith('/'):
                    thumbnail_url = BASE_URL + img_src
                elif not img_src.startswith('http'):
                    thumbnail_url = BASE_URL + '/' + img_src
                else:
                    thumbnail_url = img_src
            
            # প্রথম কলামের টেক্সট থেকে ইমেজ ট্যাগ বাদ দিয়ে শুধু নাম নেওয়া
            for img in first_col.find_all('img'):
                img.decompose()
            team_name = first_col.text.strip()
            
            # ২. Event Name এবং Link বের করা (দ্বিতীয় কলাম)
            if len(cols) > 1:
                second_col = cols[1]
                event_name = second_col.text.strip()
                link_tag = second_col.find('a')
                if link_tag and link_tag.get('href'):
                    href = link_tag.get('href')
                    if href.startswith('/'):
                        match_link = BASE_URL + href
                    elif not href.startswith('http'):
                        match_link = BASE_URL + '/' + href
                    else:
                        match_link = href
            
            # ৩. Match Time বের করা (তৃতীয় কলাম)
            if len(cols) > 2:
                match_time = cols[2].text.strip()
            
            # যদি দ্বিতীয় কলামে লিংক না পাওয়া যায়, পুরো সারিতে খোঁজা
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
            
        print("সঠিক ফরম্যাটে ডেটা সফলভাবে আপডেট হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
