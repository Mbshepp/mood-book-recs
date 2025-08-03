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


def build_answer_code(i, user_input):
    """Builds a code, like 'q2a' for each answer to compare to the answer tree and find the user's mood."""
    return "q" + str(i +1) + user_input.strip().lower()


def is_valid_quiz_input(user_input):
    """"Validates that the user input is one of: A, B, or C."""
    return user_input.strip().lower() in ['a','b','c']


def mood_quiz(collective_answers, answer_tree):
    """Quizzes the user with 9 0questions to determine their mood."""
    global user_mood
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
    """Obtains the user's determined mood from the first index in the respective answer tree row."""
    for row in answer_tree:
        mood, triggers = row[0].split(":")
        individual_triggers = [x.strip().lower() for x in triggers.split(",")]
        if any(trigger in collective_answers for trigger in individual_triggers):
            return mood.lower()
        print("row[0] is:", row[0], "type:", type(row[0]))

    return None