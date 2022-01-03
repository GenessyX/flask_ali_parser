import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.exceptions import abort

from flaskr.db import get_db

from .ali_parser import (
    get_author_object,
    get_user_reviews_count,
    parse_product,
    parse_reviews,
    parse_user,
    search,
)
from .db_utils import (
    save_author,
    save_pictures,
    save_product,
    save_products,
    save_reviews,
    save_authors,
)

bp = Blueprint("ali_parser", __name__)


@bp.route("/")
def index():
    products = sorted(
        [row_to_dict(x) for x in get_products()],
        key=lambda d: d["reviews_count"],
        reverse=True,
    )[:25]

    users = get_users()
    for index, user in enumerate(users):
        user = row_to_dict(user)
        review_count = len(get_user_reviews(user["id"]))
        user["review_count"] = review_count
        users[index] = user
    users = sorted(users, key=lambda d: d["review_count"], reverse=True)[:25]
    return render_template("index.html", users=users, products=products)


def row_to_dict(row):
    d = dict()
    for key in row.keys():
        d[key] = row[key]
    return d


def get_products():
    db = get_db()
    products = db.execute("SELECT *" " FROM product").fetchall()
    return products


def get_product(id):
    db = get_db()
    product = db.execute(
        "SELECT id, title, link, descr, reviews_count" " FROM product" " WHERE id = ?",
        (id,),
    ).fetchone()

    if product is None:
        product = parse_product(id)
        save_product(product)

    return product


def get_product_reviews(product_id):
    db = get_db()
    reviews = db.execute(
        "SELECT r.id, author_id, a.username as author_username, a.link as author_link, product_id, body"
        " FROM review r JOIN author a ON a.id = author_id"
        " WHERE product_id = ?",
        (product_id,),
    ).fetchall()
    if not reviews:
        reviews, pictures, authors = parse_reviews(product_id)
        save_reviews(reviews)
        save_pictures(pictures)
        save_authors(authors)

    return reviews


def get_users():
    db = get_db()
    users = db.execute("SELECT *" " FROM author").fetchall()
    return users


def get_user(id):
    db = get_db()
    user = db.execute("SELECT *" " FROM author" " WHERE id = ?", (id,)).fetchone()
    return user


def get_user_reviews(author_id):
    db = get_db()
    reviews = db.execute(
        "SELECT r.id, author_id, product_id, body"
        " FROM review r JOIN author a ON a.id = author_id"
        " WHERE author_id = ?",
        (author_id,),
    ).fetchall()
    if not reviews:
        abort(404, f"Reviews for user_id {author_id} do not exist.")
    return reviews


def get_pictures(review_id):
    db = get_db()
    pictures = db.execute(
        "SELECT p.review_id, link, r.id"
        " FROM picture p JOIN review r ON p.review_id = r.id"
        " WHERE r.id = ?",
        (review_id,),
    ).fetchall()

    if pictures is None:
        pictures = []

    return pictures


def combine_reviews(reviews, gallery=False, product=False):
    if not (gallery or product):
        return reviews
    _reviews = []
    for index, review in enumerate(reviews):
        temp = row_to_dict(review)
        if gallery:
            pictures = get_pictures(review["id"])
            temp["gallery"] = pictures
        if product:
            product = get_product(review["product_id"])
            temp["product"] = product

        _reviews.append(temp)
    return _reviews


@bp.route("/id/<int:id>")
def product_page(id: int):
    product = get_product(id)
    _reviews = get_product_reviews(id)
    reviews = combine_reviews(_reviews, gallery=True)

    return render_template("product.html", product=product, reviews=reviews)


@bp.route("/search", defaults={"search_text": None, "parse": 0})
@bp.route("/search/<string:search_text>/", defaults={"parse": 0})
@bp.route("/search/<string:search_text>/<int:parse>/")
def search_page(search_text, parse):

    if search_text:
        products = search(search_text)
        if products:
            save_products(products)
            if parse:
                for product in products:
                    get_product_reviews(product["id"])

    else:
        products = []

    return render_template("search.html", products=products)


@bp.route("/user/<int:author_id>")
def user_page(author_id: int):
    user = get_user(author_id)
    # if user:
    #     _reviews = get_user_reviews(author_id)
    #     if len(_reviews) == get_user_reviews_count(author_id):
    #         reviews = combine_reviews(_reviews, gallery=True, product=True)

    # else:
    #     products = parse_user(author_id)
    #     for _product in products:
    #         product = get_product(int(_product))
    #         _reviews = get_product_reviews(int(_product))

    if not user:
        user = get_author_object(id)
        save_author(user)
        products = parse_user(author_id)
        for _product in products:
            product = get_product(int(_product))
            _reviews = get_product_reviews(int(_product))
    else:
        _reviews = get_user_reviews(author_id)
        if len(_reviews) != get_user_reviews_count(author_id):
            products = parse_user(author_id)
            for _product in products:
                product = get_product(int(_product))
                _reviews = get_product_reviews(int(_product))

    _reviews = get_user_reviews(author_id)
    reviews = combine_reviews(_reviews, gallery=True, product=True)

    return render_template("user.html", reviews=reviews, user=user)
