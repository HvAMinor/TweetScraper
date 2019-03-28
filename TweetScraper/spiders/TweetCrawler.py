from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.conf import settings
from scrapy import http
from scrapy.shell import inspect_response  # for debugging
import re
import json
import time
import logging
import datetime

from urllib.parse import quote  # Python 3+

from TweetScraper.items import Tweet, User

from scrapy.loader import ItemLoader


logger = logging.getLogger(__name__)


class TweetScraper(CrawlSpider):
    name = 'TweetScraper'
    allowed_domains = ['twitter.com']

    def __init__(self, query=None, lang='nl', crawl_user=True, top_tweet=True):
        self.query = f"from:JRHelmus OR to:JRHelmus"
        if query is not None:
            self.query = query

        self.lang = lang
        self.crawl_user = crawl_user
        self.url = "https://twitter.com/i/search/timeline?l={}".format(self.lang)
        self.url += "&f=tweets" if top_tweet else ''
        self.url += "&q=%s&src=typed&max_position=%s"


    def start_requests(self):
        url = self.url % (quote(self.query), '')
        logger.debug(f'opvragen {url}')
        yield http.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        data = json.loads(response.body.decode("utf-8"))
        logging.debug(f'pagina geparsed van {response.request.url}')
        for item in self.parse_tweets_block(data['items_html']):
            logging.debug(f"item geparsed {item}")
            yield item

        min_position = data['min_position']
        min_position = min_position.replace("+","%2B")
        url = self.url % (quote(self.query), min_position)
        logger.debug('opvragen volgende pagina')
        yield http.Request(url, callback=self.parse_page)

    def parse_tweets_block(self, html_page):
        page = Selector(text=html_page)
        items = page.xpath('//li[@data-item-type="tweet"]/div')
        for item in self.parse_tweet_item(items):
            yield item

    def parse_tweet_item(self, items):
        logger.debug(f'items ontvangen {items}')
        tw_xpaden = {'ID': './/@data-tweet-id',
                     'user_id': './/@data-user-id',
                     'text': './/div[@class="js-tweet-text-container"]/p',
                     'url': './/@data-permalink-path',
                     'timestamp': './/div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time',
                     'retweets': './/span[contains(@class, "ProfileTweet-action--retweet")]//@data-tweet-stat-count',
                     'favorites': './/span[contains(@class, "ProfileTweet-action--favorite")]//@data-tweet-stat-count',
                     'replies': './/span[contains(@class, "ProfileTweet-action--reply")]//@data-tweet-stat-count',
                     'conversation_id': '//@data-conversation-id',
                     'lang': self.lang}

        user_xpaden = {'ID': './/@data-user-id',
                       'screenname': './/@data-screen-name',
                       'name': './/@data-name'}

        for item in items:
            tweet = ItemLoader(Tweet(), item)
            for keys, values in tw_xpaden.items():
                tweet.add_xpath(keys, values)
            yield tweet.load_item()


            if self.crawl_user:
                user = ItemLoader(User(), item)
                for keys, values in user_xpaden.items():
                    user.add_xpath(keys, values)
                yield user.load_item()
        logger.info('pagina compleet geparsed op tweets')
