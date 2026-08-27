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
            
            # ১. লোগো বা থাম্বনেইল বের করা (প্রথম কলামের ইমেজ থেকে)
            img_tag = cols[0].find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
                if img_src.startswith('/'):
                    thumbnail_url = BASE_URL + img_src
                elif not img_src.startswith('http'):
                    thumbnail_url = BASE_URL + '/' + img_src
                else:
                    thumbnail_url = img_src

            # ২. টিম নেম বের করা (প্রথম কলামের টেক্সট বা লিংক থেকে)
            team_name = cols[0].text.strip()
            
            # ৩. ইভেন্ট নেম এবং লিংক বের করা (দ্বিতীয় কলাম)
            event_name = cols[1].text.strip()
            link_tag = cols[1].find('a')
            if link_tag and link_tag.get('href'):
                href = link_tag.get('href')
                if href.startswith('/'):
                    match_link = BASE_URL + href
                elif not href.startswith('http'):
                    match_link = BASE_URL + '/' + href
                else:
                    match_link = href

            # ৪. ম্যাচ টাইম বের করা (তৃতীয় কলাম)
            # অনেক সময় সময় বা টাইমার চতুর্থ কলামেও থাকতে পারে, তাই সেফ চেক রাখা হলো
            if len(cols) > 3:
                # যদি চতুর্থ কলামে আসল সময় বা কাউন্টডাউন থাকে
                match_time = cols[3].text.strip() if cols[3].text.strip() else cols[2].text.strip()
            else:
                match_time = cols[2].text.strip()

            # যদি কোনো কারণে দ্বিতীয় কলামে লিংক না পাওয়া যায়, পুরো সারিতে খোঁজা
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
            
        print("ডেটা সফলভাবে সাজিয়ে সেভ করা হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
