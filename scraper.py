from playwright.sync_api import sync_playwright
import json

BASE_URL = "https://crichd.mobile"

def scrape_matches():
    with sync_playwright() as p:
        # হেডলেস ব্রাউজার চালু করা
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("ওয়েবসাইট ভিজিট করা হচ্ছে...")
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_selector('table', timeout=10000)
        
        matches_list = []
        
        # টেবিলের রো গুলোর সংখ্যা বের করা (প্রথম হেডার বাদে)
        rows = page.locator('table tr').all()[1:]
        
        for row in rows:
            cols = row.locator('td, th').all()
            if len(cols) < 3:
                continue
                
            team_name = cols[0].inner_text().strip()
            event_name = cols[1].inner_text().strip()
            match_time = cols[2].inner_text().strip()
            
            if len(cols) > 3:
                extra_text = cols[3].inner_text().strip()
                if extra_text:
                    match_time = f"{match_time} {extra_text}"

            # সবুজ টাইটেল বা লিঙ্কে ক্লিক করে আসল ওয়াচ পেজের লিংক বের করার লজিক
            watch_link = BASE_URL
            try:
                link_element = cols[1].locator('a')
                if link_element.count() > 0:
                    # নতুন পেজ ওপেন না করে বা ক্লিক করে রিডাইরেক্ট ইউআরএল ক্যাপচার করা
                    with page.expect_navigation(timeout=5000):
                        link_element.first.click()
                    watch_link = page.url
                    # কাজ শেষে আবার হোমপেজে ফিরে আসা
                    page.goto(BASE_URL, timeout=60000)
                    page.wait_for_selector('table', timeout=10000)
                else:
                    # যদি ট্যাগ না থাকে, href অ্যাট্রিবিউট সরাসরি নেওয়া
                    href = link_element.first.get_attribute('href')
                    if href:
                        watch_link = href if href.startswith('http') else BASE_URL + href
            except Exception:
                # ক্লিক করতে সমস্যা হলে বা টাইমআউট হলে বেস লিংক বা ফলব্যাক রাখা
                watch_link = BASE_URL

            matches_list.append({
                "Team Name": team_name,
                "Event Name": event_name,
                "Match Time": match_time,
                "Link": watch_link
            })
            
        browser.close()
        
        # JSON ফাইলে সেভ করা
        with open('match_table.json', 'w', encoding='utf-8') as f:
            json.dump(matches_list, f, ensure_ascii=False, indent=4)
            
        print("সঠিক ওয়াচ পেজ লিংক সহ ডেটা সফলভাবে সেভ হয়েছে!")

if __name__ == "__main__":
    scrape_matches()
