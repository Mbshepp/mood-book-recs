import requests
import re
from playwright.sync_api import sync_playwright
#from playwright.sync_api import sync_playwright



titles_and_ratings_list = []
recommended_books_list = []
reading_list = []
title_rating_list = []
book_title = None
recommended_book_headings = []
reading_list_headings = []
collective_answers = []


def build_answer_code(i, user_input):
    return "q" + str(i +1) + user_input.strip().lower()


# To ensure the user is only entering valid inputs.
def is_valid_quiz_input(user_input):
    return user_input.strip().lower() in ['a','b','c']


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


    for i, question in enumerate(quiz_questions):
        print(question)
        answer_row_index = answers[i]   # Get answer row index to build user input question with answer choices a,b, & c.

        while True:
            user_input = input(                     # To present the choices for each question for input.
                f" Choose: A, B, or C \n"
                f"{answer_row_index[0]}\n"          
                f"{answer_row_index[1]}\n"
                f"{answer_row_index[2]}"
            )

            if is_valid_quiz_input(user_input):
                user_input = user_input.strip().lower()
                break
            else:
                print("Invalid choice. Please enter A, B, or C.")


        user_answer = build_answer_code(i,user_input)                                              # Have an answer code for each user's choice to determine their mood.
        collective_answers.append(user_answer)
        print(collective_answers)

        for row in answer_tree:                                                                 # defines user_mood to be used in open_webpage_choose_mood function
            mood, triggers = row[0].split(": ")
            individual_triggers = [x.strip().lower() for x in triggers.split(",")]              # strip commas & whitespace to analyze if each individual trigger is present in collective_answers

            if any(trigger.lower() in collective_answers for trigger in individual_triggers):       # Check if this code gives me the output I want.
                user_mood = mood.lower()
                break
    return user_mood


def get_user_mood(collective_answers, answer_tree):
    for row in answer_tree:
        mood, triggers = row[0].split(":")
        individual_triggers = [x.strip().lower() for x in triggers.split(",")]
        if any(trigger in collective_answers for trigger in individual_triggers):
            return mood.lower()
        print("row[0] is:", row[0], "type:", type(row[0]))

    return None


def open_webpage_choose_mood(user_mood):
    global page
    browser = p.chromium.launch(headless=False)                                                     # To show browser actions as the code runs.
    page = browser.new_page()
    page.goto("https://booksbymood.com/")
    page.wait_for_selector("h2.text-3xl.font-semibold.text-accent.text-center.drop-shadow-md")      # ensures mood selector isn't searched for until page elements appear.

    selector = f'a[href*="{user_mood}"]'                                                            # The button/selector text is equal to user_mood.

    page.wait_for_selector(selector)                                                                # To ensure mood selector is loaded before attempting to click it.
    page.click(selector)


def scrape_book_info():
    global book_title
    global title_rating_list, book_title
    while len(titles_and_ratings_list) < 5:                                                                 # To select information for a maximum of five books.
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

            title_rating_list = [book_title, book_rating, author_selector, book_summary, purchase_link_locator, img_url]                        # To collect each books distinctive data
            titles_and_ratings_list.append(title_rating_list)                                                                                   # To store each books data to later sort and present to the user
            page.get_by_text("Next Book").scroll_into_view_if_needed()                                                                          # To ensure the "Next Book" button is visible.
            page.click(f"text={'Next Book'}")

    page.close()

    return title_rating_list


def three_highest_ratings():
    global top_three_rated
    top_three_rated = []
    #sorted_high_low = sorted(titles_and_ratings_list, key=lambda x: list(x.values())[0], reverse=True)
    sorted_high_low = sorted(titles_and_ratings_list, key=lambda x: x[1], reverse=True)                         # Sorting to only have to extract the three highest rated books later.
    top_three_rated = sorted_high_low[:3]                                                                       # To only present the top three rated books to the user.

    return top_three_rated


def get_real_amazon_url(purchase_link_locator):
    try:                                                                                                        # To Catch unsuccessful attempts to get amazon url.
        response = requests.get(purchase_link_locator, allow_redirects=True, timeout=5)
        return response.url                                                                                     # To later use to extract the book image url from Amazon and present amazon link to user.
    except Exception as e:
        print("Redirect failed", e)
        return None


def get_amazon_image_url(purchase_link_locator):
    real_url = get_real_amazon_url(purchase_link_locator)
    if real_url:
        match = re.search(r'/dp/(\w+)', real_url)                                                        # To find and extract the specific ID for the book within the link
        if match:
            amzn_link_tail = match.group(1)                                                                     #Extracts the book's ID from the URL for image lookup.
            return f"https://images-na.ssl-images-amazon.com/images/P/{amzn_link_tail}.01._SCLZZZZZZZ_.jpg"     # The amazon link needs the distinct tail portion for the image link.
    return None


def save_book_recommendations():
    for book in top_three_rated:
        add_to_recommended_books_list = recommended_books_list.append(book[:5])                                 # To track which books have already been recommended.


def present_books_to_user():
    print("Here Are Your Happy Book Recommendations!")
    for row in top_three_rated:
        save_book = input("Add " + row[0] + " To Your Reading List? (Y/N) ")                                    # To ask user if they want to save book title to reading list.
        if save_book.lower() in ["yes", "y"]:
            add_to_reading_list = reading_list.append(row[:5])                                                  # To save book info except the image url if user wants to save it to reading list.
        elif save_book.lower() in ["no","n"]:
            print("Okay, I'll Just Add It To Your Recommended Books List")
    print("READING LIST")
    print(reading_list)
    print("RECOMMENDED BOOKS LIST")
    print(recommended_books_list)


def add_book_mood_headings(answer_tree, user_name):
    # To organize recommended list books if heading not already present
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


def view_reading_list():
    open_reading_list = input("View Reading List?")
    if open_reading_list.lower() == "Yes":
        print(reading_list)
    elif open_reading_list.lower() == "No":
        print(' ')  # Placeholder if user doesn't want to view the list.


def view_recommended_list():
    open_recommended_list = input("View Recommended List?")
    if open_recommended_list.lower() == "Yes":
        print(recommended_books_list)
    elif open_recommended_list.lower() == "No":
        print(' ')





def main():
    user_mood = mood_quiz()


    with (sync_playwright() as p):
        open_webpage_choose_mood(user_mood)                     # To open website, select user's mood, and books based on the mood.
        scrape_book_info()                                      # To organize book details and present to the user.
        three_highest_ratings()                                 # To only show the user the top three books selected from the website.
        save_book_recommendations()                             # To keep track of all recommended books, so the user is presented with new choices later.
        present_books_to_user()                                 # To allow the user to view all book details and choose to save to reading list or recommended list.
        add_book_mood_headings(answer_tree, user_mood)          # To organize the books in the reading list and recommended list.
        print("READING LIST HEADINGS")
        print(reading_list_headings)
        print("RECOMMENDED LIST HEADINGS")
        print(recommended_book_headings)


if __name__ == "__main__":
    main()





