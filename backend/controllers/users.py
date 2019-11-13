from passlib.hash import sha256_crypt
import os.path
import uuid
import jwt

SECRET = os.getenv('SECRET')


def register_user(LSMT, request, context):
    user = {
        'id': str(uuid.uuid4()),
        'username': request.username,
        'email': request.email,
        'user_type': request.user_type,
        'password': sha256_crypt.encrypt(request.password),
        'type': 'users'
    }

    aux_user = LSMT.search({'type': 'users', 'username': user['username']})

    if aux_user:
        return True, {'msg': 'User already exists'}

    LSMT.create(user['id'], user)
    token = jwt.encode({'username': user['username']}, SECRET, algorithm='HS256')
    return False, {'user': user, 'token': token}


def login_user(LSMT, request, context):
    user = {
        'username': request.username,
        'password': request.password
    }

    aux_user = LSMT.search({'type': 'users', 'username': user['username']})

    if not aux_user:
        return True, {'msg': 'User does not exist'}

    if not sha256_crypt.verify(user['password'], aux_user['password']):
        return True, {'msg': 'User Invalid'}

    token = jwt.encode({'username': aux_user['username']}, SECRET, algorithm='HS256')
    return False, {'user': aux_user, 'token': token}
