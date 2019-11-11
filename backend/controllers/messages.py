import uuid
import jwt
import os

USERS_PATH = 'archive/users.json'
MESSAGES_PATH = 'archive/messages.json'
SECRET = os.getenv('SECRET')


def send_message(LSMT, request, context):
    token = request.user.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.user.username:
        return True, {'msg': 'Wrong Credentials'}

    message = {
        'id': str(uuid.uuid4()),
        'username': request.user.username,
        'user_type': request.user.user_type,
        'message': request.message,
        'type': 'messages'
    }

    LSMT.create(message['id'], message)
    return False, {'message': message}


def get_messages(LSMT, request, context):
    messages = LSMT.search_multiple({'type': 'messages'})
    return False, {'messages': messages}
