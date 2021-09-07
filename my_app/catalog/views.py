from flask import request, jsonify, Blueprint, render_template, flash, redirect, abort
from my_app import ALLOWED_EXTENSIONS
from flask.helpers import url_for
from werkzeug.utils import secure_filename
from my_app import db, app
from my_app.catalog.models import Product, Category
from sqlalchemy.orm.util import join
from flask_restful import Resource
from my_app import api
import json
from flask import abort
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('price', type=float)
parser.add_argument('category', type=dict)



#from functools import wraps

catalog = Blueprint('catalog', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


'''
prints "Welcome to the catalog home" on the index route 
'''
@catalog.route('/home')
@catalog.route('/')
def home():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        products = Product.query.all()
        return jsonify({
            'count' : len(products)
        })
    return render_template('home.html')

 
@catalog.route('/product/<id>')
def product(id):
    product = Product.query.get_or_404(id)
    return render_template('product.html', product=product)


@catalog.route('/products')
@catalog.route('/products/<int:page>')
def products(page=1):
    products = Product.query.paginate(page, 10)
    return render_template('products.html', products=products)


@catalog.route('/product-create', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        categ_name = request.form.get('category')
        category = Category.query.filter_by(name=categ_name).first()
        if not category:
            category = Category(categ_name)
        product = Product(name, price, category)
        db.session.add(product)
        db.session.commit()
        flash('The product %s has been created' % name, 'success')
        return redirect(url_for('catalog.product', id=product.id))
    return render_template('product-create.html')


@catalog.route('/product-search')
@catalog.route('/product-search/<int:page>')
def product_search(page=1):
    name = request.args.get('name')
    price = request.args.get('price')
    company = request.args.get('company')
    category = request.args.get('category')
    products = Product.query
    if name:
        products = products.filter(Product.name.like('%' + name + '%'))
    if price:
        products = products.filter(Product.price == price)
    if company:
        products = products.filter(Product.company.like('%' + company + '%'))
    if category:
        products = products.select_from(join(Product, Category)).filter(
            Category.name.like('%' + category + '%')
        )
    return render_template(
        'products.html', products=products.paginate(page, 10)
    )


@catalog.route('/category-create', methods=['POST','GET'])
def create_category():
    name = request.form.get('name')
    category = Category(name)
    db.session.add(category)
    db.session.commit()
    return render_template('category.html', category=category)


@catalog.route('/category/<id>')
def category(id):
    category = Category.query.get_or_404(id)
    return render_template('category.html', category=category)


@catalog.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

class ProductApi(Resource):
    def get(self, id=None, page=1):
        if not id:
            products = Product.query.paginate(page, 10).items
        else:
            products = [Product.query.get(id)]
        if not products:
            abort(404)
        res = {}
        for product in products:
            res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name
        }
        return json.dumps(res)

    def post(self):
        args = parser.parse_args()
        name = args['name']
        price = args['price']
        categ_name = args['category']['name']
        category = Category.query.filter_by(name=categ_name).first()
        if not category:
            category = Category(categ_name)
        product = Product(name, price, category)
        db.session.add(product)
        db.session.commit()
        res = {}
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name
        }

        return json.dumps(res)


    def put(self, id):
        args = parser.parse_args()
        name = args['name']
        price = args['price']
        categ_name = args['category']['name']
        category = Category.query.filter_by(name=categ_name).first()
        product = Product.query.filter_by(id=id).update({
            'name': name,
            'price': price,
            'category_id': category.id 
        })
        db.session.commit()
        res = {}
        res[product.id] = {
            'name' : product.name,
            'price': product.price,
            'category' : product.category.name

        }

    def delete(self, id):
        product = Product.query.filter_by(id=id).delete()
        product.delete()
        db.session.commit()
        return json.dumps({'response': 'Success'})


api.add_resource(
ProductApi,
'/api/product',
'/api/product/<int:id>',
'/api/product/<int:id>/<int:page>'
)