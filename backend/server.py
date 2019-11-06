from concurrent import futures
import grpc
import time

from proto import API_pb2
from proto import API_pb2_grpc

from controllers import authentication
from controllers import matches
from controllers import messages
from controllers import users


class APIServicer(API_pb2_grpc.APIServicer):
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
                pb_match.recruiter_match = match['recruiter_match']
                pb_match.employee_match = match['employee_match']

            return pb_auth_response

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

    def GetMessages(self, request, context):
        error, data = messages.get_messages(request, context)
        if error:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(data['msg'])
            return API_pb2.Message()
        else:
            for message in data['messages']:
                pb_message = API_pb2.Message()
                pb_message.message = message['message']
                pb_message.user.username = message['username']
                pb_message.user.user_type = message['user_type']
                yield pb_message

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

    def GetMatches(self, request, context):
        pass

    def AcceptMatch(self, request, context):
        pass

    def RejectMatch(self, request, context):
        pass


# Create gRPC Server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# Add the class into server
API_pb2_grpc.add_APIServicer_to_server(APIServicer(), server)

print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
