from flask import render_template, request, redirect, jsonify
from app import app
from app.proto import API_pb2
from grpc import RpcError


@app.route('/matches')
def matches():
    from app import stub

    token = request.cookies.get('token')
    if not token:
        return redirect('/')
    username = request.cookies.get('username')

    pb_auth_request = API_pb2.AuthRequest()
    pb_auth_request.token = token
    pb_auth_request.username = username

    try:
        auth_response = stub.Authenticate(pb_auth_request)
    except RpcError as e:
        print(e)
        return redirect('/')

    user = {
        'username': auth_response.user.username,
        'email': auth_response.user.email,
        'user_type': auth_response.user.user_type
    }

    pb_user = API_pb2.User(username=auth_response.user.username, user_type=auth_response.user.user_type)
    try:
        matches = []
        for match in stub.GetMatches(pb_user):
            matches.append({
                'id': match.id,
                'recruiter': match.recruiter.username,
                'employee': match.employee.username,
                'employee_email': match.employee.email,
                'recruiter_match': match.recruiter_match,
                'employee_match': match.employee_match
            })
    except RpcError as e:
        print(e)
        return redirect('/')

    return render_template('matches.html', user=user, matches=matches)


@app.route('/offer_job', methods=['POST'])
def offer_job():
    from app import stub

    data = request.json
    pb_match = API_pb2.Match()
    pb_match.recruiter.username = data['recruiter']
    pb_match.recruiter.token = data['token']
    pb_match.employee.username = data['employee']

    try:
        match = stub.OfferJob(pb_match)
    except RpcError as e:
        print(e)
        return {'error': True}

    return jsonify({
        'id': match.id,
        'recruiter': match.recruiter.username,
        'employee': match.employee.username,
    })


@app.route('/accept_match', methods=['POST'])
def accept_match():
    from app import stub

    data = request.json
    pb_match = API_pb2.Match()
    pb_match.id = data['id']
    pb_match.recruiter.username = data['recruiter']
    pb_match.employee.token = data['token']
    pb_match.employee.username = data['employee']

    try:
        match = stub.AcceptMatch(pb_match)
    except RpcError as e:
        print(e)
        return {'error': True}

    return jsonify({
        'recruiter': match.recruiter.username,
        'employee': match.employee.username,
    })


@app.route('/reject_match', methods=['POST'])
def reject_match():
    from app import stub

    data = request.json
    pb_match = API_pb2.Match()
    pb_match.id = data['id']
    pb_match.recruiter.username = data['recruiter']
    pb_match.employee.token = data['token']
    pb_match.employee.username = data['employee']

    try:
        match = stub.RejectMatch(pb_match)
    except RpcError as e:
        print(e)
        return {'error': True}

    return jsonify({
        'recruiter': match.recruiter.username,
        'employee': match.employee.username,
    })

