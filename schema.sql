DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS search_text;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS picture;

CREATE TABLE product (
    id INTEGER PRIMARY KEY,
    title TEXT,
    link TEXT,
    descr TEXT,
    preview_img TEXT,
    reviews_count INTEGER
);

CREATE TABLE author (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    link TEXT NOT NULL
);

CREATE TABLE review (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    body TEXT,
    country TEXT,
    FOREIGN KEY (product_id) REFERENCES product (id)
    FOREIGN KEY (author_id) REFERENCES author (id)
);

CREATE TABLE picture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    link TEXT NOT NULL,
    FOREIGN KEY (review_id) REFERENCES review (id)
);