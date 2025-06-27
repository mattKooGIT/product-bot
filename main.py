import os, time, smtplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

PRODUCT_URL = "https://detail.tmall.com/item.htm?detail_redpacket_pop=true&id=877042114592"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def check_stock_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    
    #fake chinese region browser
    options.add_argument('--lang=zh-CN')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         'AppleWebKit/537.36 (KHTML, like Gecko)'
                         'Chrome/114.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.implicitly_wait(10)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    size_options = soup.find_all("div", class_="_4nNipe17pV--valueItem--ee898cc0")

    for option in size_options:
        class_list = option.get("class", [])
        if any("isDisabled" in cls for cls in class_list):
            continue
        else:
            return True  # at least one size is in stock

    return False

def send_email(url):
    msg = MIMEText(f"The item is back in stock! Check it out here:\n\n{url}")
    msg['Subject'] = '🔔 Taobao/Tmall Item Back In Stock!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
    print("EMAIL SENT!")

def main_loop():
    while True:
        print("🔄 Checking stock status...")
        try:
            if check_stock_with_selenium(PRODUCT_URL):
                print("✅ Item is in stock!")
                send_email(PRODUCT_URL)
                break
            else:
                print("❌ Still out of stock.")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        time.sleep(3600)  # wait 1 hour before checking again

if __name__ == "__main__":
    main_loop()