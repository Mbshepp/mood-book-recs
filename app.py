import requests
import re
from playwright.sync_api import sync_playwright
import sqlite3
import os
from database import (
    get_reading_list,
    delete_book_from_reading_list,
    add_book_to_reading_list,
    initialize_database,
    create_tables_from_schema
)

from quiz_logic import (
    mood_quiz,
    build_answer_code,
    is_valid_quiz_input,
    get_user_mood,
    answer_tree
)


collective_book_list = []
recommended_books_list = []
reading_list = []
individual_book_info = []
book_title = None
recommended_book_headings = []
reading_list_headings = []
collective_answers = []


# ------------   MAIN MENU ----------------------------
def main_menu(answer_tree):
    """ Presents the user with menu choices to navigate the app."""
    while True:
        print("\nWhat would you like to do?")
        print("1. Take the Mood Quiz")
        print("2. View Reading List")
        print("3. View Recommended List")
        print("4. Exit")

        menu_choice = input("Enter your choice (1-4): ").strip()

        if menu_choice == "1":
            main()
        elif menu_choice == "2":
            books = get_reading_list()
            if not books:
                print("\nYour  reading list is empty.")
            else:
                print("\nYour Reading List:")
                for book in books:
                    print(f"{book[0]}. {book[1]}")

                while True:
                    delete_book = input("\nWould you like to remove a book? (Y/N").strip().lower()
                    if delete_book in ["y", "yes"]:
                        try:
                            book_id = int(input("Enter the ID of the book to remove: "))
                            delete_book_from_reading_list(book_id)
                            print(f"Removed book with ID: {book_id}")
                            break
                        except ValueError:
                            print("Please enter a valid number")
                    elif delete_book in ["n", "no"]:
                        break
                    else:
                        print("Invalid input. Please enter Y or N.")
        elif menu_choice == "3":
            print("Recommended List")
            print(recommended_books_list)
        elif menu_choice == "4":
            print("Goodbye")
            break
        else:
            print("Invalid option. Please enter a number between 1 and 4.")


# --------------------  SCRAPING LOGIC --------------------------------

def open_webpage_choose_mood(user_mood,p):
    """ Opens a headless browser and navigates to booksbymood.com"""
    global page
    browser = p.chromium.launch(headless=False)                                                     # To show browser actions as the code runs.
    page = browser.new_page()
    page.goto("https://booksbymood.com/")
    page.wait_for_selector("h2.text-3xl.font-semibold.text-accent.text-center.drop-shadow-md")      # ensures mood selector isn't searched for until page elements appear.

    selector = f'a[href*="{user_mood}"]'                                                            # The button/selector text is equal to user_mood.
    page.wait_for_selector(selector)                                                                # To ensure mood selector is loaded before attempting to click it.
    page.click(selector)


def scrape_book_info():
    """Scrapes each book's information like title, author, summary, rating, amazon link, and image url."""
    global book_title
    global individual_book_info, book_title
    while len(collective_book_list) < 5:                                                                 # To select information for a maximum of five books.
        book_title = page.inner_text("h2")
        if book_title in recommended_books_list:                                                            # To ensure only books that have not been previously recommended are recommended to the user.
            page.get_by_text("Next Book").scroll_into_view_if_needed()                                      # To find the "Next Book" button
            page.click(f"text={'Next Book'}")
        else:
            rating_selector = 'div.tooltip.tooltip-top.md\\:tooltip-right[data-tip^="From GoodReads"]'
            book_rating = (page.inner_text(rating_selector))
            a, b = book_rating.split("/")                                                                      # To make the rating fraction usable as two floats for sorting.
            float(a) / float(b)
            author_selector = page.inner_text("span.text-gray-500.drop-shadow-md")
            book_summary = page.inner_text("div.pt-2.leading-relaxed.drop-shadow-md")
            page.wait_for_selector("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg")                                         # To make sure purchase link selector loads before trying to save it.
            purchase_link_locator = page.locator("a.btn.w-full.justify-self-center.rounded-lg.bg-base-300.shadow-lg").get_attribute('href')
            get_real_amazon_url(purchase_link_locator)                                                                                          # Amazon link URL is embedded in the Purchase link locator. I need to extract and present it to user.
            get_amazon_image_url(purchase_link_locator)                                                                                         # Book image URL is embedded in the Purchase link locator. I need to extract and present it to user.
            img_url = get_amazon_image_url(purchase_link_locator)                                                                               # To later create code to show user the books image

            individual_book_info = [book_title, book_rating, author_selector, book_summary, purchase_link_locator, img_url]                        # To collect each book's distinctive data
            collective_book_list.append(individual_book_info)                                                                                   # To store each books data to later sort and present to the user
            page.get_by_text("Next Book").scroll_into_view_if_needed()                                                                          # To ensure the "Next Book" button is visible.
            page.click(f"text={'Next Book'}")
    page.close()
    return individual_book_info


def get_real_amazon_url(purchase_link_locator):
    """ Takes the URL and follows redirects to find the final URL for the book on Amazon."""
    try:                                                                                                        # To catch unsuccessful attempts to get amazon url.
        response = requests.get(purchase_link_locator, allow_redirects=True, timeout=5)
        return response.url                                                                                     # To later use to extract the book image url from Amazon and present amazon link to user.
    except Exception as e:
        print("Redirect failed", e)
        return None


def get_amazon_image_url(purchase_link_locator):
    """ Builds a direct link to the book cover image using the URL product ID. """
    real_url = get_real_amazon_url(purchase_link_locator)
    if real_url:
        match = re.search(r'/dp/(\w+)', real_url)                                                        # To find and extract the specific ID for the book within the link
        if match:
            amzn_link_tail = match.group(1)                                                                     #Extracts the book's ID from the URL for image lookup.
            return f"https://images-na.ssl-images-amazon.com/images/P/{amzn_link_tail}.01._SCLZZZZZZZ_.jpg"     # The amazon link needs the distinct tail portion for the image link.
    return None



# ------------------------ BOOK PROCESSING -----------------------------

def three_highest_ratings(book_list=None):
    """Sorts the selected books by rating from high to low and retains the top three books only."""
    global top_three_rated
    if book_list is None:
        book_list = collective_book_list

    sorted_high_low = sorted(book_list, key=lambda x: x[1], reverse=True)                         # Sorting to only have to extract the three highest rated books later.
    top_three_rated = sorted_high_low[:3]                                                                       # To only present the top three rated books to the user.
    return top_three_rated


def save_book_recommendations():
    """Saves all recommended books information to a list except the img URL."""
    for book in top_three_rated:
        add_to_recommended_books_list = recommended_books_list.append(book[:5])                                 # To track which books have already been recommended.


def present_books_to_user(user_mood):
    """Presents the user with the top three rated books and their information and asks if they want to add them to the reading list."""
    print("Here Are Your Happy Book Recommendations!")
    for row in top_three_rated:
        save_book = input("Add " + row[0] + " To Your Reading List? (Y/N)")                                    # To ask user if they want to save book title to reading list.
        if save_book.lower() in ["yes", "y"]:
            add_book_to_reading_list(row[:5], user_mood)
        elif save_book.lower() in ["no","n"]:
            print("Okay, I'll Just Add It To Your Recommended Books List")
    print("READING LIST")
    print(reading_list)
    print("RECOMMENDED BOOKS LIST")
    print(recommended_books_list)


def add_book_mood_headings(answer_tree, user_mood):
    """Adds headings to reading and recommended lists if heading not already present."""
    if not any(row[0] == user_mood for row in recommended_book_headings):
        inner_recommended_list = [user_mood]
        recommended_book_headings.append(inner_recommended_list)
    else:
        for row in recommended_book_headings:
            if row[0] == user_mood:
                row.extend(recommended_books_list)

    # To organize Reading list books if heading not already present
    if not any(row[0] == user_mood for row in reading_list_headings):
        inner_reading_list = [user_mood]
        reading_list_headings.append(inner_reading_list)
    else:
        for row in reading_list_headings:
            if row[0] == user_mood:
                row.extend(reading_list)
    return reading_list_headings, recommended_book_headings


def main():
    """Runs the core logic for the app."""
    user_mood = mood_quiz(collective_answers, answer_tree)
    if not os.path.exists("moodbooks.db"):
        initialize_database()

    with (sync_playwright() as p):
        open_webpage_choose_mood(user_mood,p)                   # To open website, select user's mood, and books based on the mood.
        scrape_book_info()                                      # To organize book details and present to the user.
        three_highest_ratings()                                 # To only show the user the top three books selected from the website.
        save_book_recommendations()                             # To keep track of all recommended books, so the user is presented with new choices later.
        present_books_to_user(user_mood)                                 # To allow the user to view all book details and choose to save to reading list or recommended list.
        add_book_mood_headings(answer_tree, user_mood)          # To organize the books in the reading list and recommended list.


if __name__ == "__main__":
    main_menu(answer_tree)





