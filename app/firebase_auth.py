import firebase_admin
from firebase_admin import credentials, auth

from app.models import User
from . import db

cred = credentials.Certificate("/firebase-key.json")
firebase_admin.initialize_app(cred)


def verify_token(token):
    """
    Verify Firebase ID token and return the user ID.
    If no user exists in the database, create a new one.
    Raise an exception if the token is invalid.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")
        name = decoded_token.get("name", None)

        if not email:
            print("Missing email in Firebase token")
            return None

        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            user = User(firebase_uid=firebase_uid, email=email, name=name)
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                print(f"Error creating user: {e}")
                return None

        return user.id
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
