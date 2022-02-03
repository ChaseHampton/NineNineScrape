import scrapy
import sqlite3
from scrapy.exceptions import CloseSpider
from ..items import NineninescrapeItem


class NinenineSpider(scrapy.Spider):
    name = 'ninenine'
    allowed_domains = ['theninenine.com']
    con = sqlite3.connect('ids.db')

    def start_requests(self):
        url = 'https://theninenine.com/quotes/latest/'
        curs = self.con.execute('CREATE TABLE IF NOT EXISTS ids (id int);')
        self.con.commit()
        curs.close()
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):

        current_page = response.css('div.standard_box').xpath('.//span/text()').get().split(' ')[1]
        total_pages = response.css('div.standard_box').xpath('.//span/text()').get().split(' ')[-1]

        next_url = response.css('div.pageLinkRight').xpath('.//a/@href').get()

        quote_divs = response.css('div.quotesDiv')
        page_ps = response.css('div.quotesDiv').xpath('./div/p')
        for div in quote_divs:
            curs = self.con.cursor()
            item = NineninescrapeItem()
            qid = div.xpath('@id').get().split('_')[-1]
            curs.execute("select id from ids where id = :id", {"id": qid})
            if curs.fetchone():
                item['id'] = qid
                quote = ''.join(div.xpath('./div/p//text()').getall())
                if quote is not None:
                    item['quote'] = quote
                speakers = []
                speaks = [x.replace(':', '') for x in div.xpath('./div/p/strong/text()').getall()]
                for speak in speaks:
                    if speak not in speakers:
                        speakers.append(speak)
                item['speakers'] = speakers
                curs.execute("INSERT INTO ids VALUES (?)", (qid,))
                curs.close()
                yield item
            else:
                curs.close()
                continue

        if int(total_pages) > int(current_page):
            url = response.urljoin(next_url)
            self.con.commit()
            yield scrapy.Request(url, callback=self.parse)
        else:
            print(f"Current_page: {current_page}, Total_pages: {total_pages}.")
            self.con.commit()
            self.con.close()
            raise CloseSpider(reason="All pages crawled.")
