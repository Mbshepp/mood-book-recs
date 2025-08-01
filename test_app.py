from app import(
    is_valid_quiz_input,
    build_answer_code,
    get_user_mood,
    answer_tree
)


def test_is_valid_quiz_input():
    #Valid Inputs
    assert is_valid_quiz_input("A")
    assert is_valid_quiz_input("B")
    assert is_valid_quiz_input("c")

    #Invalid Inputs
    assert not is_valid_quiz_input("D")
    assert not is_valid_quiz_input("apple")
    assert not is_valid_quiz_input("")


def test_build_answer_code():
    assert build_answer_code(1, "A") =="q2a"
    assert build_answer_code(5, "b") == "q6b"
    assert build_answer_code(9, "c") == "q10c"


def test_get_user_mood_happy():
    answers = ['q1a', 'q4a', 'q7a', 'q9a']
    assert get_user_mood(answers, answer_tree) == 'happy'


def test_get_user_mood_inspired():
    answers = ['q2b', 'q5a', 'q7c', 'q8b']
    assert get_user_mood(answers, answer_tree) == 'inspired'


