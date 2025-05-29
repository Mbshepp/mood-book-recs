import heapq
import requests
import operator
import re
import base64
from flask import Flask
from PIL import Image
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from sqlalchemy.util import counter
from starlette_admin import HasOne
from tenacity import before_log
from fraction import Fraction
from heapq import nlargest
from collections import OrderedDict
import numpy as np
from operator import itemgetter
from urllib.request import urlretrieve



'''
moods_synonyms = {
    'Happy': ['happy','cheerful','elated'],
    'Sad': ['sad','melancholy','downcast'],
    'Enchanted': ['enchanted','captivated','wonderment'],
    'Inspired': ['inspired','stimulated','emboldened'],
    'Motivated': ['motivated','driven','hopeful'],
    'Nostalgic': ['nostalgic','sentimental','wishful'],
    'Curious': ['curious','inquisitive','questioning'],
    'Grateful': ['grateful','thankful', 'appreciative'],
    'Lonely': ['lonely','isolated','forlorn'],
    'Playful': ['playful','whimsical','goofy'],
    'Mad': ['mad','furious','irate'],
    'Bored': ['bored','uninterested','disinterested'],
    'Anxious': ['anxious','stressed','troubled'],
    'Humorous': ['humorous','amusing','witty'],
    'Serious': ['serious','solemn','earnest']
}
'''

titles_and_ratings_list = []
recommended_books_list = []
#title_rating_dict ={}
title_rating_list = []
book_title = None


def open_webpage_choose_mood():
    global page
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://booksbymood.com/")
    page.wait_for_selector("h2.text-3xl.font-semibold.text-accent.text-center.drop-shadow-md")
    timeout = 5000
    page.click(f"text={User_Mood}")


def scrape_book_info():
    #global title_rating_dict, book_title
    global title_rating_list, book_title
    while len(titles_and_ratings_list) < 5:
        book_title = page.inner_text("h2")
        if book_title in recommended_books_list:
            page.get_by_text("Next Book").scroll_into_view_if_needed()
            page.click(f"text={'Next Book'}")
        else:
            rating_selector = 'div.tooltip.tooltip-top.md\\:tooltip-right[data-tip^="From GoodReads"]'
            book_rating = (page.inner_text(rating_selector))
            a, b = book_rating.split("/")
            float_book_rating = float(a) / float(b)
            #title_rating_dict = {book_title: float_book_rating}
            title_rating_list= [book_title, float_book_rating]
            #titles_and_ratings_list.append(title_rating_dict)
            titles_and_ratings_list.append(title_rating_list)
            page.get_by_text("Next Book").scroll_into_view_if_needed()
            page.click(f"text={'Next Book'}")

    #return title_rating_dict
    return title_rating_list


def three_highest_ratings():
    global top_three_rated
    top_three_rated = []
    #sorted_high_low = sorted(titles_and_ratings_list, key=lambda x: list(x.values())[0], reverse=True)
    sorted_high_low = sorted(titles_and_ratings_list, key=lambda x: x[1], reverse=True)
    top_three_rated = sorted_high_low[:3]

    return top_three_rated


def scrape_top_three_books_full_info():
        open_webpage_choose_mood()
        #author_selector = 'div.tooltip.tooltip-top.md\\:tooltip-right[data-tip^="From GoodReads"]'
        page.wait_for_selector("span.text-gray-500.drop-shadow-md")
        timeout=3000
        author_selector = page.inner_text("span.text-gray-500.drop-shadow-md")
        book_summary = page.inner_text("div.pt-2.leading-relaxed.drop-shadow-md")
        page.wait_for_selector("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg")
        #purchase_link = page.locator("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg")
        purchase_link_locator = page.locator("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg").get_attribute('href')
        print("Purchase Link: ")
        print(purchase_link_locator)
        page.get_by_text("Next Book").scroll_into_view_if_needed()
        page.click(f"text={'Next Book'}")
        print("Author Name: " + author_selector)
        print("Book Summary: " + book_summary)

        return purchase_link_locator


def get_real_amazon_url(purchase_link_locator):
    try:
        response = requests.get(purchase_link_locator, allow_redirects=True, timeout=5)
        return response.url
    except Exception as e:
        print("Redirect failed", e)
        return None

def get_amazon_image_url(purchase_link_locator):
    real_url = get_real_amazon_url(purchase_link_locator)
    if real_url:
        match = re.search(r'/dp/(\w+)', real_url)
        if match:
            amzn_link_tail = match.group(1)
            return f"https://images-na.ssl-images-amazon.com/images/P/{amzn_link_tail}.01._SCLZZZZZZZ_.jpg"
    return None





        #current_url = page.url
        #response = requests.get(current_url)
        #soup = BeautifulSoup(response.text, 'html.parser')
        #img_tags = soup.find_all('img')
        #for img in img_tags:
         #   img_url = img.get('src')
          #  if img_url:
           #     img_name = img_tags[1]
            #    image_source = img_name['src']
             #   print("Image Source")
              #  print(image_source)'''





        #print(current_url)
        #print("Book Cover Elements: ")
        #print(book_cover)
        #print(source_code)
        #print("image source")
        #print(image_locator)


'''book_title_and_key_not_equal = book_title != list(titles_and_ratings_list)[0]
       if book_title_and_key_not_equal:
            page.get_by_text("Next Book").scroll_into_view_if_needed()
            page.click(f"text={'Next Book'}")
       else:'''



User_Mood = "Happy".lower()

with sync_playwright() as p:
    open_webpage_choose_mood()
    scrape_book_info()
    three_highest_ratings()
    scrape_top_three_books_full_info()
    purchase_link_locator = scrape_top_three_books_full_info()
    img_url = get_amazon_image_url(purchase_link_locator)
    if img_url:
        print(img_url)
    else:
        print("No Image Found")
    #page.pause()









