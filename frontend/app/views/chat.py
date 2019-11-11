from flask import render_template, request, redirect
from app import app
from app.proto import API_pb2
from grpc import RpcError


@app.route('/chat')
def chat():
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
        'id': auth_response.user.id,
        'username': auth_response.user.username,
        'email': auth_response.user.email,
        'user_type': auth_response.user.user_type
    }

    matches = [{
        'id': match.id,
        'recruiter': match.recruiter.username,
        'employee': match.employee.username,
        'recruiter_match': match.recruiter_match,
        'employee_match': match.employee_match
    } for match in auth_response.matches]

    pb_user = API_pb2.User(username=auth_response.user.username, user_type=auth_response.user.user_type)

    try:
        old_messages = []
        for message in stub.GetMessages(pb_user):
            old_messages.append({
                'message': message.message,
                'user': {
                    'username': message.user.username,
                    'user_type': message.user.user_type
                }
            })
    except RpcError as e:
        print(e)
        return redirect('/')

    return render_template('chat.html', user=user, matches=matches, old_messages=old_messages)
