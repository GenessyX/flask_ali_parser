# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3
from flaskr.db import get_db
from collections import Counter
from typing import List

product_fields = ["id", "title", "link", "descr", "reviews_count", "preview_img"]
review_fields = ["id", "author_id", "product_id", "body", "country"]
picture_fields = ["review_id", "link"]
author_fields = ["id", "username", "link"]


def validate(scheme: list, object: dict) -> bool:
    return Counter(scheme) == Counter(object.keys())


def save_product(product: dict):
    error = None
    print(product)
    if validate(product_fields, product):
        db = get_db()
        try:
            db.execute(
                "INSERT INTO product (id, title, link, descr, reviews_count, preview_img)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    product["id"],
                    product["title"],
                    product["link"],
                    product["descr"],
                    product["reviews_count"],
                    product["preview_img"],
                ),
            )
            db.commit()
        except sqlite3.IntegrityError:
            print(product)
            if product["title"] or product["descr"] or product["preview_img"]:
                db.execute(
                    "UPDATE product SET title = ?, descr = ?, preview_img = ?"
                    " WHERE id = ?",
                    (
                        product["title"],
                        product["descr"],
                        product["preview_img"],
                        product["id"],
                    ),
                )
                db.commit()
            else:
                print("There is same product")


def save_products(products: List[dict]):
    error = None
    for product in products:
        save_product(product)


def save_reviews(reviews: List[dict]):
    error = None
    for review in reviews:
        if validate(review_fields, review):
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO review (id, author_id, product_id, body, country)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (
                        review["id"],
                        review["author_id"],
                        review["product_id"],
                        review["body"],
                        review["country"],
                    ),
                )
                db.commit()
            except sqlite3.IntegrityError:
                print("There is same review")


def save_pictures(pictures: List[dict]):
    error = None
    for picture in pictures:
        if validate(picture_fields, picture):
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO picture (review_id, link)" " VALUES (?, ?)",
                    (
                        picture["review_id"],
                        picture["link"],
                    ),
                )
                db.commit()
            except sqlite3.IntegrityError:
                print("There is same picture")


def save_author(author: dict):
    error = None
    if validate(author_fields, author):
        db = get_db()
        try:
            db.execute(
                "INSERT INTO author (id, username, link)" " VALUES (?, ?, ?)",
                (author["id"], author["username"], author["link"]),
            )
            db.commit()
        except sqlite3.IntegrityError:
            print("There is same author")


def save_authors(authors: List[dict]):
    error = None
    for author in authors:
        save_author(author)
