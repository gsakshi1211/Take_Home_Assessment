## IMPORT STATEMENTS
from ..items import EleclercItem
import scrapy
import json

## Scrapy class
class eleclercSpider(scrapy.Spider):
    name = "eleclerc"
    # Initializor
    def __init__(self):
        # Start urls to encounter successively
        self.start_urls = [
            "https://www.e.leclerc/api/rest/live-api/categories-tree-by-code/NAVIGATION_sport-loisirs?pageType=NAVIGATION&maxDepth=undefined",
            "https://www.e.leclerc/api/rest/live-api/categories-tree-by-code/NAVIGATION_vetements?pageType=NAVIGATION&maxDepth=undefined"
        ]

    # function to handle the response data of start_url
    def parse(self, response):
        categories = json.loads(response.text)["children"]
        # Looping over all of the categories
        for category in categories:
            # print(category)
            number_of_products = category["nbProducts"]
            code = category["code"]
            # Pages to loop on, to fetch complete data
            pages = (number_of_products // 90) + 1
            for page in range(1, pages + 1):
                # The new category-specific url --> that is forwarded to parse_category_url() function
                category_url = 'https://www.e.leclerc/api/rest/live-api/product-search?language=fr-FR&size=90&page=' + \
                                str(page) + '&sorts=[{"key":"alpha","order":"desc"}]&categories={"code":["' + \
                                code + '"]}'
                yield scrapy.Request(url=category_url, callback=self.parse_category_url)


        ##### SINGLE PAGE SCRAPING FOR UNSERSTANDING THE SCHEMA #####
        # category_url = "https://www.e.leclerc/api/rest/live-api/product-search?language=fr-FR&size=30&page=1&sorts=[{%22key%22:%22alpha%22,%22order%22:%22desc%22}]&categories={%22code%22:[%22NAVIGATION_bon-plan-sport-et-loisir%22]}"
        # yield scrapy.Request(url=category_url, callback=self.parse_category_url)

    # function to handle each category response data.
    def parse_category_url(self, response):
        # Creating a temporary Item Object to store the data
        result = EleclercItem()
        category_items = json.loads(response.text)["items"]
        # Looping over each and individual item to fetch the required keys or data only
        for item in category_items:
            name = item["label"]
            sku = item["id"]
            ean = item["sku"]
            slug = item["slug"]
            original_price = item["variants"][0]["offers"][0]["basePrice"]["price"]["price"]
            product_category = item["families"][2]["label"]
            product_page_url = "/fp/" + slug + "-" + ean
            image_url = "https://e-leclerc.scene7.com/is/image/gtinternet/" + ean + "_1"
            stock = int(item["variants"][0]["offers"][0]["stock"])
            try:
                sale_price = item["variants"][0]["offers"][0]["basePrice"]["discountPrice"]["totalPrice"]["price"]
            except Exception as e:
                sale_price = original_price
            brand_section = item["attributeGroups"][0]["attributes"]
            brand = [brand["value"]["label"] for brand in brand_section if brand["code"]=="marque"]

            # Storing the data in temporary item object and yielding
            result["name"] = name
            result["brand"] = brand[0]
            result["original_price"] = float(original_price)
            result["sale_price"] = float(sale_price)
            result["image_url"] = image_url
            result["product_page_url"] = "https://www.e.leclerc" + product_page_url
            result["product_category"] = product_category
            result["stock"] = True if (stock > 0) else False
            result["sku"] = sku
            result["ean"] = ean

            yield result

