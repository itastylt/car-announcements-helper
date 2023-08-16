# Web crawler that downloads data
# To car dataset for ResNet-50
# Author: itastylt
# Sources: https://www.topcoder.com/thrive/articles/web-crawler-in-python

# Imports
import requests
from bs4 import BeautifulSoup
import time 
import csv
import os

class WebFlockerWorker:
    def __init__(self, csv_read=False,csv_file="links.csv", links=[]):
        """
        WebFlockerWorker classes constructor
        ------------------------------------
        Args:
            csv_read:   True if links need to be read from csv file
            
            csv_file:   Filename of the csv in which links are located

            links:      List of links that is already read
        """
        # Set user agent's header to Mozilla
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
        # Set links array
        self.links = links

        # If we need to read csv,
        # We read it and save list to links
        if(csv_read):
            print(self.links)
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                self.links = list(reader)
                print(self.links)

    def hasLinks(self) -> bool:
        """
        Check if current instance has any links
        ---------------------------------------
        Returns:
            True:   Current object instance has links

            False:  Current object instance has no links
        """
        return len(self.links) > 0
    
    def crawl_cars(self, tags, delay_s):
        last_index = len(self.links)-1
        car_link = self.links.pop(last_index)
        req = requests.get(car_link, headers=self.header)
        # Parse current page as HTML
        soup = BeautifulSoup(req.content, 'html.parser')
        # Get all elements that contains wanted information
        for tag in tags:
            item = soup.findAll(tag)
            print(item)
        
    def crawl_links(self, csv_file="mirror1.csv", base_url="https://autogidas.lt/", url_split=True, pagination_url="https://autogidas.lt/skelbimai/automobiliai/?f_50=kaina_asc&page=",
    pages=270, html_tag="a", link_class="item-link", delay_s=30):
        """ 
        Get car announcment links
        -------------------------
        Args:
            csv_file:       Filename of the the file, in which
                            car announcement links are saved
        
            base_url:       Base url of the site that is getting crawled

            url_split:      True if the crawled link is in format /.../
                            False if the crawled link is in format base_url/.../

            pagination_url: Url that represents pagination of the announcments

            pages:          Number of pages that will be read

            html_tag:       HTML tag of the element in which link
                            for the car announcment is saved

            link_class:     Class that is searched by BeautifulSoup
                            and we extract link from it

            delay_s:       Delay of the crawler, found in
                            https://www.*.*/robots.txt
        """
         
        # Open (create) csv file with writing mode
        with open(csv_file, 'w', newline='') as file:
            # Create python csv Writer object
            writer = csv.writer(file)
            
            # Crawl for each page
            for i in range(1, pages):
                # Get current page
                req = requests.get(pagination_url+str(i), headers=self.header)
                # Parse current page as HTML
                soup = BeautifulSoup(req.content, 'html.parser')
                # Get all elements that contains wanted information
                a = soup.findAll(html_tag, class_=link_class, href=True)
                
                # Write every link from the elements
                for link in a:
                    if(url_split):
                        self.links.append(base_url + link['href'])
                    else:
                        self.links.append(link['href'])
                    index = len(self.links)-1
                    writer.writerow([self.links[index]])
                time.sleep(delay_s)

class WebFlockerServer:
    def __init__(self, NUM_THREADS=os.cpu_count()):
        self.threads = NUM_THREADS
    def test(self):
        mirror1 = WebFlockerWorker(csv_read=True, csv_file="mirror1.csv")

webflockerserver = WebFlockerServer()
webflockerserver.test()