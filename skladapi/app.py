from flask import Flask, request, jsonify, Blueprint
from skladapi.extensions import jwt, jwt_required, get_jwt_identity, get_jwt_claims
from skladapi.extensions import fbcrypt
from skladapi.models import db
from pymysql.err import IntegrityError
from json import loads


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    config_app(app, config)
    register_extensions(app)
    register_models(app)
    register_routes_api(app)
    return app


def register_extensions(app):
    jwt.init_app(app)
    fbcrypt.init_app(app)


def register_models(app):
    db.init_app(app)


def config_app(app, config):
    class BaseCfg:
        SQLALCHEMY_TRACK_MODIFICATIONS = False

    class TestingCfg(BaseCfg):
        TESTING = True
        DEBUG = False

    class DevelopmentCfg(BaseCfg):
        EXPLAIN_TEMPLATE_LOADING = True
        DEBUG = True

    if config == "development":
        app.config.from_object(DevelopmentCfg)
        app.config.from_pyfile('development.py', silent=False)
    elif config == "testing":
        app.config.from_object(TestingCfg)
        app.config.from_pyfile('testing.py', silent=False)


def register_routes_api(app):
    from skladapi.models import check_credentials

    api = Blueprint('api', __name__)

    @api.route('/login', methods=['POST'])
    def get_auth_token():
        try:
            data = request.get_json()
            username = data['username']
            password = data['password']
            access_token = check_credentials(username, password)
            if access_token:
                return jsonify({"access_token": access_token}), 200
            else:
                return jsonify({"msg": "Bad credentials."})
        except KeyError:
            return jsonify({"msg": "No credentials were sent."})
        except TypeError:
            return jsonify({"msg": "No credentials were sent."})
        except Exception as ex:
            return jsonify({"msg": "Cannot create token - " + str(ex)})

    @api.route('/time', methods=['GET'])
    @jwt_required
    def test_method_time():
        claims = get_jwt_claims()
        return jsonify({'claims': claims})

    @api.route('/users', methods=['POST'])
    @jwt_required
    def create_user():

        request_json = request.get_json()

        if request_json is not None:
            try:
                name = request_json['user']
                password = request_json['password']
                oscislo = request_json['oscislo']
                id_pobocka = request_json['id_pobocka']

                from skladapi.models import Uzivatel
                uzivatel = Uzivatel(osobni_cislo=oscislo, jmeno=name, password=password, id_pobocka=id_pobocka)
                db.session.add(uzivatel)
                db.session.commit()
                return jsonify({"id": Uzivatel.query.filter_by(osobni_cislo=oscislo).first().id}), 200
            except KeyError as ke:
                return jsonify("bad arguments", str(ke)), 400
            except IntegrityError:
                return jsonify("user already exists"), 400
            except Exception as ex:
                return jsonify("uknown error"), 400

    app.register_blueprint(api, url_prefix='/api')
