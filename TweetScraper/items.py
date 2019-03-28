# -*- coding: utf-8 -*-

# Define here the models for your scraped items
from scrapy import Item, Field
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

class Tweet(Item):
    ID = Field(
        output_processor=TakeFirst()
    )
    user_id = Field(
        output_processor=TakeFirst()
    )
    text = Field(
        input_processor = MapCompose(remove_tags),
        output_processor = Join()
    )
    url = Field(
        output_processor = TakeFirst()
    )
    timestamp = Field(
        output_processor = TakeFirst()
    )
    retweets = Field(
        output_processor = TakeFirst()
    )
    favorites = Field(
        output_processor = TakeFirst()
    )
    replies = Field(
        output_processor = TakeFirst()
    )
    lang = Field()

    conversation_id = Field(
        output_processor = TakeFirst()
    )


class User(Item):
    ID = Field(
        output_processor=TakeFirst()
    )
    screenname = Field(
        output_processor=TakeFirst()
    )
    name = Field(
        output_processor=TakeFirst()
    )
