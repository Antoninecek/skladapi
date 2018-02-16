from skladapi.models import *
from skladapi.models import Uzivatel
from sqlalchemy.exc import IntegrityError


def vytvor_db(app):
    with app.app_context():
        db.drop_all()

        try:
            db.create_all()
        except Exception as ex:
            raise Exception("integrita modelu")

        try:
            pobocka = Pobocka(id=1, mesto="Domov")
            db.session.add(pobocka)
            db.session.commit()
        except Exception as ex:
            print("nemozno vlozit pobocku")
            raise ex

        try:
            admin = Uzivatel(osobni_cislo=0, jmeno="root", password="bagr",
                             email="a@a.cz", aktivni=1, admin=1, id_pobocka=1)
            db.session.add(admin)
            db.session.commit()
        except IntegrityError as ie:
            raise ie

    return True
