from concurrent import futures
import grpc
import time
import os

from proto import API_pb2
from proto import API_pb2_grpc

from controllers import authentication
from controllers import matches
from controllers import messages
from controllers import users
from helpers.consistent_hashing import ConsistentHashing
from helpers.log_structure_merge_tree import LogStructureMergeTree


HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
SERVER_ID = int(os.getenv('SERVER_ID'))
CONNECT_HOST = os.getenv('CONNECT_HOST')
CONNECT_PORT = int(os.getenv('CONNECT_PORT'))


class APIServicer(API_pb2_grpc.APIServicer):
    def __init__(self):
        print('Initializating Consistent Hashing')

        self.CH = ConsistentHashing({
            'server_id': SERVER_ID,
            'host': HOST,
            'port': PORT,
            'connect_host': CONNECT_HOST,
            'connect_port': CONNECT_PORT
        })
        self.LSMT = LogStructureMergeTree()

    def Authenticate(self, request, context):
        key = self.CH.hash(request.username)
        print(f'Authenticate - Server {SERVER_ID} / Username {request.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'Authenticate - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.Authenticate(request)
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Wrong Credentials')
                return API_pb2.AuthResponse()
        print(f'Authenticate - Server {SERVER_ID} executing the action')

        error, data = authentication.authenticate(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.AuthResponse()
        else:
            pb_auth_response = API_pb2.AuthResponse()
            pb_auth_response.user.id = data['user']['id']
            pb_auth_response.user.username = data['user']['username']
            pb_auth_response.user.user_type = data['user']['user_type']
            pb_auth_response.user.email = data['user']['email']

            for match in data['matches']:
                pb_match = pb_auth_response.matches.add()
                pb_match.id = match['id']
                pb_match.recruiter.username = match['recruiter']
                pb_match.employee.username = match['employee']
                pb_match.employee.email = match['employee_email']
                pb_match.recruiter_match = match['recruiter_match']
                pb_match.employee_match = match['employee_match']

            return pb_auth_response

    def RegisterUser(self, request, context):
        key = self.CH.hash(request.username)
        print(f'RegisterUser - Server {SERVER_ID} / Username {request.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'RegisterUser - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.RegisterUser(request)
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('User Already exists')
                return API_pb2.AuthResponse()
        print(f'RegisterUser - Server {SERVER_ID} executing the action')

        error, data = users.register_user(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.AuthResponse()
        else:
            pb_auth_response = API_pb2.AuthResponse()
            pb_auth_response.user.id = data['user']['id']
            pb_auth_response.user.username = data['user']['username']
            pb_auth_response.user.user_type = data['user']['user_type']
            pb_auth_response.user.email = data['user']['email']
            pb_auth_response.user.token = data['token']
            return pb_auth_response

    def LoginUser(self, request, context):
        key = self.CH.hash(request.username)
        print(f'LoginUser - Server {SERVER_ID} / Username {request.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'LoginUser - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.LoginUser(request)
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid User')
                return API_pb2.AuthResponse()
        print(f'LoginUser - Server {SERVER_ID} executing the action')

        error, data = users.login_user(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.AuthResponse()
        else:
            pb_auth_response = API_pb2.AuthResponse()
            pb_auth_response.user.id = data['user']['id']
            pb_auth_response.user.username = data['user']['username']
            pb_auth_response.user.user_type = data['user']['user_type']
            pb_auth_response.user.email = data['user']['email']
            pb_auth_response.user.token = data['token']
            return pb_auth_response

    def GetMessages(self, request, context):
        key = self.CH.hash(request.username)
        print(f'GetMessages - Server {SERVER_ID} / Username {request.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'GetMessages - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    for message in stub.GetMessages(request):
                        yield message
            except Exception as e:
                print(e)
                yield API_pb2.Message()
        else:
            print(f'GetMessages - Server {SERVER_ID} executing the action')

            error, data = messages.get_messages(self.LSMT, request, context)
            for message in data['messages']:
                pb_message = API_pb2.Message()
                pb_message.id = message['id']
                pb_message.message = message['message']
                pb_message.user.username = message['username']
                pb_message.user.user_type = message['user_type']
                yield pb_message

    def SendMessage(self, request, context):
        """The messages need to be replicated across the chord"""
        print(f'SendMessage - Server {SERVER_ID} / Username {request.user.username}')

        replicated_message = API_pb2.ReplicatedMessage()
        replicated_message.message.user.username = request.user.username
        replicated_message.message.user.user_type = request.user.user_type
        replicated_message.message.user.token = request.user.token
        replicated_message.message.message = request.message

        nodes = self.CH.get_reachable_nodes()
        for node in nodes:
            pb_node = replicated_message.nodes.add()
            pb_node.id = str(node.id)
            pb_node.server_id = node.server_id

        pb_node = replicated_message.nodes.add()
        pb_node.id = str(self.CH.node.id)
        pb_node.server_id = self.CH.node.server_id

        for node in nodes:
            if node.server_id == SERVER_ID:
                continue

            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    stub.ReplicateMessage(replicated_message)
            except Exception as e:
                print(e)
                continue

        error, data = messages.send_message(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Message()
        else:
            pb_message = API_pb2.Message()
            pb_message.id = data['message']['id']
            pb_message.user.username = data['message']['username']
            pb_message.user.user_type = data['message']['user_type']
            pb_message.message = data['message']['message']
            return pb_message

    def ReplicateMessage(self, request, context):
        print(f'ReplicateMessage - Server {SERVER_ID} executing the action')
        messages.send_message(self.LSMT, request.message, context)

        replicated_message = request

        nodes = self.CH.get_reachable_nodes()
        for node in nodes:
            exists = next((x for x in replicated_message.nodes if x.id == str(node.id)), None)
            if not exists:
                pb_node = replicated_message.nodes.add()
                pb_node.id = str(node.id)
                pb_node.server_id = node.server_id
                try:
                    with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                        stub = API_pb2_grpc.APIStub(channel)
                        stub.ReplicateMessage(replicated_message)
                except Exception as e:
                    print(e)
                    continue

        empty = API_pb2.Empty()
        return empty

    def OfferJob(self, request, context):
        key = self.CH.hash(request.employee.username)
        print(f'OfferJob - Employee Server {SERVER_ID} / Username {request.employee.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'OfferJob - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.OfferJob(request)
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Wrong Credentials')
                return API_pb2.Match()

        key = self.CH.hash(request.recruiter.username)
        print(f'OfferJob - Recruiter Server {SERVER_ID} / Username {request.recruiter.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'OfferJob - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    stub.ReplicateOfferJob(request)
            except Exception as e:
                print(e)

        print(f'OfferJob - Server {SERVER_ID} executing the action')

        error, data = matches.offer_job(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Match()
        else:
            pb_match = API_pb2.Match()
            pb_match.id = data['match']['id']
            pb_match.recruiter.username = data['match']['recruiter']
            pb_match.employee.username = data['match']['employee']
            return pb_match

    def ReplicateOfferJob(self, request, context):
        key = self.CH.hash(request.recruiter.username)
        print(f'ReplicateOfferJob - Recruiter Server {SERVER_ID} / Username {request.recruiter.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'ReplicateOfferJob - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.ReplicateOfferJob(request)
            except Exception as e:
                print(e)
        else:
            print(f'ReplicateOfferJob - Server {SERVER_ID} executing the action')
            empty = API_pb2.Empty()
            matches.offer_job(self.LSMT, request, context)
            return empty

    def GetMatches(self, request, context):
        key = self.CH.hash(request.username)
        print(f'GetMatches - Server {SERVER_ID} / Username {request.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'GetMatches - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    for match in stub.GetMatches(request):
                        yield match
            except Exception as e:
                print(e)
                yield API_pb2.Match()
        else:
            print(f'GetMatches - Server {SERVER_ID} executing the action')

            error, data = matches.get_matches(self.LSMT, request, context)
            for match in data['matches']:
                pb_match = API_pb2.Match()
                pb_match.id = match['id']
                pb_match.recruiter.username = match['recruiter']
                pb_match.employee.username = match['employee']
                pb_match.recruiter_match = match['recruiter_match']
                pb_match.employee_match = match['employee_match']
                yield pb_match

    def AcceptMatch(self, request, context):
        key = self.CH.hash(request.employee.username)
        print(f'AcceptMatch - Employee Server {SERVER_ID} / Username {request.employee.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'AcceptMatch - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.AcceptMatch(request)
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Wrong Credentials')
                return API_pb2.Match()

        key = self.CH.hash(request.recruiter.username)
        print(f'AcceptMatch - Recruiter Server {SERVER_ID} / Username {request.recruiter.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'AcceptMatch - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    stub.ReplicateAcceptMatch(request)
            except Exception as e:
                print(e)

        print(f'AcceptMatch - Server {SERVER_ID} executing the action')

        error, data = matches.accept_match(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Match()
        else:
            pb_match = API_pb2.Match()
            pb_match.id = data['match']['id']
            pb_match.recruiter.username = data['match']['recruiter']
            pb_match.employee.username = data['match']['employee']
            return pb_match

    def ReplicateAcceptMatch(self, request, context):
        key = self.CH.hash(request.recruiter.username)
        print(f'ReplicateAcceptMatch - Recruiter Server {SERVER_ID} / Username {request.recruiter.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'ReplicateAcceptMatch - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.ReplicateAcceptMatch(request)
            except Exception as e:
                print(e)
        else:
            print(f'ReplicateOfferJob - Server {SERVER_ID} executing the action')
            empty = API_pb2.Empty()
            matches.accept_match(self.LSMT, request, context)
            return empty

    def RejectMatch(self, request, context):
        key = self.CH.hash(request.employee.username)
        print(f'RejectMatch - Employee Server {SERVER_ID} / Username {request.employee.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'RejectMatch - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.RejectMatch(request)
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Wrong Credentials')
                return API_pb2.Match()

        key = self.CH.hash(request.recruiter.username)
        print(f'RejectMatch - Recruiter Server {SERVER_ID} / Username {request.recruiter.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'RejectMatch - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    stub.ReplicateRejectMatch(request)
            except Exception as e:
                print(e)

        print(f'RejectMatch - Server {SERVER_ID} executing the action')

        error, data = matches.reject_match(self.LSMT, request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Match()
        else:
            pb_match = API_pb2.Match()
            pb_match.id = data['match']['id']
            pb_match.recruiter.username = data['match']['recruiter']
            pb_match.employee.username = data['match']['employee']
            return pb_match

    def ReplicateRejectMatch(self, request, context):
        key = self.CH.hash(request.recruiter.username)
        print(f'ReplicateRejectMatch - Recruiter Server {SERVER_ID} / Username {request.recruiter.username} / Username key: {key}')

        node = self.CH.find_successor(key)
        if node.server_id != SERVER_ID:
            print(f'ReplicateRejectMatch - Redirected to server {node.server_id}')
            try:
                with grpc.insecure_channel(f'{node.host}:{node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.ReplicateRejectMatch(request)
            except Exception as e:
                print(e)
        else:
            print(f'ReplicateRejectMatch - Server {SERVER_ID} executing the action')
            empty = API_pb2.Empty()
            matches.reject_match(self.LSMT, request, context)
            return empty

    def FindSuccessor(self, request, context):
        node = self.CH.find_successor(request.key)
        pb_node = node.to_pb()
        return pb_node

    def Notify(self, request, context):
        self.CH.notify(request)
        return API_pb2.Empty()

    def GetPredecessor(self, request, context):
        node = self.CH.get_predecessor()
        pb_node = node.to_pb()
        return pb_node


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_servicer = APIServicer()
    API_pb2_grpc.add_APIServicer_to_server(api_servicer, server)

    print(f'Starting server: {SERVER_ID}. Listening on port 50051.')

    server.add_insecure_port('[::]:50051')
    server.start()

    # since server.start() will not block,
    # a sleep-loop is added to keep alive
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
