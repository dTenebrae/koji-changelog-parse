from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from koji_changelogs import settings
from koji_changelogs.spiders.changelogs import ChangelogsSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(ChangelogsSpider)
    crawl_proc.start()
