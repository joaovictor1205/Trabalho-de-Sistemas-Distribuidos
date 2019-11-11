from flask import render_template, request, redirect, jsonify
from app import app
from app.proto import API_pb2
from grpc import RpcError


@app.route('/send_message', methods=['POST'])
def send_message():
    from app import stub

    data = request.json
    pb_message = API_pb2.Message()
    pb_message.user.username = data['user']['username']
    pb_message.user.user_type = data['user']['user_type']
    pb_message.user.token = data['token']
    pb_message.message = data['message']

    try:
        message = stub.SendMessage(pb_message)
    except RpcError as e:
        print(e)
        return {'error': True}

    return jsonify({
        'id': message.id,
        'username': message.user.username,
        'user_type': message.user.user_type,
        'message': message.message
    })
