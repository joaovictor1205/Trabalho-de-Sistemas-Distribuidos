import jwt
import os

SECRET = os.getenv('SECRET')


def authenticate(LSMT, request, context):
    token = request.token

    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    user = LSMT.search({'type': 'users', 'username': username})

    if not user:
        return True, {'msg': 'Wrong Credentials'}

    matches = LSMT.search_multiple({'type': 'matches', 'recruiter': username})

    return False, {'user': user, 'matches': matches}
