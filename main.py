from sys import stdout
from time import sleep
from steamy import SteamAPI, SteamMarketAPI
import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import defaultdict

TIME_INTERVAL = 15
API_KEY = ""

class SteamPriceScraper:
    def __init__(self):
        steam = SteamAPI(API_KEY)
        self.steam_market = steam.market(730)
        self.model = LinearRegression()

    # Can be used to retrieve all csgo items from the steam api. Saves them into a csv file.
    def extract_all_itemnames(self):
        current_progress = 0
        try:
            with open("allitems.csv", "r", encoding="utf-8") as f:
                current_progress = len(f.readlines())
                print(f"continuing progress for extraction of itemnames: {current_progress}")
        except FileNotFoundError:
            print("no progress made scraping all itemnames. Starting now!")

        item_amount = self.steam_market.get_item_count()

        for i in range(current_progress,item_amount,100):
            item = self.steam_market.list_items("", i, 100, "quantity", "desc")
            item_list = list(item)
            
            with open("allitems.csv", "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(item_list))
            
            for idx in range (0,100):
                percent = (i+idx) / item_amount * 100 
                stdout.write(f"\rProgress {i+idx} of {item_amount} => {percent:.2f}%")
                stdout.flush()
                sleep(TIME_INTERVAL/100)

    # loads all itemnames from allitems.csv
    def load_all_itemnames(self):
        with open("allitems.csv", "r", encoding="utf-8") as f:
            items = []
            for line in f.readlines():
                items.append(line.rstrip())
        return items

    # calculates the difference of the price between the current date and date(time_delta_in_days) and also
    # calculates a simple LinearRegression and returns the slope
    def calculate_price_trend(self, item_name, time_delta_in_days):
        try:
            test = self.steam_market.get_item_price_history(item_name)
            filtered = {k.toordinal(): v for k, v in test.items() if (datetime.datetime.now() - datetime.timedelta(days=time_delta_in_days)) < k < datetime.datetime.now()}

            prices = list(filtered.values())
            dates = list(filtered.keys())

            dates = np.array(dates).reshape(-1, 1)

            diff = prices[len(prices)-1] - prices[0]
            diff_in_perc = round(diff / prices[0] * 100, 2)

            self.model.fit(dates, prices)

            return f"{diff_in_perc} % : RegrCoeff {self.model.coef_[0]}"
        except Exception as e :
            print(e)
            return "error"


if __name__ == '__main__':
    steam_price_scraper = SteamPriceScraper()
    #steam_price_scraper.extract_all_itemnames()
    all_items = steam_price_scraper.load_all_itemnames()

    current_progress = 0
    try:
        with open("result.csv", "r", encoding="utf-8") as f:
            current_progress = len(f.readlines())
            print(f"continuing progress for extraction of pricetrends at item: {current_progress}")
    except FileNotFoundError:
        print("no progress made calculating pricetrends. Starting now!")

    for idx in range(current_progress, len(all_items)):
        item = all_items[idx]
        price_diff = steam_price_scraper.calculate_price_trend(item, 30)
        with open("result.csv", "a", encoding="utf-8") as f:
            f.write(f"{item} : {price_diff}\n")
            stdout.write(f"\rProgress: {idx+1} of {len(all_items)}")
            stdout.flush()
        sleep(TIME_INTERVAL)


