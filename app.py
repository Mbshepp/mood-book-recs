import heapq
import requests
import operator
import re
import base64
import keyboard
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
from playwright.sync_api import sync_playwright


'''
moods_synonyms = {
    'Happy': ['happy','cheerful','elated'],
    'Sad': ['sad','melancholy','downcast'],
    'Enchanted': ['enchanted','captivated','wonderment'],
    'Inspired': ['inspired','stimulated','emboldened'],
    'Nostalgic': ['nostalgic','sentimental','wishful'],
    'Lonely': ['lonely','isolated','forlorn'],
    'Mad': ['mad','furious','irate'],
    'Humorous': ['humorous','amusing','witty'],
    'Serious': ['serious','solemn','earnest']
}
'''


titles_and_ratings_list = []
recommended_books_list = []
reading_list = []
#title_rating_dict ={}
title_rating_list = []
book_title = None
recommended_book_headings = []
reading_list_headings = []
collective_answers = []




def mood_quiz():
    global user_mood, answer_tree
    user_mood = None
    quiz_questions = [
        "1. What kind of moment sounds most appealing right now?", "2. You're walking and your playlist surprises you. What hits best today?",
        "3. A friend says 'Tell me something real.' You say:", "4. Pick a setting that sounds closest to your current mood:",
        "5. Right now, your thoughts feel:", "6. You open a book. The first line should make you feel:",
        "7. How does your body feel today?", "8. Which scene could you step into right now?", "9. Someone asks how you're really doing. You say:"
    ]

    answers = [
        ["A. Sitting in a sunny spot with something sweet to sip.", "B. Wandering through an old bookstore or antique shop","C. Getting lost in a quiet place with no phone service"],
        ["A. Something dreamy and cinematic.", "B. Something that punches the air and moves fast", "C. Something with depth that makes you think"],
        ["A. Honestly? I'm not sure how I'm doing.", "B. I feel like I'm waking up from something.", "C. Life's weird, but at least it's never boring."],
        ["A. A rooftop at golden hour.", "B. A quiet kitchen at midnight.", "C. A mossy trail you haven't walked before."],
        ["A. Sharp and pointed.", "B. Heavy but honest.", "C. Like a cloud you're trying to hold."],
        ["A. Like you're about to remember something you forgot.", "B. Like anything is possible.", " C. Like you're about to laugh out loud."],
        ["A. Light, like there's a skip in your step.", "B. Like you're moving through molasses.", "C. Like you're buzzing with ideas or restlessness."],
        ["A. A candlelit room full of soft music.", "B. A city street, neon lights, people moving fast.", "C. A field of fireflies under a big sky."],
        ["A. 'Honestly? I'm doing okay. Better than usual.", "B. 'It's been a lot lately, but I'm managing.", " C. 'I don't know... I just feel off."]
    ]

    answer_tree = [
        ["Happy: Q1A, Q4A, Q7A, Q9A"],
        ["Sad: Q3A, Q4B, Q7B, Q8A, Q9C"],
        ["Enchanted: Q2A, Q4C, Q8C"],
        ["Inspired: Q3B, Q6B, Q7C, Q9B"],
        ["Nostalgic: Q1B, Q6A, Q8A"],
        ["Humorous: Q3C, Q6C"],
        ["Lonely: Q1C, Q5C, Q9C"],
        ["Mad: Q2B, Q5A, Q7C, Q8B"],
        ["Serious: Q2C, Q5B, Q8B, Q9B"]
    ]

    for i, question in enumerate(quiz_questions):
        print(question)
        answer_row_index = answers[i]
        user_input = input(
            f" Choose: A, B, or C \n"
            f"{answer_row_index[0]}\n"
            f"{answer_row_index[1]}\n"
            f"{answer_row_index[2]}")

        user_answer = "q" + str(i+1) + user_input.lower()
        collective_answers.append(user_answer)
        print(collective_answers)

        for row in answer_tree:
            mood, triggers = row[0].split(": ")
            individual_triggers = [x.strip().lower() for x in triggers.split(",")]

            if any(trigger.lower() in collective_answers for trigger in individual_triggers):
                user_mood = mood.lower()
                break

    return user_mood


def open_webpage_choose_mood(user_mood):
    global page
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://booksbymood.com/")
    page.wait_for_selector("h2.text-3xl.font-semibold.text-accent.text-center.drop-shadow-md")
    timeout = 2000

    selector = f'a[href*="{user_mood}"]'

    page.wait_for_selector(selector)
    page.click(selector)


def scrape_book_info():
    global book_title
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
            author_selector = page.inner_text("span.text-gray-500.drop-shadow-md")
            book_summary = page.inner_text("div.pt-2.leading-relaxed.drop-shadow-md")
            page.wait_for_selector("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg")
            purchase_link_locator = page.locator("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg").get_attribute('href')
            get_real_amazon_url(purchase_link_locator)
            get_amazon_image_url(purchase_link_locator)
            img_url = get_amazon_image_url(purchase_link_locator)

            title_rating_list = [book_title, book_rating, author_selector, book_summary, purchase_link_locator, img_url]
            titles_and_ratings_list.append(title_rating_list)
            page.get_by_text("Next Book").scroll_into_view_if_needed()
            page.click(f"text={'Next Book'}")

    return title_rating_list


def three_highest_ratings():
    global top_three_rated
    top_three_rated = []
    #sorted_high_low = sorted(titles_and_ratings_list, key=lambda x: list(x.values())[0], reverse=True)
    sorted_high_low = sorted(titles_and_ratings_list, key=lambda x: x[1], reverse=True)
    top_three_rated = sorted_high_low[:3]

    return top_three_rated


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


def save_book_recommendations():
    for book in top_three_rated:
        add_to_recommended_books_list = recommended_books_list.append(book[:5])


def present_books_to_user():
    print("Here Are Your Happy Book Recommendations!")
    for row in top_three_rated:
        save_book = input("Add " + row[0] + " To Your Reading List? (Y/N) ")
        if save_book.lower() in ["yes", "y"]:
            add_to_reading_list = reading_list.append(row[:5])
        elif save_book.lower() in ["no","n"]:
            print("Okay, I'll Just Add It To Your Recommended Books List")
            timeout=1000
    print("READING LIST")
    print(reading_list)
    print("RECOMMENDED BOOKS LIST")
    print(recommended_books_list)


def add_book_mood_headings(answer_tree, user_name):
    if not any(row[0] == user_mood for row in recommended_book_headings):
        inner_recommended_list = [user_mood]
        recommended_book_headings.append(inner_recommended_list)
    else:
        for row in recommended_book_headings:
            if row[0] == user_mood:
                row.extend(recommended_books_list)

    if not any(row[0] == user_mood for row in reading_list_headings):
        inner_reading_list = [user_mood]
        reading_list_headings.append(inner_reading_list)
    else:
        for row in reading_list_headings:
            if row[0] == user_mood:
                row.extend(reading_list)

    return reading_list_headings, recommended_book_headings


'''if not any(row and row[0] == user_mood for row in static_reading_headings_list):
        new_row = [user_mood] + reading_list
        static_reading_headings_list.append(new_row)
    else:
        for row in static_reading_headings_list:
            if row[0] == user_mood:
                row.extend(reading_list)
                break'''




'''if not any(row and row[0] == user_mood for row in static_reading_headings_list):
        [user_mood].extend(reading_list)
        static_reading_headings_list.extend([user_mood])

        #for row in  static_reading_headings_list:
            #if row[0] == user_mood:


    return static_reading_headings_list, reading_list_headings'''

        # Now, find that sublist and extend it with this round's reading list
        #for row in static_reading_headings_list:
            #if row[0] == user_mood:
              #  row.extend(reading_list)
                #break




'''if not any(isinstance(row, list) and row and row[0] == user_mood for row in reading_list_headings):
        inner_reading_list = [user_mood]
        reading_list_headings.append(inner_reading_list)
    else:
        for row in reading_list_headings:
            if row[0] == user_mood:
                row.extend(reading_list)'''

'''if not any(isinstance(row, list) and row and row[0] == user_mood for row in recommended_book_headings):
        inner_recommended_list = [user_mood]
        recommended_book_headings.append(inner_recommended_list)
        return None
    else:
        for row in recommended_book_headings:
            if row[0] == user_mood:
                row.extend(recommended_books_list)
                
        return reading_list_headings, recommended_book_headings'''


def view_reading_list():
    open_reading_list = input("View Reading List?")
    if open_reading_list.lower() == "Yes":
        print(reading_list)
    elif open_reading_list.lower() == "No":
        print(' ')


def view_recommended_list():
    open_recommended_list = input("View Recommended List?")
    if open_recommended_list.lower() == "Yes":
        print(reading_list)
    elif open_recommended_list.lower() == "No":
        print(' ')


with (sync_playwright() as p):
    user_mood = mood_quiz()
    open_webpage_choose_mood(user_mood)
    scrape_book_info()
    three_highest_ratings()
    save_book_recommendations()
    present_books_to_user()
    add_book_mood_headings(answer_tree, user_mood)
    print("READING LIST HEADINGS")
    print(reading_list_headings)
    print("RECOMMENDED LIST HEADINGS")
    print(recommended_book_headings)
    #print("RECOMMENDED LIST HEADINGS")
    #print(recommended_book_headings)

    #page.pause()




