from bs4 import BeautifulSoup
import requests
import json

BASE_URL = "https://crichd.mobile"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# আন্তর্জাতিক সব প্রধান ক্রিকেট খেলুড়ে দেশের জন্য কোড ম্যাপিং
ALL_COUNTRIES = {
    "india": "in", "ind": "in",
    "sri lanka": "lk", "sl": "lk",
    "pakistan": "pk", "pak": "pk",
    "england": "gb-eng", "eng": "gb-eng",
    "australia": "au", "aus": "au",
    "bangladesh": "bd", "ban": "bd",
    "south africa": "za", "rsa": "za", "sa": "za",
    "new zealand": "nz", "nz": "nz",
    "west indies": "jm", "wi": "jm",
    "afghanistan": "af", "afg": "af",
    "ireland": "ie", "ire": "ie",
    "zimbabwe": "zw", "zim": "zw",
    "netherlands": "nl", "ned": "nl",
    "scotland": "sco", "sco": "sco"
}

def get_logo(team_name):
    name_lower = team_name.lower().strip()
    
    # ১. আন্তর্জাতিক দেশের নামের সাথে মিলে গেলে ফ্ল্যাগ সিডিএন লিংক দেওয়া
    for country, code in ALL_COUNTRIES.items():
        if country in name_lower:
            return f"https://flagcdn.com/w80/{code}.png"
            
    # ২. ডোমেস্টিক লিগের ক্ষেত্রে আপনার দেওয়া সিডিএন লিংক এবং শেষে .png যুক্ত করা
    # যেমন: http://logocdn.wapsite.me/images/CPL.png
    # লিগের মূল শব্দটি বা প্রথম অংশটি নিয়ে বড় হাতের (Uppercase) করে লিংকের সাথে জুড়ে দেওয়া
    clean_name = name_lower.replace("t20", "").replace("league", "").strip()
    words = clean_name.split()
    if words:
        league_key = words[0].upper() # যেমন CPL, TNPL ইত্যাদি
        return f"http://logocdn.wapsite.me/images/{league_key}.png"
        
    # ফলব্যাক ডিফল্ট লোগো
    return "http://logocdn.wapsite.me/images/DEFAULT.png"

response = requests.get(BASE_URL + "/", headers=headers, timeout=10)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table') 
    
    matches_list = []
    
    if table:
        rows = table.find_all('tr')
        
        # ডায়নামিক হেডার ম্যাপিং
        headers_map = {}
        header_row = rows[0]
        for idx, th in enumerate(header_row.find_all(['th', 'td'])):
            header_text = th.get_text(strip=True).lower()
            if 'league' in header_text:
                headers_map['league'] = idx
            elif 'title' in header_text:
                headers_map['title'] = idx
            elif 'match time' in header_text or 'time' in header_text:
                headers_map['time'] = idx

        # ডেটা রো প্রসেস করা
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 3:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = BASE_URL
            
            # League কলাম
            if 'league' in headers_map and len(cols) > headers_map['league']:
                team_name = cols[headers_map['league']].get_text(strip=True)
            elif len(cols) > 0:
                team_name = cols[0].get_text(strip=True)

            # Title কলাম (ইভেন্ট নেম এবং সঠিক ওয়াচ পেজ লিংক)
            title_col = None
            if 'title' in headers_map and len(cols) > headers_map['title']:
                title_col = cols[headers_map['title']]
            elif len(cols) > 1:
                title_col = cols[1]

            if title_col:
                event_name = title_col.get_text(strip=True)
                
                all_links = title_col.find_all('a')
                for a_tag in all_links:
                    href = a_tag.get('href')
                    if href:
                        href = href.strip()
                        if 'schedule' not in href.lower():
                            if href.startswith('http'):
                                match_link = href
                            else:
                                clean_href = href.lstrip('/')
                                match_link = f"{BASE_URL}/{clean_href}"
                            break

            # Match Time কলাম
            time_parts = []
            if 'time' in headers_map and len(cols) > headers_map['time']:
                t1 = cols[headers_map['time']].get_text(strip=True)
                if t1:
                    time_parts.append(t1)
                if len(cols) > headers_map['time'] + 1:
                    t2 = cols[headers_map['time'] + 1].get_text(strip=True)
                    if t2 and "watch" not in t2.lower():
                        time_parts.append(t2)
            else:
                if len(cols) > 2:
                    t1 = cols[2].get_text(strip=True)
                    if t1:
                        time_parts.append(t1)
                if len(cols) > 3:
                    t2 = cols[3].get_text(strip=True)
                    if t2 and "watch" not in t2.lower():
                        time_parts.append(t2)

            match_time = " ".join(time_parts)

            if not team_name and event_name:
                team_name = event_name

            # অটো লোগো জেনারেট করা
            team_logo = get_logo(team_name)

            matches_list.append({
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link,
                "Team Logo": team_logo
            })
            
        # JSON ফাইলে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("আন্তর্জাতিক পতাকা এবং ডোমেস্টিক লিগের কাস্টম সিডিএন লোগো সহ ডেটা সফলভাবে সেভ হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
