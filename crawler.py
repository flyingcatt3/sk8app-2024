import csv
import os
import random
import time
import requests
from fake_useragent import UserAgent # 可隨機產生 User-Agent
from bs4 import BeautifulSoup
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def parse_csv(file_path):
    links = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            link = row.get('Link')
            if link:
                links.append(link.strip('b').strip("'"))  # 去除可能的空白字符
    return links

def scrape_url(url, css_selectors):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        #ua = UserAgent() 
        #headers["User-Agent"] = ua.random
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = {}
            for selector in css_selectors:
                elements = soup.select(selector)
                results[selector] = [element.text.strip() for element in elements]
            return results
        else:
            print(f"Failed to retrieve {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error while scraping {url}: {str(e)}")
        return None
    finally:
        time.sleep(random.randint(5,10))

def save_to_txt(data, file_path):
    file_path = os.path.join("data/sk8", file_path)
    with open(file_path, 'a', encoding='utf-8') as txtfile:
        for url, results in data.items():
            #txtfile.write(f"URL: {url}\n")
            for selector, texts in results.items():
                #txtfile.write(f"Selector: {selector}\n")
                for text in texts:
                    txtfile.write(f"{text}\n")
                txtfile.write('\n')
            txtfile.write('\n')

if __name__ == "__main__":
    csv_file = 'output1.csv'
    css_selectors = ['.unified-story-hero__title', '.standfirst__headline','.standfirst__author','time','.inline-content__item']  # 這裡舉例兩個CSS Selector

    links = parse_csv(csv_file)
    for link in links:
        scraped_data = scrape_url(link, css_selectors)
        if scraped_data:
            save_to_txt({link: scraped_data}, f"data_{get_current_time()}.txt")

    print("Done!")