import os
import serpapi
import csv

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('SERPAPI_KEY')

client = serpapi.Client(api_key=api_key)
result = client.search(
	q="滑板 site:https://www.redbull.com/tw-zh/",
	engine="google",
	location="Taiwan",
	hl="zh-tw",
	gl="tw",
    num=100
)

print(result)

organic_results = result["organic_results"]

  
with open('output.csv', 'w', encoding='utf-8',newline='') as csvfile:
	csv_writer = csv.writer(csvfile)
	
	# Write the headers
	csv_writer.writerow(["Title", "Link", "Snippet"])
	
	# Write the data
	for result in organic_results:
		csv_writer.writerow([result["title"].encode('utf-8'), result["link"].encode('utf-8'), result["snippet"].encode('utf-8')])

  
print('Done writing to CSV file.')