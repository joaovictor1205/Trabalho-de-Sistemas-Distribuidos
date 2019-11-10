from flask import render_template, request, redirect, make_response
from app import app
from app.proto import API_pb2
from grpc import RpcError


@app.route('/')
def index():
    token = request.cookies.get('token')
    if token:
        return redirect('/chat')

    return render_template('home.html')


@app.route('/register', methods=['GET'])
def register():
    token = request.cookies.get('token')
    if token:
        return redirect('/chat')

    return render_template('register.html', error=False)


@app.route('/register', methods=['POST'])
def post_register():
    from app import stub

    data = request.form
    pb_user = API_pb2.User()
    pb_user.username = data['username']
    pb_user.email = data['email']
    pb_user.password = data['password']

    if int(data['user_type']) == 1:
        pb_user.user_type = API_pb2.USER_TYPE.EMPLOYEE
    else:
        pb_user.user_type = API_pb2.USER_TYPE.RECRUITER

    try:
        auth_response = stub.RegisterUser(pb_user)
    except RpcError as e:
        print(e)
        return render_template('register.html', error=True)

    resp = make_response(redirect('/chat'))
    resp.set_cookie('token', auth_response.user.token)
    resp.set_cookie('username', auth_response.user.username)
    return resp


@app.route('/login', methods=['GET'])
def login():
    token = request.cookies.get('token')
    if token:
        return redirect('/chat')

    return render_template('login.html', error=False)


@app.route('/login', methods=['POST'])
def post_login():
    from app import stub

    data = request.form
    pb_user = API_pb2.User()
    pb_user.username = data['username']
    pb_user.password = data['password']

    try:
        auth_response = stub.LoginUser(pb_user)
    except RpcError as e:
        print(e)
        return render_template('login.html', error=True)

    resp = make_response(redirect('/chat'))
    resp.set_cookie('token', auth_response.user.token)
    resp.set_cookie('username', auth_response.user.username)
    return resp
