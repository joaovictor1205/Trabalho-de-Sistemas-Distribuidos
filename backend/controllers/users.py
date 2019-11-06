from passlib.hash import sha256_crypt
import os.path
import json
import jwt

USERS_PATH = 'archive/users.json'
SECRET = os.getenv('SECRET')


def register_user(request, context):
    user = {
        'username': request.username,
        'email': request.email,
        'user_type': request.user_type,
        'password': sha256_crypt.encrypt(request.password)
    }

    if os.path.exists(USERS_PATH):
        with open(USERS_PATH, 'r+') as json_file:
            users = json.load(json_file)

            for aux_user in users:
                if aux_user['username'] == user['username']:
                    return True, {'msg': 'User already exists'}, None

            users.append(user)
            json_file.seek(0)
            json.dump(users, json_file)
            json_file.truncate()

            token = jwt.encode({'username': user['username']}, SECRET, algorithm='HS256')
            return False, {'user': user, 'token': token}
    else:
        with open(USERS_PATH, 'w+') as json_file:
            users = [user]
            json.dump(users, json_file)

            token = jwt.encode({'username': user['username']}, SECRET, algorithm='HS256')
            return False, {'user': user, 'token': token}


def login_user(request, context):
    obj_user = {
        'username': request.username,
        'password': request.password
    }

    if not os.path.exists(USERS_PATH):
        return True, {'msg': 'User does not exist'}

    with open(USERS_PATH, 'r+') as json_file:
        users = json.load(json_file)

        user = None
        for aux_user in users:
            if aux_user['username'] == obj_user['username']:
                user = aux_user
                break

        if user is None:
            return True, {'msg': 'User does not exist'}

        if not sha256_crypt.verify(obj_user['password'], user['password']):
            return True, {'msg': 'User Invalid'}

        token = jwt.encode({'username': user['username']}, SECRET, algorithm='HS256')
        return False, {'user': user, 'token': token}
