from bs4 import BeautifulSoup
import requests
import json
import datetime

url = "https://crichd.mobile/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # টেবিলটি খুঁজে বের করার কোড (ওয়েবসাইটের স্ট্রাকচার অনুযায়ী টেবিল সিলেক্ট করতে হবে)
    # সাধারণত টেবিল <table> ট্যাগের মধ্যে থাকে
    table = soup.find('table') 
    
    match_data = []
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            match_data.append(cols)
            
        # ডাটা সেভ করার জন্য
        data = {
            "timestamp": str(datetime.datetime.now()),
            "matches": match_data
        }
        
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("ট্যাবলেট সফলভাবে সেভ করা হয়েছে!")
    else:
        print("টেবিলটি পাওয়া যায়নি।")
else:
    print("ওয়েবসাইট ভিজিট করা সম্ভব হয়নি।")
