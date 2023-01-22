from django.shortcuts import render
from rest_framework import generics, status
from ..serializers.auth_serializers import SignInSerializer, SignOutSerializer, SignUpSerializer #,ForgotPasswordSerializer
from ..models import Listing, User, Notification, Attachment, Session, ResetPassword
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.http import JsonResponse
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
# from ...backend_v3.settings import BASE_DIR

import os
# SESSION_KEY = os.getenv('SESSION_KEY')

class SignIn(APIView):
    serializer_class = SignInSerializer

    def post(self, request, format=None):

        # Get the request data (login details)
        serializer = self.serializer_class(data=request.data)
        print(serializer)
        if serializer.is_valid(): # check if data in our post request is valid
            username = serializer.data.get('username')
            given_password = serializer.data.get('password')

            users_queryset = User.objects.filter(username=username)
            if users_queryset.exists():
                user = users_queryset[0]
                if user.password != given_password:
                    print('first')
                    return Response({'msg': 'Incorrect login details given.'}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Successful sign in!

                # print('Token:', SESSION_KEY)
                
                # Create session if it doesn't exist already
                if not self.request.session.exists(self.request.session.session_key):
                    self.request.session.create()
                    old_session = Session.objects.filter(username=username)
                    if old_session.exists():
                        old_session[0].delete()

                # Create new session (awkward way to do it)
                print(self.request.session.session_key)
                print(len(self.request.session.session_key))
                new_session = Session(key=self.request.session.session_key, username=username)
                new_session.save()

                # request.session['username'] = username

                return Response({
                                'user': {
                                    'avatar': '',
                                    'username': username,
                                    'email': user.email,
                                    'authority': user.profile.authorisations,
                                },
                                'token': self.request.session.session_key, # SESSION_KEY
                                }, status=status.HTTP_200_OK) # Send the notification details to frontend
            else:
                print('second', username)
                return Response({'msg': 'User name not found in database.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            print('didnt pass serializer')
            return Response({'msg': 'Login request not valid.'}, status=status.HTTP_401_UNAUTHORIZED)
         

class SignOut(APIView):
    serializer_class = SignOutSerializer

    def post(self, request, format=None):

        # Get the request data (logout details)
        serializer = self.serializer_class(data=request.data)
        print(serializer, request.data)
        if serializer.is_valid(): # check if data in our post request is valid

            # Successful sign out!
            
            # Delete session if it exists
            if self.request.session.exists(self.request.session.session_key):
                del self.request.session

            print('Session deleted')
            key = request.headers['Authorization'].split(' ')[1]
            Session.objects.filter(key=key).delete()

            return Response(status=status.HTTP_200_OK) # Send the logout details to frontend
        else:
            print('Sign Out didnt pass serializer')
            return Response({'Bad Request': 'Logout request not valid.'}, status=status.HTTP_400_BAD_REQUEST)
         

class SignUp(APIView):
    serializer_class = SignUpSerializer

    def post(self, request, format=None):

        # Get the request data (logout details)
        serializer = self.serializer_class(data=request.data)
        print(serializer)
        if serializer.is_valid(): # check if data in our post request is valid

            username = serializer.data.get('username')
            given_password = serializer.data.get('password')
            given_email = serializer.data.get('email')

            users_queryset = User.objects.filter(username=username)
            if users_queryset.exists():
                errors = [{'message': '', 'domain': "global", 'reason': "invalid"}]
                packet = errors, {'message': 'User already exists!'}
                print('USer already exists')
                return Response(json.dumps(packet), status=status.HTTP_400_BAD_REQUEST)
            
            email_queryset = User.objects.filter(email=given_email)
            if email_queryset.exists():
                errors = [{'message': '', 'domain': "global", 'reason': "invalid"}]
                packet = errors, {'message': 'Email already in use!'}
                print('Email already exists')
                print(json.dumps(packet))
                return Response(json.dumps(packet), status=status.HTTP_400_BAD_REQUEST)

            new_user = User(username=username,
                            password=given_password,
                            email = given_email,
                            )
            new_user.save()
            new_user.profile.authorisations = ['user'],
            new_user.profile.authorised_listings_leads = [],
            new_user.profile.authorised_listings_contacted = [],
            new_user.profile.authorised_listings_booked = [],
            # new_user.set_cities()

            packet = {
                'username': username,
                'avatar': 'null',
                'authority': new_user.profile.authorisations,
                'email': given_email,
            }

            packet = {
                'user': packet,
                'token': self.request.session.session_key,
            }
            packet = json.dumps(packet)

            return Response(packet, status=status.HTTP_200_OK) # Send the logout details to frontend
        else:
            print('Sign Up didnt pass serializer')
            return Response({'Bad Request': 'Logout request not valid.'}, status=status.HTTP_400_BAD_REQUEST)
         

class ForgotPassword(APIView):
    # serializer_class = ForgotPasswordSerializer
    # lookup_url_kwarg = 'code' # when we call this instance, we need to give a keyword arguement

    # Define a get request: frontend asks for stuff
    def post(self, request, format=None):

        # NOTE: no auth
        # print(request.data)
        # serializer = self.serializer_class(data=request.data)
        # print(serializer)
        # if serializer.is_valid(): # check if data in our post request is valid (should just be email)

            # email = serializer.data.get('email')
            email = request.data['email']
            user_set = User.objects.filter(email=email)

            if user_set.exists():
                user = user_set[0]

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # # If token has already been used
                # if ResetPassword.objects.filter(token=token, uid=uid).exists():
                #     # return Response({'msg': 'Error: stale request.'}, status=status.HTTP_400_BAD_REQUEST)
                # # ResetPassword.objects.create(token=token, uid=uid)
                #     pass
                ResetPassword.objects.create(token=token, uid=uid, user=user)
                # r.save()
 
                # SEND EMAIL WITH VERIFICATION CODE
                # r = ResetPassword(user=user, email=email)

                subject = "Password Reset Requested"
                email_template_name = "email_templates/password_reset_email.txt"
                c = {
                "email":user.email,
                'domain':'127.0.0.1:3000', 
                'site_name': 'Website',
                "uid": uid,
                "user": user,
                'token': token,
                'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:  
                    send_mail(subject, email, 'oscar@sav-estates.co.uk' , [user.email], fail_silently=False)
                    return Response(status=status.HTTP_200_OK)
                except BadHeaderError:
                    print('What')
                    return Response({'msg':'Invalid header found.'}, status=status.HTTP_400_BAD_REQUEST)

                # return Response({'msg': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)
            # print('OOh rah')
            # All is well, don't let hackers know email isn't vlaid
            return Response(status=status.HTTP_200_OK)
        # return Response({'msg': 'Session data not valid.'}, status=status.HTTP_401_UNAUTHORIZED)

class ResetPasswordView(APIView):
    # serializer_class = PasswordSerializer
    # lookup_url_kwarg = 'code' # when we call this instance, we need to give a keyword arguement

    # Define a get request: frontend asks for stuff
    def post(self, request, format=None):

        print(request.data)
        uid = request.data['uid']
        token = request.data['token']
        new_password = request.data['password'] 

        # NOTE: need to check it's valid password, although I guess done in model field.

        query_set = ResetPassword.objects.filter(uid=uid, token=token)
        if query_set.exists():
            reset_password = query_set[0] 

            from datetime import date, timedelta
            print('Given:', reset_password.date, '; Expires:', (date.today() + timedelta(days=1)))
            if date.today() > (reset_password.date + timedelta(days=1)):
                print('Old')
                return Response({'message': 'Stale forgotten password token, request a new one.'}, status=status.HTTP_401_UNAUTHORIZED)

            user = reset_password.user

            try:
                user.password = new_password
                user.save()
                print('Updated password')
            except:
                return Response({'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

            reset_password.delete()
            return Response(status=status.HTTP_200_OK)
        return Response({'message': 'Stale forgotten password token, request a new one.'}, status=status.HTTP_401_UNAUTHORIZED)

# from django.shortcuts import redirect   
# def ResetPassword(request):
#     print('Stuff')
#     response = redirect('/reset-password/')
#     return response
# export async function apiForgotPassword (data) {
#     return ApiService.fetchData({
#         url: '/forgot-password',
#         method: 'post',
#         data
#     })
# }

# export async function apiResetPassword (data) {
#     return ApiService.fetchData({
#         url: '/reset-password',
#         method: 'post',
#         data
#     })
# } 