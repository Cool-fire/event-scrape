# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup as bs
import requests
import json
import csv

class BridalscrapeSpider(scrapy.Spider):
    name = 'bridalscrape'
    def __init__(self, *args, **kwargs):
        self.profiles = []
        self.data = [['profile_pic_url','id','name','slug','contact_email','contact_name','email','city','other_cities','category_name','category_slug','phone_numbers','address','landmark']]

    
    #allowed_domains = ['https://www.wedmegood.com/vendors/all/bridal-makeup/?page=1']
    #start_urls = ['http://https://www.wedmegood.com/vendors/all/bridal-makeup/?page=1/']
    def start_requests(self):
        no_pages = 117    #no of pages in the website to crawl
        base_url = 'https://www.wedmegood.com/vendors/all/bridal-makeup/?page={}/'
        for page in range(1,no_pages+1):
            url = base_url.format(page)
            yield scrapy.Request(url = url, callback = self.parse)

    def parse(self, response):
        body = response.body
        soup = bs(body,'html.parser')
        base_profile_url = "https://www.wedmegood.com"
        tags = soup.find_all("a",class_ = "vendor-detail text-bold h6")
        self.profiles = [base_profile_url+tag['href'] for tag in tags]
        self.getDetails(self.profiles)


    def getDetails(self, profiles):
        ids = []
        for profile in profiles:
            profile_html = requests.get(profile)
            soup = bs(profile_html.content,'html.parser')
            try:
                script_tag = soup.find_all("script")[-1].string
                if(script_tag != None):
                    vendor_id = json.loads(script_tag)['@id']
                    ids.append(vendor_id)
            except:
                print("Error")

        for id in ids:
            url = 'https://www.wedmegood.com/api/v1/vendor/{}?version=1.1&token=5ca092c0aea269.16605168'.format(id)
            details = requests.get(url)
            details_json = json.loads(details.content)

            profile_pic_url = details_json['data']['profile']['profile_pic_url']
            id_ = details_json['data']['profile']['id']
            name = details_json['data']['profile']['name']
            slug = details_json['data']['profile']['slug']
            contact_email = details_json['data']['profile']['contact_email']
            contact_name = details_json['data']['profile']['contact_name']
            email = details_json['data']['profile']['email']
            city = details_json['data']['profile']['city']
            other_cities = details_json['data']['profile']['other_cities']
            category_name = details_json['data']['profile']['category_name']
            category_slug = details_json['data']['profile']['category_slug']
            phone_numbers_json = details_json['data']['profile']['phone_numbers']
            phone_numbers = ",".join([str(phone_number['phone']) for phone_number in phone_numbers_json])

            complete_address = None
            landmark = None

            if 'address' in details_json:
                address_json = details_json['data']['profile']['address']
                complete_address = address_json[0]['completeAddress']
                landmark = address_json[0]['landmark']  
            self.data.append([profile_pic_url,id_,name,slug,contact_email,contact_name,email,city,other_cities,category_name,category_slug,phone_numbers,complete_address,landmark])
        
        self.WritetoCsv(self.data)

    def WritetoCsv(self, data):
        with open('bridal.csv','w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(data)
        csvFile.close()
        print(self.data)




