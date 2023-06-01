"""
Note that this module does not really scrape Willhaben.at,
it just requests a few pages for house/flat listings and processes
those into csv files.
"""
import json
import os
from pathlib import Path

import pandas as pd
import scrapy
import path_util
from scrapy.crawler import CrawlerProcess

_PROPERTIES = [
    "COORDINATES",
    "POSTCODE",
    "STATE",
    "COUNTRY",

    "HEADING",
    "BODY_DYN"

    "PROPERTY_TYPE",
    "PROPERTY_TYPE_FLAT",
    "LOCATION_QUALITY",
    "ESTATE_SIZE",
    "ESTATE_SIZE/LIVING_AREA",
    "FLOOR",
    "NUMBER_OF_ROOMS",
    "ROOMS",

    "RENT/PER_MONTH_LETTINGS",
    "PRICE",

    "PUBLISHED",
]

_OUTFILE = Path(path_util.DATA_DIR, 'willhaben_scrape.csv')


class WillhabenSpider(scrapy.Spider):
    name = 'willhaben'
    base_url = 'https://www.willhaben.at/iad/immobilien/mietwohnungen/wien?rows=30'
    n_pages = 2

    def start_requests(self):
        start_urls = [f"{self.base_url}?page={i}" for i in range(1, self.n_pages + 1)]
        for url in start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        data_str = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        data_json = json.loads(data_str)['props']['pageProps']['searchResult']
        flats = self._process_script_tag_data(data_json)
        df = pd.DataFrame(flats)
        df.to_csv(_OUTFILE, mode='a', header=not os.path.exists(_OUTFILE))

    def _process_script_tag_data(self, data_json: dict) -> list[dict]:
        """
        Re-used code from the project starting template.
        :param data_json: The search result data in JSON format.
        :return: Returns a list of dictionaries, where each item is one listing
        on Willhaben with the properties described in _PROPERTIES.
        """
        returns = []
        if 'advertSummaryList' not in data_json.keys():
            return []

        for advert in data_json['advertSummaryList']['advertSummary']:
            flat_properties = {}
            for attribute in advert['attributes']['attribute']:
                if attribute['name'] in _PROPERTIES:
                    flat_properties[attribute['name']] = "||".join(attribute['values'])

            if 'COORDINATES' not in flat_properties:
                continue

            latLon = flat_properties['COORDINATES'].split(",")

            flat_properties['LATITUDE'] = latLon[0]
            flat_properties['LONGITUDE'] = latLon[1]
            del flat_properties['COORDINATES']
            returns.append(flat_properties)
        return returns


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(WillhabenSpider)
    process.start()
