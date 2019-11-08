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
from consistent_hashing import ConsistentHashing

ID_SERVER = int(os.getenv('ID_SERVER'))
INITIAL_PORT = int(os.getenv('INITIAL_PORT'))
NUM_SERVERS = int(os.getenv('NUM_SERVERS'))

def check_server(func):
    def decorator(*args, **kwargs):
        # Before request handlers
        print('Before request')

        rtn = func(*args, **kwargs)

        # After request handlers
        print('After request')

        return rtn
    return decorator


class APIServicer(API_pb2_grpc.APIServicer):
    @check_server
    def Authenticate(self, request, context):
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

    @check_server
    def RegisterUser(self, request, context):
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

    @check_server
    def LoginUser(self, request, context):
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

    @check_server
    def GetMessages(self, request, context):
        error, data = messages.get_messages(request, context)
        for message in data['messages']:
            pb_message = API_pb2.Message()
            pb_message.message = message['message']
            pb_message.user.username = message['username']
            pb_message.user.user_type = message['user_type']
            yield pb_message

    @check_server
    def SendMessage(self, request, context):
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

    @check_server
    def OfferJob(self, request, context):
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

    @check_server
    def GetMatches(self, request, context):
        error, data = matches.get_matches(request, context)
        for match in data['matches']:
            pb_match = API_pb2.Match()
            pb_match.recruiter.username = match['recruiter']
            pb_match.employee.username = match['employee']
            pb_match.recruiter_match = match['recruiter_match']
            pb_match.employee_match = match['employee_match']
            yield pb_match

    @check_server
    def AcceptMatch(self, request, context):
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

    @check_server
    def RejectMatch(self, request, context):
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


if __name__ == '__main__':
    print('Initializating Consistent Hashing')

    servers = [{
        'id': i,
        'port': INITIAL_PORT + i
    } for i in range(NUM_SERVERS)]

    CH = ConsistentHashing(servers)
    print(CH.nodes)
    print(len(CH.ring))
    print(CH.peers_per_node)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    API_pb2_grpc.add_APIServicer_to_server(APIServicer(), server)

    print(f'Starting server: {ID_SERVER}. Listening on port 50051.')

    server.add_insecure_port('[::]:50051')
    server.start()

    # since server.start() will not block,
    # a sleep-loop is added to keep alive
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
