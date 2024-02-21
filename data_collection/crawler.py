import asyncio
import os
import re
import time
from datetime import date, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.async_api import (
    async_playwright,
)
from playwright.async_api._generated import Locator, Page


async def main(place: str, query: str) -> None:

    # 讀取舊檔
    # load old file (if there is one)
    try:
        old_reviews_df = pd.read_csv("text_data/reviews.csv")

        # 讀取最後一個餐廳id
        # get the last restaurant id
        restaurant_id = (old_reviews_df["restaurant_id"].astype(int).iloc[-1]) + 1
        existing_restaurant = old_reviews_df[
            ["restaurant_name", "restaurant_address"]
        ].drop_duplicates()
        if_old_file_exist = True

    except FileNotFoundError:
        restaurant_id = 0
        if_old_file_exist = False

    TODAY = date.today()
    MAPS_URL = "https://www.google.com/maps/?hl=en"  # english google maps url

    # start crawling
    async with async_playwright() as p:
        # browser = await p.firefox.launch(headless=False)  # for testing
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(MAPS_URL)

        # locate to given location
        await page.fill("#searchboxinput", place)
        await page.click("#searchbox-searchbutton")
        await page.wait_for_load_state("networkidle")
        time.sleep(1)

        # search for restaurants
        await page.fill("#searchboxinput", query)
        await page.click("#searchbox-searchbutton")
        await page.wait_for_load_state("networkidle")
        rest_list_loc = page.locator(".m6QErb.DxyBCb.kA9KIf.dS8AEf").nth(1)
        restaurants_loc = page.locator(".Nv2PK.THOPZb.CpccDe")

        # 載入所有餐廳
        # load all restaurants
        restaurants_count = await scroll_restaurant_async(
            page, rest_list_loc, restaurants_loc
        )

        # set id of restaurant in this round of crawling
        restaurant_on_web_id = 0

        # 依序爬取餐廳評論
        # crawling reviews one by one
        while restaurant_on_web_id < restaurants_count:
            print(f"restaurant_on_web_id: {restaurant_on_web_id}")
            rest = restaurants_loc.nth(restaurant_on_web_id)

            # get restaurant name
            restaurant_name = await rest.locator(
                ".qBF1Pd.fontHeadlineSmall"
            ).inner_text()

            # get short address
            restaurant_address = (
                await rest.locator(".W4Efsd>span>span").nth(2).inner_text()
            ).strip()

            if if_old_file_exist is True:
                # 跳過舊檔中已經有的餐廳
                # skip duplicated restaurants in old file by name and short address
                fltr = (existing_restaurant["restaurant_name"] == restaurant_name) & (
                    existing_restaurant["restaurant_address"] == restaurant_address
                )
                if len(existing_restaurant[fltr]) != 0:
                    print(f"Skip {restaurant_name, restaurant_address}, already exists")
                    restaurant_on_web_id += 1
                    continue
                print(f"New restaurant {restaurant_name, restaurant_address} detected")

            # 如果餐廳沒有評論則跳過
            # skip restaurant if no reviews
            no_reviews_label = await rest.locator(".e4rVHe.fontBodyMedium").inner_text()
            if no_reviews_label.strip() == "No reviews":
                print(f"{restaurant_on_web_id} No reviews")
                restaurant_on_web_id += 1
                continue

            # get review amount
            review_count_loc = rest.locator(".UY7F9")
            inner_text = await review_count_loc.inner_text()
            reveiw_count = int(inner_text[1:-1].replace(",", ""))
            print(f"reveiw_count: {reveiw_count}")

            # get restaurant type
            restaurant_type = (
                await rest.locator(".W4Efsd>span>span").first.inner_text()
            ).strip()

            # 大於200則評論則開始爬取
            # if review amount greater than 200 then start crawling
            if reveiw_count >= 200:
                # 開啟評論區塊
                # open review block
                await rest.locator(".hfpxzc").click()
                time.sleep(2)
                await page.locator(".hh2c6", has_text="Reviews").click()
                await page.wait_for_load_state("networkidle")
                review_list_div = page.locator(".m6QErb.DxyBCb.kA9KIf.dS8AEf").nth(2)

                # 載入所有評論
                # load all reviews
                await scroll_reviews_async(page, review_list_div)

                # 建立空的DataFrame接收評論資料
                # create DataFrame structure for review data
                reviews_df = pd.DataFrame(
                    {
                        "restaurant_id": int(),
                        "restaurant_type": [],
                        "review_rating": int(),
                        "review_date": [],
                        "review_body": [],
                        "restaurant_name": [],
                        "restaurant_address": [],
                    }
                )

                # start parsing html
                soup = BeautifulSoup(await page.content(), "html.parser")
                reviews = soup.select(".jftiEf.fontBodyMedium")

                for review in reviews:
                    # parsing review rating
                    review_rating_label = (review.select_one(".kvMYJc"))["aria-label"]
                    review_rating = int(re.search(r"\d+", review_rating_label).group())

                    # parsing review date
                    review_date_label = review.select_one(".rsqaWe").string
                    if review_date_label[0] == "a":
                        review_unit_number = 1
                    else:
                        review_unit_number = int(
                            re.search(r"\d+", review_date_label).group()
                        )
                    if "day" in review_date_label:
                        time_delta = timedelta(days=review_unit_number)
                    elif "week" in review_date_label:
                        time_delta = timedelta(days=review_unit_number * 7)
                    elif "month" in review_date_label:
                        time_delta = timedelta(days=review_unit_number * 30)
                    elif "year" in review_date_label:
                        time_delta = timedelta(days=review_unit_number * 365)

                    review_date = (TODAY - time_delta).strftime("%m/%d/%Y")

                    # parsing review body
                    if review.select_one(".MyEned") is not None:
                        review_body_org = review.select_one(".MyEned")
                        review_body = review_body_org.text.strip()
                    else:
                        review_body = None

                    # add data into DataFrame structure
                    new_data = pd.DataFrame(
                        {
                            "restaurant_id": restaurant_id,
                            "restaurant_type": restaurant_type,
                            "review_rating": review_rating,
                            "review_date": review_date,
                            "review_body": review_body,
                            "restaurant_name": restaurant_name,
                            "restaurant_address": restaurant_address,
                        },
                        index=[0],
                    )
                    reviews_df = pd.concat(
                        [reviews_df, new_data], axis=0, ignore_index=True
                    )
                print(f"restaurant_id : {restaurant_id} writing into reviews.csv")

                # writing into csv file
                if os.path.isdir("text_data") is False:
                    os.mkdir("text_data")
                if restaurant_id == 0:
                    reviews_df.to_csv(
                        "text_data/reviews.csv",
                        encoding="utf-8",
                        index_label="review_no_per_rest",
                    )
                else:
                    reviews_df.to_csv(
                        "text_data/reviews.csv",
                        mode="a",
                        header=False,
                        encoding="utf-8",
                    )
                restaurant_id += 1
            restaurant_on_web_id += 1

        await browser.close()


async def scroll_restaurant_async(
    page: "Page", rest_list_loc: "Locator", restaurants_loc: "Locator"
) -> int:
    """scroll餐廳列表

    scroll restaurant list
    """
    restaurants_count = 0
    while True:
        await rest_list_loc.evaluate(
            "element => element.scrollTop = element.scrollHeight"
        )
        time.sleep(3)
        await page.wait_for_load_state("networkidle")
        restaurants_count_new = await restaurants_loc.count()
        print(f"restaurants_count: {restaurants_count_new}")
        if restaurants_count == restaurants_count_new:
            break
        restaurants_count = restaurants_count_new

    return restaurants_count


async def scroll_reviews_async(page: "Page", review_list_div: "Locator") -> None:
    """scroll+展開留言

    scroll review list and unfold reviews
    """
    reviews_loc = page.locator(".jftiEf.fontBodyMedium")
    reviews_count = 0
    # unfold at most 1000 reviews
    for i in range(102):
        try:
            await review_list_div.evaluate(
                "element => element.scrollTop = element.scrollHeight"
            )
            time.sleep(1)
            print(f"scrolled to page {i+1}")
            reviews_count_new = await reviews_loc.count()
            if i > 20 and reviews_count == reviews_count_new:
                break
            reviews_count = reviews_count_new
        except PlaywrightTimeoutError:
            print("Time Error Occurs")
            continue
    # 展開所有評論
    # unfold all reviews by clicking "more"
    more_buttons = page.locator(".w8nwRe.kyuRq")
    more_buttons_count = await more_buttons.count()
    if more_buttons_count > 0:
        for i in range(more_buttons_count):
            try:
                button = more_buttons.first
                await button.click()
            except PlaywrightTimeoutError:
                print("Time Error Occurs")
                continue


place = "Staten Island, New York, NY, USA"
# NY, Manhattan, Brooklyn, Queens, Bronx, Staten Island
query = "Restaurant"
asyncio.run(main(place, query))
