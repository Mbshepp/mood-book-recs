CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    rating REAL,
    author TEXT,
    summary TEXT,
    purchase_link TEXT,
    image_url TEXT
);


CREATE TABLE IF NOT EXISTS recommended_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    rating TEXT,
    author TEXT,
    summary TEXT,
    purchase_link TEXT,
    mood TEXT
);


CREATE TABLE IF NOT EXISTS reading_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    rating TEXT,
    author TEXT,
    summary TEXT,
    purchase_link TEXT,
    mood TEXT
);










