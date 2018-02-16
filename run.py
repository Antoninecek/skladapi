from skladapi.app import create_app

app = create_app("development")
"""
vytvoreni db
from init_db import vytvor_db
vytvor_db(app)
"""
app.run()
