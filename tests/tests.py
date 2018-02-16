import unittest
from flask import request
from json import dumps, loads
from json.decoder import JSONDecodeError
from skladapi import app
from init_db import vytvor_db
import flask


def _create_db(self):
    vytvor_db(self.app)


def _make_request(self, url, token, method="get", params=None):
    with self.app.test_client() as c:
        if method.lower() == 'get':
            response = c.get(url, headers={'Content-Type': 'application/json',
                                           'Authorization': 'Bearer ' + token})
        elif method.lower() == 'post':
            response = c.post(url, headers={'Content-Type': 'application/json',
                                            'Authorization': 'Bearer ' + token}, data=params)
        else:
            return False
    try:
        resp = loads(response.get_data())
        if response.status_code == 200:
            return resp
        else:
            return False
    except JSONDecodeError:
        return False


def _get_jwt(self, username="user", password="pass"):
    with self.app.test_client() as c:
        response = c.post("/api/login", headers={'Content-Type': 'application/json'},
                          data=dumps({"username": username, "password": password}))
    try:
        resp = loads(response.get_data(as_text=True))
        if response.status_code == 200 and "access_token" in resp:
            return resp["access_token"]
        else:
            return False
    except JSONDecodeError:
        return False


class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app("testing")
        _create_db(self)

    def test_users_add(self):
        response = _make_request(self, '/api/users', _get_jwt(self), "POST", dumps({"user": "user",
                                                                                    "password": "pass",
                                                                                    "oscislo": "12",
                                                                                    "id_pobocka": "1"}))
        self.assertIn('id', response)


class TestJWT(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app("testing")

    def test_create_db(self):
        self.assertIs(vytvor_db(self.app), True)

    def test_check_user_password_from_db(self):
        _create_db(self)
        uzivatel_id = self._insert_user_to_db()
        with self.app.app_context():
            from skladapi.models import Uzivatel
            uziv = Uzivatel.query.filter_by(jmeno="test user").first()
            uziv.is_correct_password("test")

    def test_insert_user_to_db(self):
        _create_db(self)
        uzivatel_id = self._insert_user_to_db()
        with self.app.app_context():
            from skladapi.models import Uzivatel
            uziv = Uzivatel.query.filter_by(jmeno="test user").first()
            self.assertEqual(uziv.id, uzivatel_id)

    def _insert_user_to_db(self):
        with self.app.app_context():
            from skladapi.app import db
            from skladapi.models import Uzivatel
            uzivatel = Uzivatel(osobni_cislo=1, jmeno="test user", password="test", id_pobocka=1)
            db.session.add(uzivatel)
            db.session.commit()
            return uzivatel.id

    def test_get_jwt_wrong_credentials(self):
        self.assertIs(_get_jwt(self, "test", "test"), False)

    def test_get_jwt_right_credentials(self):
        response = _get_jwt(self, "user", "pass")
        self.assertIsNot(response, False)

    def test_get_access_to_protected_method(self):
        token = _get_jwt(self, "user", "pass")
        res = _make_request(self, "/api/time", token)
        assert res


if __name__ == '__main__':
    unittest.main()
