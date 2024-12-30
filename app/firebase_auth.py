import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('/firebase-key.json')
firebase_admin.initialize_app(cred)

def verify_token(token):
    """
    Verify Firebase ID token and return the user ID (uid).
    Raise an exception if the token is invalid.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        return None