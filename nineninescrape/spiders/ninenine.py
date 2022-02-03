import scrapy
from scrapy.exceptions import CloseSpider
from ..items import NineninescrapeItem


class NinenineSpider(scrapy.Spider):
    name = 'ninenine'
    allowed_domains = ['theninenine.com']

    def start_requests(self):
        url = 'https://theninenine.com/quotes/latest/'
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        current_page = response.css('div.standard_box').xpath('.//span/text()').get().split(' ')[1]
        total_pages = response.css('div.standard_box').xpath('.//span/text()').get().split(' ')[-1]

        next_url = response.css('div.pageLinkRight').xpath('.//a/@href').get()

        quote_divs = response.css('div.quotesDiv')
        page_ps = response.css('div.quotesDiv').xpath('./div/p')
        for div in quote_divs:
            item = NineninescrapeItem()
            item['id'] = div.xpath('@id').get().split('_')[-1]
            quote = ''.join(div.xpath('./div/p//text()').getall())
            if quote is not None:
                item['quote'] = quote
            speakers = []
            speaks = [x.replace(':', '') for x in div.xpath('./div/p/strong/text()').getall()]
            for speak in speaks:
                if speak not in speakers:
                    speakers.append(speak)
            item['speakers'] = speakers
            yield item

        if int(total_pages) > int(current_page):
            url = response.urljoin(next_url)
            yield scrapy.Request(url, callback=self.parse)
        else:
            print(f"Current_page: {current_page}, Total_pages: {total_pages}.")
            raise CloseSpider(reason="All pages crawled.")
