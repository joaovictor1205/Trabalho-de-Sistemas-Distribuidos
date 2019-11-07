import json
import jwt
import os

USERS_PATH = 'archive/users.json'
MATCHES_PATH = 'archive/matches.json'
SECRET = os.getenv('SECRET')


def authenticate(request, context):
    token = request.token

    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if not os.path.exists(USERS_PATH):
        return True, {'msg': 'Wrong Credentials'}

    user = None
    with open(USERS_PATH, 'r+') as json_file:
        users = json.load(json_file)

        for aux_user in users:
            if aux_user['username'] == username:
                user = aux_user

    if not user:
        return True, {'msg': 'Wrong Credentials'}

    matches = []
    if os.path.exists(MATCHES_PATH):
        with open(MATCHES_PATH, 'r+') as json_file:
            matches = json.load(json_file)
            matches = [{
                'recruiter': match['recruiter'],
                'employee': match['employee'],
                'employee_email': match['employee_email'],
                'recruiter_match': match['recruiter_match'],
                'employee_match': match['employee_match']
            } for match in matches if match['recruiter'] == username]

    return False, {'user': user, 'matches': matches}
