from proto import API_pb2
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
        'recruiter_match': 1,
        'employee_match': -1,
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


def get_matches(request, context):
    matches = []

    if os.path.exists(MATCHES_PATH):
        with open(MATCHES_PATH, 'r+') as json_file:
            matches = json.load(json_file)

            if request.user_type == API_pb2.USER_TYPE.EMPLOYEE:
                matches = [{
                    'recruiter': match['recruiter'],
                    'employee': match['employee'],
                    'employee_email': match['employee_email'],
                    'recruiter_match': match['recruiter_match'],
                    'employee_match': match['employee_match']
                } for match in matches if match['employee'] == request.username]
            elif request.user_type == API_pb2.USER_TYPE.RECRUITER:
                matches = [{
                    'recruiter': match['recruiter'],
                    'employee': match['employee'],
                    'employee_email': match['employee_email'],
                    'recruiter_match': match['recruiter_match'],
                    'employee_match': match['employee_match']
                } for match in matches if match['recruiter'] == request.username]

    return False, {'matches': matches}


def accept_match(request, context):
    token = request.employee.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.employee.username:
        return True, {'msg': 'Wrong Credentials'}

    if os.path.exists(MATCHES_PATH):
        with open(MATCHES_PATH, 'r+') as json_file:
            matches = json.load(json_file)

            for i in range(len(matches)):
                if matches[i]['employee'] == request.employee.username and \
                   matches[i]['recruiter'] == request.recruiter.username:
                    matches[i]['employee_match'] = 1

                    json_file.seek(0)
                    json.dump(matches, json_file)
                    json_file.truncate()

                    return False, {
                        'recruiter': matches[i]['recruiter'],
                        'employee': matches[i]['employee'],
                    }

            return True, {'msg': 'Match Does Not Exist'}
    else:
        return True, {'msg': 'Match Does Not Exist'}


def reject_match(request, context):
    token = request.employee.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.employee.username:
        return True, {'msg': 'Wrong Credentials'}

    if os.path.exists(MATCHES_PATH):
        with open(MATCHES_PATH, 'r+') as json_file:
            matches = json.load(json_file)

            for i in range(len(matches)):
                if matches[i]['employee'] == request.employee.username and \
                        matches[i]['recruiter'] == request.recruiter.username:
                    matches[i]['employee_match'] = 0

                    json_file.seek(0)
                    json.dump(matches, json_file)
                    json_file.truncate()

                    return False, {
                        'recruiter': matches[i]['recruiter'],
                        'employee': matches[i]['employee'],
                    }

            return True, {'msg': 'Match Does Not Exist'}
    else:
        return True, {'msg': 'Match Does Not Exist'}
