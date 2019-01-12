from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect


from jira import JIRA, JIRAError
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework_jwt.settings import api_settings


from .models import *
from .serializers import *


# Rest API View
@api_view(['GET'])
def current_user(request):
    '''
    Determine the current user by their token, and return their data
    '''

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserAuthentication(APIView):
    '''
    Handle authentication with tokens
    '''

    permission_classes = (AllowAny,)

    def get_object(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def post(self, request, format=None):
        email = request.data['email']
        password = request.data['password']
        try:
            # Login with Jira Auth
            jac = JIRA(
                'https://agilecommandcentralgroup10.atlassian.net/',
                basic_auth=(email, password)
            )
            jac_username = jac.myself().get('displayName')
            user = self.get_object(email)
            if user is None:
                # Signup with ACC
                serializer = UserSerializerWithToken(data={
                    'email': email,
                    'username': jac_username,
                    'password': password
                })
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                token = generate_new_token(user)
                user_existed_data = {
                    'token': token,
                    'email': user.email,
                    'username': user.username
                }
                return Response(
                    user_existed_data,
                    status=status.HTTP_200_OK
                )
        except JIRAError as e:
            return Response(status=status.HTTP_408_REQUEST_TIMEOUT)


class SessionViewSet(viewsets.ModelViewSet):
    '''
    Set of Session views for listing, retrieving, creating, deleting sessions
    '''

    queryset = Session.objects.all()
    serializer_class = SessionSerializer


# def home(request):
#     '''
#     Return sessions and allow user create new sessions
#     '''

#     pass


# def session(request, session_name):
#     '''
#     Determine which session (channel) user belongs to
#     and emit messages to all users on the channel
#     '''

#     pass


# Utitlities
def my_jwt_response_handler(token, user=None, request=None):
    '''
        Return response includes token, email, username
    '''

    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


def generate_new_token(user):
    '''
        Return token for authenticated user
    '''
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token
