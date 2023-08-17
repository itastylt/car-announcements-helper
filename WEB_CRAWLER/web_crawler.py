# Web crawler that downloads data
# To car dataset for ResNet-50
# Author: itastylt
# Sources: https://www.topcoder.com/thrive/articles/web-crawler-in-python

# Imports
from bs4 import BeautifulSoup
import time, csv, os, re, base64, requests
from io import BytesIO
from PIL import Image

class WebFlockerWorker:
    """
        WebFlockerWorker class
        ----------------------
        Description:
            Represents One Worker Thread
            Has basic methods that are used to crawl one
            Car announcment website
    """
    def __init__(self, csv_read: bool,csv_file: str, links: list):
        """
        WebFlockerWorker classes constructor
        ------------------------------------
        Args:
            csv_read:   Boolean: 
                        True if links need to be read from csv file
                        
            csv_file:   String: 
                        Filename of the csv in which links are located

            links:      List <String>: 
                        List of links that is already read

        Return:
            None
        """

        # Set user agent's header to Mozilla
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
        # Set links array
        self.links = links

        # If we need to read csv,
        # We read it and save list to links
        if(csv_read):
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                self.links = list(reader)

    def hasLinks(self) -> bool:
        """
        Check if current instance has any links
        ---------------------------------------
        Return:
            True:   Current object instance has links

            False:  Current object instance has no links
        """
        return len(self.links) > 0

    def crawl_cars(self, table_tags: list, image_tag: dict, csv_file: str, delay_s: int):
        """
        Get car information
        -------------------
        Args:
            table_tags:     List<Dictionary>:
                            Tags that are queried:
                            "html_tag" is HTML tag selector
                            "css_class" is class selector
                            "content" is pattern that is searched
                            ex. [{"html_tag":"div", "css_class":"class1", "content": "example1"},
                                 {"html_tag":"div", "css_class":"class2", "content":"example2"}]
            
            image_tag:      Dictionary:
                            Tag that finds image:
                            "html_tag" is HTML tag selector (expected img)
                            "css_class" is class selector
                            ex: {"html_tag":"img", "css_class":"image_class"}

            csv_file:       String:
                            Filename of the csv in which our data is saved

            delay_s:        Integer:
                            Delay of the crawler, found in
                            https://www.*.*/robots.txt

        Return:
            None
        """

        # Wait a bit so we don't get banned
        time.sleep(delay_s)
        # Get first index of the link stack
        last_index = len(self.links)-1
        # Pop stack, and save link into memory
        car_link = self.links.pop(last_index)[0]
        # Send HTTP GET request to popped link
        res = requests.get(car_link, headers=self.header)
        # Parse current page as HTML
        soup = BeautifulSoup(res.content, 'html.parser')
        tag_vals = []

        # Get all elements that contains wanted information
        for tag in table_tags:
            parameter = soup.find(tag["html_tag"],string=re.compile(tag["content"])).parent
            value = parameter.find(tag["html_tag"], class_=tag["css_class"]).text
            tag_vals.append(value)

        # Get image URL
        image_url = soup.find(image_tag["html_tag"], class_=image_tag["css_class"])['src']

        # If image url is valid, Base64 encode it's buffer
        # And save it to CSV file, so we can work with it later. 
        if(image_url != None):
            time.sleep(5)
            response = requests.get(image_url, headers=self.header)
            img = Image.open(BytesIO(response.content))

            # Convert image to cStringIO Buffer.
            # Get it's raw value, convert it to PNG.
            # And then do Base64 encode.
            # --------------------------------------
            # Note: BytesIO buffer in Python3 is eq to cStringIO buffer in Python2
            with BytesIO() as buf:
                img.save(buf, 'png')
                image_bytes = buf.getvalue()
                base64_image = base64.b64encode(image_bytes)
                tag_vals.append(base64_image)
            # Append csv file with extracted information.
            with open(csv_file, 'a') as file:
                writer = csv.writer(file)
                writer.writerow(tag_vals)
        # Proceed to the next car link in the stack
        self.crawl_cars(table_tags=table_tags, image_tag=image_tag, csv_file=csv_file, delay_s=delay_s)
        
    def crawl_links(self, csv_file: str, base_url: str, url_split: bool, pagination_url:str,
    pages:int, html_tag: str, link_class: str, delay_s: int):
        """ 
        Get car announcment links
        -------------------------
        Args:
            csv_file:       String:
                            Filename of the the file, in which
                            car announcement links are saved
        
            base_url:       String:
                            Base url of the site that is getting crawled

            url_split:      Boolean:
                            True if the crawled link is in format /.../ 
                            False if the crawled link is in format base_url/.../

            pagination_url: String:
                            Url that represents pagination of the announcments

            pages:          Integer:
                            Number of pages that will be read

            html_tag:       String:
                            HTML tag of the element in which link
                            for the car announcment is saved

            link_class:     String:
                            Class that is searched by BeautifulSoup
                            and we extract link from it

            delay_s:        Integer:
                            Delay of the crawler, found in
                            https://www.*.*/robots.txt
        Return:
            None
        """
         
        # Open (create) csv file with writing mode
        with open(csv_file, 'w', newline='') as file:
            # Create python csv Writer object
            writer = csv.writer(file)
            
            # Crawl for each page
            for i in range(1, pages):
                # Get current page
                res = requests.get(pagination_url+str(i), headers=self.header)
                # Parse current page as HTML
                soup = BeautifulSoup(res.content, 'html.parser')
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
        mirror1.crawl_cars([{"html_tag": "div", "css_class": "right", "content": "Markė"},
                            {"html_tag": "div", "css_class": "right", "content": "Modelis"}, 
                            {"html_tag": "div", "css_class": "right", "content": "Metai"}],
                            {"html_tag": "img", "css_class": "show"}, "autogidas.csv", 30)
webflockerserver = WebFlockerServer()
webflockerserver.test()