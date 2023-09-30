from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import random
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

blp = Blueprint('costco', __name__, description='Operations on costco')


class CostcoSchema(Schema):
    keyword = fields.Str(required=True)
class ItemSchema(Schema):
    item_id = fields.Str(dump_only=True)
    product_name = fields.Str(dump_only=True)


@blp.route('/item')
class Costco(MethodView):

    @blp.arguments(CostcoSchema, location='query')
    @blp.response(200, ItemSchema)
    def get(self, search_term):
        try:
            item = search_term.get('keyword')
            headers = {
                "User-Agent": random.choice(user_agents),
            }
            costco_res = requests.get(url=f'https://www.costco.com/CatalogSearch?dept=All&keyword={item}', headers=headers)
            soup = BeautifulSoup(costco_res.content, "html.parser")
            no_result = soup.find("h2", {"automation-id": "noResultsFound"})
            suggested_items = soup.find(string="We were not able to find a match. Try another search or shop related products.")
            if no_result:
                abort(404, message='The item you are looking for was not found.')
            elif suggested_items:
                abort(404, message='Your searched returned only related products.')
            else:
                item_id = soup.find_all("div", class_="thumbnail", limit=1)[0]['itemid']
                
                product_name = soup.find_all("a", attrs={"automation-id": "productDescriptionLink_0"}, limit=1)[0].get_text()
                
                return {"item_id": item_id, "product_name": ' '.join(product_name.split())}
        except Exception as e:
            abort(400, message=str(e))