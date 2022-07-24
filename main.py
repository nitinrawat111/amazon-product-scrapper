import requests
from bs4 import BeautifulSoup
import csv

class Product:
    def __init__(self):
        self.url = "NA"
        self.name = "NA"
        self.price = "NA"
        self.rating = "NA"
        self.reviewCount = "NA"
        self.description = "NA"
        self.asin = "NA"
        self.manufacturer = "NA"
    def parseToList(self):
        return [self.url, self.name, self.price, self.rating, self.reviewCount, self.description, self.asin, self.manufacturer]

siteUrl = "https://www.amazon.in"
targetUrlStart = "https://www.amazon.in/s?k=bags&page="
targetUrlEnd = "&crid=2M096C61O4MLT&qid=1658575076&sprefix=ba%2Caps%2C283&ref=sr_pg_"
#Custom headers to prevent blocking by Amazon Site
requestHeaders = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

#List to store details of bags 
bags = []

for i in range(1, 21):
    htmlText = requests.get(targetUrlStart + str(i) + targetUrlEnd + str(i), headers = requestHeaders).text
    soup = BeautifulSoup(htmlText, 'lxml')
    searchResultsTags = soup.find_all('div', class_ = "s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")
    for resultTag in searchResultsTags:
        bag = Product()
        
        #Finding Name and Url of product
        resultUrlTag = resultTag.find('h2').a
        bag.url = siteUrl + resultUrlTag['href']
        bag.name = resultUrlTag.span.text
        
        #Finding Price
        try:
            bag.price = resultTag.find('span', class_ = "a-price").span.text
        except:
            pass
        
        resultRatingDivisionTag = resultTag.find('div', class_ = "a-row a-size-small")
        
        #Finding Rating
        try:
            bag.rating = resultRatingDivisionTag.contents[0]['aria-label'].split()[0]
        except:
            pass
        
        #Finding Review Count
        try:
            bag.reviewCount = resultRatingDivisionTag.contents[1]['aria-label']
        except:
            pass
        
        bags.append(bag)
    print("Fetched Results from Page " + str(i))

def doesStringContainASIN(string):
    if string is None:
        return False
    return string.startswith("ASIN") or  string.startswith(" ASIN")

def doesStringContainManufacturer(string):
    if string is None:
        return False
    return string.startswith("Manufacturer") or string.startswith(" Manufacturer")

def checkIdForProductDetails(id):
    return "prodDetails" == id or "detailBullets_feature_div" == id

for bag in bags:
    htmlText = requests.get(bag.url, headers = requestHeaders).text
    soup = BeautifulSoup(htmlText, 'lxml')
    productDetailsDiv = soup.find('div', id = checkIdForProductDetails)

    # Finding ASIN Number
    try:
        asinTag = productDetailsDiv.find(["span", "th"], string = doesStringContainASIN)
        asinTag = asinTag.find_next_sibling()
        bag.asin = asinTag.text.replace("&lrm;", "").replace("&rlm;", "").strip()
    except:
        pass

    #Finding Manufacturer
    try:
        manufacturerTag = productDetailsDiv.find(["span", "th"], string = doesStringContainManufacturer)
        manufacturerTag = manufacturerTag.find_next_sibling()
        bag.manufacturer = manufacturerTag.text.replace("&lrm;", "").replace("&rlm;", "").strip() 
    except:
        pass
    
    #Finding Product Description
    try:
        productDescriptionDiv = soup.find("h2", string = "Product Description")
        productDescriptionDiv = productDescriptionDiv.find_next_sibling()
        bag.description = productDescriptionDiv.text.strip()
        bag.description = " ".join(bag.description.split())
    except:
        pass
    print("Fetched Product Details for " + bag.name)

#Heading for Excel Sheet Columns
excelHeaders  = ["url", "name", "price", "rating", "reviewCount", "description", "asin", "manufacturer"]
with open("bags.csv", 'w', newline = '', encoding = "utf8") as excelFile:
    writer = csv.writer(excelFile)
    writer.writerow(excelHeaders)
    for bag in bags:
        writer.writerow(bag.parseToList())