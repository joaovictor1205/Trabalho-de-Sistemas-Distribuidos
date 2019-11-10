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


PORT = int(os.getenv('PORT'))
ID_SERVER = int(os.getenv('ID_SERVER'))
NUM_SERVERS = int(os.getenv('NUM_SERVERS'))


class APIServicer(API_pb2_grpc.APIServicer):
    def __init__(self):
        print('Initializating Consistent Hashing')

        self.CH = ConsistentHashing(NUM_SERVERS, PORT, {'id': ID_SERVER})
        self.LSMT = LogStructureMergeTree()

    def Authenticate(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.AuthResponse()

        key = self.CH.hash(request.username)
        print(f'Authenticate - Server {ID_SERVER} / Username {request.username} / Username key: {key}')

        pb_node = self.CH.find_successor(key)
        if pb_node.server_id != ID_SERVER:
            print(f'Authenticate - Redirected to server {pb_node.server_id}')
            try:
                with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.Authenticate(request)
            except Exception as e:
                print(e)
                return API_pb2.AuthResponse()
        print(f'Authenticate - Server {ID_SERVER} executing the action')

        error, data = authentication.authenticate(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.AuthResponse()
        else:
            pb_auth_response = API_pb2.AuthResponse()
            pb_auth_response.user.username = data['user']['username']
            pb_auth_response.user.user_type = data['user']['user_type']
            pb_auth_response.user.email = data['user']['email']

            for match in data['matches']:
                pb_match = pb_auth_response.matches.add()
                pb_match.recruiter.username = match['recruiter']
                pb_match.employee.username = match['employee']
                pb_match.employee.email = match['employee_email']
                pb_match.recruiter_match = match['recruiter_match']
                pb_match.employee_match = match['employee_match']

            return pb_auth_response

    def RegisterUser(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.AuthResponse()

        key = self.CH.hash(request.username)
        print(f'RegisterUser - Server {ID_SERVER} / Username {request.username} / Username key: {key}')

        pb_node = self.CH.find_successor(key)
        if pb_node.server_id != ID_SERVER:
            print(f'RegisterUser - Redirected to server {pb_node.server_id}')
            try:
                with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.RegisterUser(request)
            except Exception as e:
                print(e)
                return API_pb2.AuthResponse()
        print(f'RegisterUser - Server {ID_SERVER} executing the action')

        error, data = users.register_user(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.AuthResponse()
        else:
            pb_auth_response = API_pb2.AuthResponse()
            pb_auth_response.user.username = data['user']['username']
            pb_auth_response.user.user_type = data['user']['user_type']
            pb_auth_response.user.email = data['user']['email']
            pb_auth_response.user.token = data['token']
            return pb_auth_response

    def LoginUser(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.AuthResponse()

        key = self.CH.hash(request.username)
        print(f'LoginUser - Server {ID_SERVER} / Username {request.username} / Username key: {key}')

        pb_node = self.CH.find_successor(key)
        if pb_node.server_id != ID_SERVER:
            print(f'LoginUser - Redirected to server {pb_node.server_id}')
            try:
                with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.LoginUser(request)
            except Exception as e:
                print(e)
                return API_pb2.AuthResponse()
        print(f'LoginUser - Server {ID_SERVER} executing the action')

        error, data = users.login_user(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.AuthResponse()
        else:
            pb_auth_response = API_pb2.AuthResponse()
            pb_auth_response.user.username = data['user']['username']
            pb_auth_response.user.user_type = data['user']['user_type']
            pb_auth_response.user.email = data['user']['email']
            pb_auth_response.user.token = data['token']
            return pb_auth_response

    def GetMessages(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            yield API_pb2.Message()
        else:
            key = self.CH.hash(request.username)
            print(f'GetMessages - Server {ID_SERVER} / Username {request.username} / Username key: {key}')

            pb_node = self.CH.find_successor(key)
            if pb_node.server_id != ID_SERVER:
                print(f'GetMessages - Redirected to server {pb_node.server_id}')
                try:
                    with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                        stub = API_pb2_grpc.APIStub(channel)
                        for message in stub.GetMessages(request):
                            yield message
                except Exception as e:
                    print(e)
                    yield API_pb2.Message()
            else:
                print(f'GetMessages - Server {ID_SERVER} executing the action')

                error, data = messages.get_messages(request, context)
                for message in data['messages']:
                    pb_message = API_pb2.Message()
                    pb_message.message = message['message']
                    pb_message.user.username = message['username']
                    pb_message.user.user_type = message['user_type']
                    yield pb_message

    def SendMessage(self, request, context):
        """The messages need to be replicated across the chord"""

        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.Message()

        print(f'SendMessage - Server {ID_SERVER} / Username {request.user.username}')

        replicated_message = API_pb2.ReplicatedMessage()
        replicated_message.message.user.username = request.user.username
        replicated_message.message.user.user_type = request.user.user_type
        replicated_message.message.user.token = request.user.token
        replicated_message.message.message = request.message

        nodes = self.CH.get_reachable_nodes()
        for node in nodes:
            pb_node = replicated_message.nodes.add()
            pb_node.id = str(node['id'])
            pb_node.server_id = node['server_id']

        pb_node = replicated_message.nodes.add()
        pb_node.id = str(self.CH.id)
        pb_node.server_id = self.CH.server_id

        for node in nodes:
            try:
                with grpc.insecure_channel(f'nerd_room_backend{node["server_id"]}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    stub.ReplicateMessage(replicated_message)
            except Exception as e:
                print(e)
                continue

        error, data = messages.send_message(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Message()
        else:
            pb_message = API_pb2.Message()
            pb_message.user.username = data['message']['username']
            pb_message.user.user_type = data['message']['user_type']
            pb_message.message = data['message']['message']
            return pb_message

    def OfferJob(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.Match()

        key = self.CH.hash(request.employee.username)
        print(f'OfferJob - Server {ID_SERVER} / Username {request.employee.username} / Username key: {key}')

        pb_node = self.CH.find_successor(key)
        if pb_node.server_id != ID_SERVER:
            print(f'OfferJob - Redirected to server {pb_node.server_id}')
            try:
                with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.OfferJob(request)
            except Exception as e:
                print(e)
                return API_pb2.Match()
        print(f'OfferJob - Server {ID_SERVER} executing the action')

        error, data = matches.offer_job(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Match()
        else:
            pb_match = API_pb2.Match()
            pb_match.recruiter.username = data['match']['recruiter']
            pb_match.employee.username = data['match']['employee']
            return pb_match

    def GetMatches(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            yield API_pb2.Match()
        else:
            key = self.CH.hash(request.username)
            print(f'GetMatches - Server {ID_SERVER} / Username {request.username} / Username key: {key}')

            pb_node = self.CH.find_successor(key)
            if pb_node.server_id != ID_SERVER:
                print(f'GetMatches - Redirected to server {pb_node.server_id}')
                try:
                    with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                        stub = API_pb2_grpc.APIStub(channel)
                        for match in stub.GetMatches(request):
                            yield match
                except Exception as e:
                    print(e)
                    yield API_pb2.Match()
            else:
                print(f'GetMatches - Server {ID_SERVER} executing the action')

                error, data = matches.get_matches(request, context)
                for match in data['matches']:
                    pb_match = API_pb2.Match()
                    pb_match.recruiter.username = match['recruiter']
                    pb_match.employee.username = match['employee']
                    pb_match.recruiter_match = match['recruiter_match']
                    pb_match.employee_match = match['employee_match']
                    yield pb_match

    def AcceptMatch(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.Match()

        key = self.CH.hash(request.employee.username)
        print(f'AcceptMatch - Server {ID_SERVER} / Username {request.employee.username} / Username key: {key}')

        pb_node = self.CH.find_successor(key)
        if pb_node.server_id != ID_SERVER:
            print(f'AcceptMatch - Redirected to server {pb_node.server_id}')
            try:
                with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.AcceptMatch(request)
            except Exception as e:
                print(e)
                return API_pb2.Match()
        print(f'AcceptMatch - Server {ID_SERVER} executing the action')

        error, data = matches.accept_match(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Match()
        else:
            pb_match = API_pb2.Match()
            pb_match.recruiter.username = data['match']['recruiter']
            pb_match.employee.username = data['match']['employee']
            return pb_match

    def RejectMatch(self, request, context):
        if not self.CH.ready:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details({'msg': 'API not ready'})
            return API_pb2.Match()

        key = self.CH.hash(request.employee.username)
        print(f'RejectMatch - Server {ID_SERVER} / Username {request.employee.username} / Username key: {key}')

        pb_node = self.CH.find_successor(key)
        if pb_node.server_id != ID_SERVER:
            print(f'RejectMatch - Redirected to server {pb_node.server_id}')
            try:
                with grpc.insecure_channel(f'nerd_room_backend{pb_node.server_id}:{self.CH.default_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    return stub.RejectMatch(request)
            except Exception as e:
                print(e)
                return API_pb2.Match()
        print(f'RejectMatch - Server {ID_SERVER} executing the action')

        error, data = matches.reject_match(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Match()
        else:
            pb_match = API_pb2.Match()
            pb_match.recruiter.username = data['match']['recruiter']
            pb_match.employee.username = data['match']['employee']
            return pb_match

    def ReplicateMessage(self, request, context):
        print(f'ReplicateMessage - Server {ID_SERVER} executing the action')
        messages.send_message(request.message, context)

        replicated_message = request

        nodes = self.CH.get_reachable_nodes()
        for node in nodes:
            exists = next((x for x in replicated_message.nodes if x.id == str(node['id'])), None)
            if not exists:
                pb_node = replicated_message.nodes.add()
                pb_node.id = str(node['id'])
                pb_node.server_id = node['server_id']
                try:
                    with grpc.insecure_channel(f'nerd_room_backend{node["server_id"]}:{self.CH.default_port}') as channel:
                        stub = API_pb2_grpc.APIStub(channel)
                        stub.ReplicateMessage(replicated_message)
                except Exception as e:
                    print(e)
                    continue

        empty = API_pb2.Empty()
        return empty

    def FloodNode(self, request, context):
        return self.CH.flood(request)

    def FindSuccessor(self, request, context):
        return self.CH.find_successor(request.key)


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_servicer = APIServicer()
    API_pb2_grpc.add_APIServicer_to_server(api_servicer, server)

    print(f'Starting server: {ID_SERVER}. Listening on port 50051.')

    server.add_insecure_port('[::]:50051')
    server.start()

    print(f'Starting DHT')
    api_servicer.CH.initialize()

    # since server.start() will not block,
    # a sleep-loop is added to keep alive
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
