import scrapy
from ..items import KojiChangelogsItem


class ChangelogsSpider(scrapy.Spider):
    name = 'changelogs'
    accepted_fields = [
        'ID',
        'Package Name',
        'Version',
        'Release',
        'Summary',
        'Description',
        'Changelog'
    ]

    allowed_domains = ['stapel.red-soft.ru']
    start_urls = ['http://stapel.red-soft.ru/koji/builds?start=0&order=-build_id&state=1']
    xpath_query = {
        'page': '//tr[starts-with(@class, "row-")]//a/@href',
        'pagination': '//form[@class="pageJump"]//option'
    }

    def parse(self, response, **kwargs):
        # собираем url'ы для всех страниц
        pages = []
        for item in response.xpath(self.xpath_query['pagination']):
            try:
                # по 50 элементов на странице
                cur_page = (int(item.xpath('./text()').get()) - 1) * 50
                pages.append(f'http://stapel.red-soft.ru/koji/builds?start={cur_page}&order=-build_id&state=1')
            except ValueError as verr:
                print(verr)
                exit(1)
        for url in pages:
            yield scrapy.Request(url=url, callback=self.parse)

        # обрабатываем список билдов на каждой странице
        for page in response.xpath(self.xpath_query['page']):
            # Так как мы найдем ссылки в том числе и на сборщиков, возьмем только нужные
            if page.get().__contains__('buildID'):
                yield response.follow(page, callback=self.build_parse)

    def build_parse(self, response):
        scr_item = KojiChangelogsItem()
        data_dict = {}
        for item in response.xpath('//table//tr'):
            name = item.xpath('.//th/text()').get()
            if name not in self.accepted_fields:
                continue
            data = item.xpath('.//td/text()').get()
            if name == 'ID':
                scr_item['build_id'] = data
                continue
            if name == 'Package Name':
                data = item.xpath('.//td/a/text()').get()
            if name == 'Changelog':
                # сплитим по двойной новой строке
                # в случае пустого поля в конце списка - отрезаем его
                data = data.split('\n\n')[:-1] \
                    if not data.split('\n\n')[-1] else data.split('\n\n')
            data_dict[name] = data
        data_dict['url'] = response.url
        scr_item['item_data'] = data_dict
        yield scr_item
