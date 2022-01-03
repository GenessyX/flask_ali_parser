from typing import List, Tuple
import requests
import os
import random
import string
import json
from bs4 import BeautifulSoup

base_url = "https://aliexpress.ru/aer-api/v1/review/filters?product_id={}"
categories_url = "https://aliexpress.ru/aer-webapi/v1/recommend"
user_url_detail = "https://feedback.aliexpress.com/display/detail.htm?ownerMemberId={}&memberType=buyer"
user_url = "https://feedback.aliexpress.com/display/detail.htm"


def parse_product(id: int) -> dict:
    review_count = get_review_count(id)
    return {
        "id": id,
        "title": "",
        "link": "https://aliexpress.ru/item/{}".format(str(id)),
        "descr": "",
        "reviews_count": review_count,
        "preview_img": "",
    }


def get_author_id(userUrl: str) -> int:
    if "ownerMemberId" in userUrl:
        id = int(userUrl.split("ownerMemberId=")[1].split("&")[0])
    else:
        id = 0
    return id


def get_author_object(id: int) -> dict:
    _user_url = user_url_detail.format(str(id))
    resp = requests.get(_user_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    username = soup.find("span", {"id": "memberVipLevel"}).text
    return {"id": id, "username": username, "link": user_url_detail.format(str(id))}


def remove_duplicates(l):
    return [dict(x) for x in {tuple(d.items()) for d in l}]


def parse_reviews(id: int) -> Tuple[List[dict], List[dict]]:
    reviews = get_reviews(id)
    reviews = [x for x in reviews if x["gallery"]]
    pictures = []
    authors = []
    for index, review in enumerate(reviews):
        author_id = get_author_id(review["userUrl"])
        temp = {
            "id": review["id"],
            "author_id": author_id,
            "product_id": id,
            "body": review["text"],
            "country": review["country"],
        }
        authors.append(
            {"id": author_id, "username": review["username"], "link": review["userUrl"]}
        )
        for pictureUrl in review["gallery"]:
            picture = {"review_id": review["id"], "link": pictureUrl}
            pictures.append(picture)
        reviews[index] = temp

    reviews = remove_duplicates(reviews)
    return reviews, pictures, authors


def get_user_reviews_count(id: int) -> int:
    params = {"ownerMemberId": str(id), "memberType": "buyer"}
    resp = requests.get(user_url, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")

    reviews_count = int(
        soup.find("a", {"class": "list_dispatche"}).text.split("(")[1].split(")")[0]
    )
    return reviews_count


def parse_user(id: int):
    products = []

    reviews_count = get_user_reviews_count(id)
    pages = ((reviews_count - 1) // 10) + 1
    for page in range(pages):
        data = {"ownerMemberId": str(id), "memberType": "buyer", "page": str(page + 1)}
        resp = requests.post(user_url, data=data)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"class": "rating-table"})
        tbody = table.find("tbody")
        trs = tbody.find_all("tr")
        for tr in trs:
            product_link = (
                tr.find("td", {"class": "td4"})
                .find("span", {"class": "product-name"})
                .find("a")
                .attrs["href"]
            )
            product_id = product_link.split("/")[-1].split(".")[0]
            products.append(product_id)

    return list(set(products))


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
        ("'", "&#39;"),
        ('"', "&quot;"),
        (">", "&gt;"),
        ("<", "&lt;"),
        ("&", "&amp;"),
    )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s


def search(search_text):
    url = "https://aliexpress.ru/price/api_price_0.html"
    params = {
        "seoChannel": "popular",
        "trafficChannel": "seo",
        "SearchText": search_text,
        "ltype": "p",
        "SortType": "total_tranpro_desc",
        "groupsort": "1",
        "isrefine": "y",
        "page": "1",
        "origin": "y",
    }
    resp = requests.get(url, params=params)
    res = json.loads(html_decode(resp.text))["items"]
    products = []
    for index, item in enumerate(res):
        review_count = get_review_count(item["productId"])
        if review_count == 0:
            pass
        else:
            temp = {
                "id": item["productId"],
                "title": item["title"],
                "link": "",
                "descr": "",
                "reviews_count": review_count,
                "preview_img": item["imageUrl"],
            }
            products.append(temp)
    return products


def get_reviews(id):
    reviews = []
    url = base_url.format(str(id))
    page_n = 1
    payload = {
        "productId": int(id),
        "starFilter": "all",
        "sort": "default",
        "page": page_n,
        "pageSize": 100,
        "translate": True,
        "local": False,
    }
    resp = requests.post(url=url, json=payload)
    if not "reviews" in resp.json()["reviewInfo"].keys():
        return reviews
    while resp.json()["reviewInfo"]["reviews"]:
        reviews_page = resp.json()["reviewInfo"]["reviews"]
        reviews += reviews_page
        payload["page"] += 1
        try:
            resp = requests.post(url=url, json=payload)
        except Exception as e:
            print(e)
            resp = None
    return reviews


def get_review_count(id):
    url = base_url.format(str(id))
    page_n = 1
    payload = {
        "productId": int(id),
        "starFilter": "all",
        "sort": "default",
        "page": page_n,
        "pageSize": 0,
        "translate": True,
        "local": False,
    }
    resp = requests.post(url=url, json=payload)
    # return resp.content
    return resp.json()["reviewInfo"]["filters"]["withPhoto"]


def download_image(folder, file_name, url):
    folder = str(folder)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    file_extension = url.split(".")[-1]
    path = os.path.join(folder, file_name + "." + file_extension)
    with open(path, "wb") as f:
        f.write(requests.get(url).content)

    # img = requests.get(url)


def get_pics(id, reviews):
    if not os.path.isdir(str(id)):
        os.mkdir(str(id))
    for ind, review in enumerate(reviews):
        if review["gallery"]:
            if review["username"] != "AliExpress Shopper":
                username = review["username"]
            else:
                username = "".join(
                    random.choice(string.ascii_uppercase) for _ in range(6)
                )
            if len(review["gallery"]) > 1:
                ind = 1

                for pic in review["gallery"]:
                    file_name = username + "_" + str(ind)
                    download_image(id, file_name, pic)
                    ind += 1
            else:
                for pic in review["gallery"]:
                    download_image(id, username, pic)


def get_category(cat_id, page):
    count = 100
    offset = (page - 1) * count
    payload = {
        "categoryIds": str(cat_id),
        "count": count,
        "currencyType": "RUB",
        "keyword": "keyword",
        "offset": offset,
    }
    resp = requests.post(categories_url, json=payload)
    _products = resp.json()["data"]["productsFeed"]["products"]
    products = []
    for index, product in enumerate(_products):
        review_count = get_review_count(product["id"])
        if review_count == 0:
            pass
        else:
            products.append(product)
            products[-1]["reviewCount"] = review_count
    return products


def main():
    pass


if __name__ == "__main__":
    main()
