from bs4 import BeautifulSoup
import requests
import json

BASE_URL = "https://crichd.mobile"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(BASE_URL + "/", headers=headers, timeout=10)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table') 
    
    matches_list = []
    
    if table:
        rows = table.find_all('tr')
        
        # ১. ডায়নামিক হেডার ম্যাপিং (হেডার চেক করে কলামের সঠিক পজিশন চিনে নেওয়া)
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

        # ডেটা রো গুলো প্রসেস করা (হেডার বাদ দিয়ে)
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 3:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = BASE_URL
            
            # হেডার ম্যাপিং অনুযায়ী সুনির্দিষ্ট কলাম থেকে ডেটা তোলা
            # League কলাম
            if 'league' in headers_map and len(cols) > headers_map['league']:
                team_name = cols[headers_map['league']].get_text(strip=True)
            elif len(cols) > 0:
                team_name = cols[0].get_text(strip=True)

            # Title কলাম (যেখান থেকে ইভেন্ট নেম এবং সঠিক ওয়াচ পেজ লিংক দুটোই নেওয়া হবে)
            title_col = None
            if 'title' in headers_map and len(cols) > headers_map['title']:
                title_col = cols[headers_map['title']]
            elif len(cols) > 1:
                title_col = cols[1]

            if title_col:
                event_name = title_col.get_text(strip=True)
                
                # Title কলামের ভেতর থেকে এমন লিংক খোঁজা যেখানে 'schedule' নেই
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

            # Match Time কলাম (টাইমের লেখা যাতে জগাখিচুড়ি না পাকায়)
            time_parts = []
            if 'time' in headers_map and len(cols) > headers_map['time']:
                t1 = cols[headers_map['time']].get_text(strip=True)
                if t1:
                    time_parts.append(t1)
                # যদি পরের কলামেও কাউন্টডাউন বা টাইম থাকে
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

            # ফলব্যাক চেক
            if not team_name and event_name:
                team_name = event_name

            matches_list.append({
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            })
            
        # JSON ফাইলে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("সঠিক হেডার ম্যাপিং এবং টাইটেল লিংক সহ ডেটা সফলভাবে সেভ হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
