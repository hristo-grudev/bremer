import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import BremerItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.bremer.com/api/insightsapi/LatestInsightsGrid"

payload="PageCategories%5B%5D=1b826e30-db22-45b1-acde-90d19a26e743&ExcludedInsightIds%5B%5D=29420bee-ff56-4a7d-a180-b252a79bc1d3&ExcludedInsightIds%5B%5D=59c05f10-f6ec-469d-83b7-f7c92fe0a6e4&ExcludedInsightIds%5B%5D=cf830919-ebeb-4917-ae6d-87612569ece3&ExcludedInsightIds%5B%5D=bfeb120e-2bd5-4574-979c-492bc1603474&Page=0&PageSize=999999"
headers = {
  'authority': 'www.bremer.com',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': '*/*',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.bremer.com',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.bremer.com/company/newsroom',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': 'ASP.NET_SessionId=jjtnj0fsleqrbtk1nde0zc23; SC_ANALYTICS_GLOBAL_COOKIE=bc553aa3af3c47cca19d220d88d032c5|False; _gcl_au=1.1.1811921379.1617863737; _ga=GA1.2.1673088893.1617863737; _gid=GA1.2.1904602027.1617863737; _gat_UA-763494-1=1; _fbp=fb.1.1617863737520.684375945; alert-b73c709a-72d7-4c86-a38f-2b44cd7f1329=false; alert-8be1dd30-17a7-41b2-bea1-2ee2e932eaaf=false; fpestid=KInzVzchkG9Vlfg0o8KrNGFqWscGS6bWDSSJNLA2x7kysoCO_21o7kmW3euFEHnWiDQ0tw; _uetsid=a10d0c70983411eb8a8ea78213908272; _uetvid=a10d6930983411eb81da4970b148cf48'
}


class BremerSpider(scrapy.Spider):
	name = 'bremer'
	start_urls = ['https://www.bremer.com/company/newsroom']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['GridPages']:
			link = post['Url']
			yield response.follow(link, self.parse_post)


	def parse_post(self, response):
		title = response.xpath('//div[@class="inner"]/h2/text()').get()
		description = response.xpath('//section[contains(@class,"content-block")]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="insights-date"]/text()').get()

		item = ItemLoader(item=BremerItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
