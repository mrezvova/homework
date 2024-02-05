import scrapy


class HomeworkSpider(scrapy.Spider):
    name = "homework"
    allowed_domains = ["dnevnik2.petersburgedu.ru"]
    start_urls = ["https://dnevnik2.petersburgedu.ru/schedule"]

    def parse(self, response):
        for reg in response.xpath('/html/body/app-root/div/main/div/page-lessons-container/int-lessons-page/widget-layout-container/int-layout/div/div/div/div/section[1]/int-lessons-schedule-container/domain-schedule/div/div/div[2]/int-day[6]/div/div/int-event[1]'):
            data = {
                'name': reg.xpath('div/span[1]/span[1]/span/text()').get(),
                'nic_handle1': reg.xpath('div/span[1]/span[2]/span[1]/text()').get(),
                'nic_handle2': reg.xpath('div/span[1]/span[2]/span[2]/text()').get(),
                'city': reg.xpath('div/span[2]/text()').get(),
                'website': reg.xpath('div/a/@href').get()
            }

            company, created = models.Registrator.objects.get_or_create(name=data['name'])

