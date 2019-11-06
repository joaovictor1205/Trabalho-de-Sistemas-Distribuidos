import json
import jwt
import os

USERS_PATH = 'archive/users.json'
MESSAGES_PATH = 'archive/messages.json'
SECRET = os.getenv('SECRET')


def send_message(request, context):
    token = request.user.token
    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    username = decoded['username']

    if username != request.user.username:
        return True, {'msg': 'Wrong Credentials'}

    message = {
        'username': request.user.username,
        'user_type': request.user.user_type,
        'message': request.message
    }

    if os.path.exists(MESSAGES_PATH):
        with open(MESSAGES_PATH, 'r+') as json_file:
            messages = json.load(json_file)
            messages.append(message)

            json_file.seek(0)
            json.dump(messages, json_file)
            json_file.truncate()

            return False, {'message': message}
    else:
        with open(MESSAGES_PATH, 'w+') as json_file:
            messages = [message]
            json.dump(messages, json_file)

            return False, {'message': message}


def get_messages(request, context):
    if os.path.exists(MESSAGES_PATH):
        with open(MESSAGES_PATH, 'r+') as json_file:
            messages = json.load(json_file)
            return False, {'messages': messages}
    else:
        return False, {'messages': []}
