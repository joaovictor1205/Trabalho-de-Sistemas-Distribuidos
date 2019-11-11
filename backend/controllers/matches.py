from proto import API_pb2
import uuid
import json
import jwt
import os

USERS_PATH = 'archive/users.json'
MATCHES_PATH = 'archive/matches.json'
SECRET = os.getenv('SECRET')


def offer_job(LSMT, request, context):
    token = request.recruiter.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.recruiter.username:
        return True, {'msg': 'Wrong Credentials'}

    employee_email = ''
    employee = LSMT.search({'type': 'users', 'username': request.employee.username})
    if employee:
        employee_email = employee['email']

    match = {
        'id': str(uuid.uuid4()),
        'recruiter': request.recruiter.username,
        'employee': request.employee.username,
        'employee_email': employee_email,
        'recruiter_match': 1,
        'employee_match': -1,
        'type': 'matches'
    }

    LSMT.create(match['id'], match)
    return False, {'match': match}


def get_matches(LSMT, request, context):
    matches = []

    if request.user_type == API_pb2.USER_TYPE.EMPLOYEE:
        matches = LSMT.search_multiple({'type': 'matches', 'employee': request.username})
    elif request.user_type == API_pb2.USER_TYPE.RECRUITER:
        matches = LSMT.search_multiple({'type': 'matches', 'recruiter': request.username})

    return False, {'matches': matches}


def accept_match(LSMT, request, context):
    token = request.employee.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.employee.username:
        return True, {'msg': 'Wrong Credentials'}

    match = LSMT.search({
        'type': 'matches',
        'employee': request.employee.username,
        'recruiter': request.recruiter.username
    })

    match['employee_match'] = 1
    LSMT.create(match['id'], match)

    return False, {'match': match}


def reject_match(LSMT, request, context):
    token = request.employee.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.employee.username:
        return True, {'msg': 'Wrong Credentials'}

    match = LSMT.search({
        'type': 'matches',
        'employee': request.employee.username,
        'recruiter': request.recruiter.username
    })

    match['employee_match'] = 0
    LSMT.create(match['id'], match)

    return False, {'match': match}
