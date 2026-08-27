from bs4 # BeautifulSoup and other necessary imports
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
        rows = table.find_all('tr')[1:] # হেডার বাদ দিয়ে
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 3:
                continue
                
            team_name = ""
            event_name = ""
            match_time = ""
            match_link = BASE_URL
            
            # ১. টিম নেম বা প্রথম কলামের তথ্য
            if len(cols) > 0:
                team_name = cols[0].get_text(strip=True)
            
            # ২. ইভেন্টের নাম এবং আপনার পছন্দসই আসল ওয়াচ পেজ লিংক বের করার লজিক
            if len(cols) > 1:
                title_col = cols[1]
                event_name = title_col.get_text(strip=True)
                
                # টেবিলের ভেতর থেকে এমন লিংক খোঁজা যেখানে 'schedule' নেই (সঠিক ওয়াচ লিংক)
                all_links = row.find_all('a')
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
            
            # ৩. ম্যাচ টাইম বা সময়ের অংশটুকু নিখুঁতভাবে আলাদা করা
            time_parts = []
            if len(cols) > 2:
                t1 = cols[2].get_text(strip=True)
                if t1:
                    time_parts.append(t1)
            
            if len(cols) > 3:
                t2 = cols[3].get_text(strip=True)
                if t2 and "watch" not in t2.lower():
                    time_parts.append(t2)
            
            match_time = " ".join(time_parts)

            # যদি কোনো কারণে টিম নেম খালি থাকে, তবে ইভেন্ট নেম বসিয়ে দেওয়া
            if not team_name and event_name:
                team_name = event_name

            matches_list.append({
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            })
            
        # ফাইল সেভ
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("ডেটা এবং ওয়াচ পেজের লিংক সফলভাবে ফিক্স করা হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
