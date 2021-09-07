from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_restful import Api


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#api = Api(app, decorators=[csrf.exempt])
api = Api(app)


app.secret_key = 'some_random_key'

from my_app.catalog.views import catalog


app.register_blueprint(catalog)

db.create_all()
