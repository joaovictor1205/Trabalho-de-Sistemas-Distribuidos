import json
import jwt
import os

USERS_PATH = 'archive/users.json'
MATCHES_PATH = 'archive/matches.json'
SECRET = os.getenv('SECRET')


def offer_job(request, context):
    token = request.recruiter.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.recruiter.username:
        return True, {'msg': 'Wrong Credentials'}

    employee_email = ''
    if os.path.exists(USERS_PATH):
        with open(USERS_PATH, 'r+') as json_file:
            users = json.load(json_file)
            for aux_user in users:
                if aux_user['username'] == request.employee.username:
                    employee_email = aux_user['email']

    match = {
        'recruiter': request.recruiter.username,
        'employee': request.employee.username,
        'employee_email': employee_email,
        'recruiter_match': True,
        'employee_match': None,
    }

    if os.path.exists(MATCHES_PATH):
        with open(MATCHES_PATH, 'r+') as json_file:
            matches = json.load(json_file)
            matches.append(match)

            json_file.seek(0)
            json.dump(matches, json_file)
            json_file.truncate()

            return False, {'match': match}
    else:
        with open(MATCHES_PATH, 'w+') as json_file:
            matches = [match]
            json.dump(matches, json_file)

            return False, {'match': match}
