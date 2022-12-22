# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


import pymongo


class LearningScrapyPipeline(object):
    def __init__(self):
        self.conn = pymongo.MongoClient(
            'localhost',
            27017
        )

        db = self.conn['leclerc_fr']
        self.collection = db['sports_tb']

    def process_item(self, item, spider):
        print(item)
        self.collection.insert_one(dict(item))
        return item