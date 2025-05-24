from flask import Flask
from PIL import Image
from playwright.sync_api import sync_playwright

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

def scrape_book_info():
    Book_Title = page.inner_text("h2")
    print(Book_Title)
    Book_Rating = page.inner_text("/html/body/div/main/div/div[2]/div[2]/span/div")
    print(Book_Rating)
    
def parse_books():
    #Add If/Then: If book is already in Recommended Books list. If it is go to "Next Book" If it's not, scrape book info.
    page.get_by_text("Next Book").scroll_into_view_if_needed()
    timeout=100
    page.click(f"text={'Next Book'}")
    scrape_book_info()


User_Mood = "Happy".lower()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://booksbymood.com/")
    page.wait_for_selector("h2.text-3xl.font-semibold.text-accent.text-center.drop-shadow-md")
    timeout=5000
    page.click(f"text={User_Mood}")
    parse_books()
    page.pause()










