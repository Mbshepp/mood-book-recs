import heapq
from flask import Flask
from PIL import Image
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
from sqlalchemy.util import counter
from tenacity import before_log
from fraction import Fraction
from heapq import nlargest
from collections import Counter



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


def scrape_book_info():
    while len(titles_and_ratings_list) < 5:
        book_title = page.inner_text("h2")
        if book_title in recommended_books_list:
            page.get_by_text("Next Book").scroll_into_view_if_needed()
            page.click(f"text={'Next Book'}")
        else:
            rating_selector = 'div.tooltip.tooltip-top.md\\:tooltip-right[data-tip^="From GoodReads"]'
            book_rating = (page.inner_text(rating_selector))
            #print(book_rating)
            a, b = book_rating.split("/")
            float_book_rating = float(a) / float(b)
            title_rating_dict = {book_title: float_book_rating}
            #title_rating_dict = {book_title: book_rating}
            #rating_as_fraction = Fraction(book_rating)
            titles_and_ratings_list.append(title_rating_dict)
            #print(title_rating_dict)
            page.get_by_text("Next Book").scroll_into_view_if_needed()
            page.click(f"text={'Next Book'}")


    print(titles_and_ratings_list)
    #titles_and_ratings_list.clear()
    #print(titles_and_ratings_list)


def three_highest_values():
    count_dict = Counter(titles_and_ratings_list)
    three_highest = count_dict.most_common(3)
    for i in three_highest:
        print(i[0],":",i[1]," ")


User_Mood = "Happy".lower()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://booksbymood.com/")
    page.wait_for_selector("h2.text-3xl.font-semibold.text-accent.text-center.drop-shadow-md")
    timeout=5000
    page.click(f"text={User_Mood}")
    scrape_book_info()
    three_highest_values()
    #page.pause()









