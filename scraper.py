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
        rows = table.find_all('tr')[1:] # হেডার বাদ দিয়ে
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 3:
                continue
                
            # ১. Team Name (প্রথম কলাম)
            team_name = cols[0].get_text(strip=True)
            
            # ২. Event Name (দ্বিতীয় কলাম - Title)
            title_col = cols[1]
            event_name = title_col.get_text(strip=True)
            
            # ৩. সঠিক ওয়াচ পেজ লিংক খুঁজে বের করার লজিক (যেখানে 'schedule' নেই)
            match_link = BASE_URL
            
            # টাইটেল বা পুরো সারির সমস্ত <a> ট্যাগ চেক করা
            all_links = row.find_all('a')
            for a_tag in all_links:
                href = a_tag.get('href')
                if href:
                    href = href.strip()
                    # শর্ত: লিংকের ভেতরে যদি 'schedule' লেখা থাকে, তবে সেটি ধরব না!
                    if 'schedule' not in href.lower():
                        if href.startswith('http'):
                            match_link = href
                        else:
                            clean_href = href.lstrip('/')
                            match_link = f"{BASE_URL}/{clean_href}"
                        break # সঠিক লিংক পেয়ে গেলে লুপ ভেঙে বের হয়ে যাবো

            # ৪. Match Time (তৃতীয় কলাম এবং কাউন্টডাউন)
            match_time = cols[2].get_text(strip=True)
            if len(cols) > 3:
                extra_text = cols[3].get_text(strip=True)
                if extra_text:
                    match_time = f"{match_time} {extra_text}"

            matches_list.append({
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": match_link
            })
            
        # ফাইল সেভ
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("সিডিউল লিংক বাদ দিয়ে সঠিক ওয়াচ পেজের লিংক সফলভাবে খুঁজে বের করা হয়েছে!")
    else:
        print("টেবিল পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা যায়নি।")
