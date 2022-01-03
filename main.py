from flask import Flask
from flask import render_template
from flask import url_for
from pycountry import countries

import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ali_parser import get_category, get_reviews, search

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    return "index page"


@app.route("/id/<int:id>")
def reviews_parse(id):
    reviews = get_reviews(id)
    reviews = [x for x in reviews if x["gallery"]]
    for index, review in enumerate(reviews):
        try:
            reviews[index]["country"] = countries.get(alpha_2=review["country"]).name
        except:
            pass
    return render_template("find.html", reviews=reviews)


@app.route("/category/<int:id>/<int:page>")
def category_parse(id, page):
    products = get_category(id, page)
    return render_template("category.html", products=products)


@app.route("/search/<string:search_text>")
def search_page(search_text):
    products = search(search_text)
    return render_template("search.html", products=products)
