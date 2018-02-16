from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
import datetime
from skladapi.extensions import jwt, create_access_token
from skladapi.extensions import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Vyvojar(db.Model):
    __tablename__ = "vyvojari"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jmeno = db.Column(db.VARCHAR(255), nullable=False)
    heslo = db.Column(db.VARCHAR(255), nullable=False)


class Pobocka(db.Model):
    __tablename__ = "pobocky"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    mesto = db.Column(db.VARCHAR(255), nullable=False)
    uzivatele = db.relationship('Uzivatel', backref='pobocka', lazy='dynamic')
    bezpecaky = db.relationship('Bezpecak', backref='pobocka', lazy='dynamic')
    zaznamy = db.relationship('Zaznam', backref='pobocka', lazy='dynamic')


class Uzivatel(db.Model):
    __tablename__ = "uzivatele"
    id = db.Column(db.Integer, primary_key=True)
    osobni_cislo = db.Column(db.Integer, unique=True, nullable=False)
    jmeno = db.Column(db.VARCHAR(255), nullable=False)
    _password = db.Column(db.VARCHAR(255), nullable=False)
    email = db.Column(db.VARCHAR(255), nullable=True)
    aktivni = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    vytvoren = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    zmenen = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now(), nullable=False)
    id_pobocka = db.Column(db.Integer, db.ForeignKey('pobocky.id'), nullable=False)
    zaznamy = db.relationship('Zaznam', backref='zaznam', lazy='dynamic')

    # def __init__(self, osobni_cislo, jmeno, plaintext_password, email, aktivni, admin, id_pobocka, _id=None):
    #     self.id = _id
    #     self.osobni_cislo = osobni_cislo
    #     self.jmeno = jmeno
    #     self.password = plaintext_password
    #     self.email = email
    #     self.aktivni = aktivni
    #     self.admin = admin
    #     self.id_pobocka = id_pobocka

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = generate_password_hash(plaintext)

    @hybrid_method
    def is_correct_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)


class Zaznam(db.Model):
    __tablename__ = "zaznamy"
    id = db.Column(db.BigInteger, primary_key=True)
    ean = db.Column(db.BigInteger, nullable=False)
    imei1 = db.Column(db.BigInteger, nullable=True)
    imei2 = db.Column(db.BigInteger, nullable=True)
    kusy = db.Column(db.Integer, nullable=False, server_default="1")
    id_uzivatele = db.Column(db.Integer, db.ForeignKey('uzivatele.id'), nullable=False)
    text = db.Column(db.Text, nullable=True)
    typ = db.Column(db.Text, nullable=False)
    faktura = db.Column(db.BigInteger, nullable=True)
    datum = db.Column(db.DateTime, server_default=func.now())
    id_pobocky = db.Column(db.Integer, db.ForeignKey('pobocky.id'), nullable=False)


class Bezpecak(db.Model):
    __tablename__ = "bezpecaky"
    id = db.Column(db.Integer, primary_key=True)
    id_pobocky = db.Column(db.Integer, db.ForeignKey('pobocky.id'), nullable=False)
    nazev = db.Column(db.VARCHAR(255), nullable=False)
    heslo = db.Column(db.VARCHAR(255), nullable=False)


def check_credentials(username: str, password: str):
    """
    validating credentials
    :param username:
    :param password:
    :return: access_token or False
    """
    if username == "user" and password == "pass":
        return create_access_token(identity=username)
    else:
        return False


@jwt.user_claims_loader
def add_claims_to_token(identity: object):
    """
    thanks to decorator this method is called before creating the token
    we can add some payload
    taking only one arg and returning serializable object
    """
    return {
        'user': identity
    }

