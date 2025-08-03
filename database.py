import sqlite3

def create_tables_from_schema(db_name="moodbooks.db", schema_path="schema.sql"):
    """Creates database tables by executing SQL commands from the schema.sql file."""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        with open(schema_path, "r") as f:
            cursor.executescript(f.read())
        print("Database tables created successfully.")


def initialize_database():
    """Initializes the database by reading and executing the schema.sql script."""
    conn = sqlite3.connect("moodbooks.db")
    cursor = conn.cursor()
    with open("schema.sql", "r") as f:
        schema_script = f.read()
    cursor.executescript(schema_script)
    conn.commit()
    conn.close()


def add_book_to_reading_list(book, mood):
    """Inserts a book and its associated mood into the reading_list table."""
    conn = sqlite3.connect("moodbooks.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reading_list (title, rating, author, summary, purchase_link, mood) VALUES (?,?,?,?,?,?)",
        (book[0], book[1], book[2], book[3], book[4], mood)
    )
    conn.commit()
    conn.close()


def add_book_to_recommended_books(book,mood):
    """Inserts a book and its associated mood into the recommended_books table."""
    conn = sqlite3.connect("moodbooks.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recommended_books (title, rating, author, summary, purchase_link, mood) VALUES (?,?,?,?,?,?)",
        (book[0], book[1], book[2], book[3], book[4], mood)
    )
    conn.commit()
    conn.close()


def get_reading_list():
    """Retrieves all book IDs and titles from the reading_list table."""
    conn = sqlite3.connect("moodbooks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM reading_list")
    books = cursor.fetchall()
    conn.close()
    return books


def delete_book_from_reading_list(book_id):
    """Deletes a book from the reading_list table based on its ID."""
    conn = sqlite3.connect("moodbooks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reading_list WHERE id =?", (book_id,))
    conn.commit()
    conn.close()


