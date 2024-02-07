import logging
import scrapy


from .src.grabber.items import LessonItem

class HomeworkSpider(scrapy.Spider):
    name = "homework"
    allowed_domains = ["dnevnik2.petersburgedu.ru"]
    start_urls = ["https://dnevnik2.petersburgedu.ru/schedule"]

    def parse(self, response):
        for reg in response.xpath("//div[@class='schedule-day__lessons']"):

            lesson = reg.xpath('div/div[2]/h4/text()').get()
            task = reg.xpath('div/div[3]/div[2]/div/div/text()').get()
            

            item = LessonItem()
            item['lesson'] = id_offer_buy
            item['task'] = area_buy
            logging.info(item)

            yield item


