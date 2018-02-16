from flask_jwt_extended import (JWTManager, create_access_token,
                                jwt_required, get_jwt_identity, get_jwt_claims)
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash

jwt = JWTManager()
fbcrypt = Bcrypt()



