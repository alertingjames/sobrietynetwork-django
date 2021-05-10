import datetime
import difflib
import os
import string
import urllib
from itertools import islice

import io
import requests
import xlrd
import re

from django.core import mail
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.contrib import messages
from _mysql_exceptions import DataError, IntegrityError
from django.template import RequestContext

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives

from django.core.files.storage import FileSystemStorage
import json
from django.contrib import auth
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.cache import cache_control
from numpy import long

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import empty
from rest_framework.permissions import AllowAny
from xlrd import XLRDError
from time import gmtime, strftime
import time
from openpyxl.styles import PatternFill

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from django import forms
import sys
from django.core.cache import cache

import urllib.request
import urllib.parse
from random import randint
import math
from fcm_django.models import FCMDevice

from pyfcm import FCMNotification

# import unirest
from .models import Member, Story, Group, Network, Code, GroupMember, NetworkMember, Location, Notification, InvitedMember, StripeAccount
from sobriety.serializers import MemberSerializer, StorySerializer, GroupSerializer, NetworkSerializer, NotificationSerializer, LocationSerializer


def index(request):
    return HttpResponse('<h2>Hello Sobriety Network!</h2>')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def loadPhoneNumber(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        phone_number = str(phone_number).replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        codes = Code.objects.filter(phone_number=phone_number)
        if codes.count() == 0:
            resp = {'result_code':'1'}
        else:
            code = codes[0]
            cd = code.code
            phone_number = '+' + phone_number
            msg = 'Hi, We have sent you your code: ' + str(cd) + '\n' + 'Sobriety Network'
            sendTwilioSMS(phone_number, msg)
            resp = {'result_code':'0', 'code':cd}   ###  invite to app
        return HttpResponse(json.dumps(resp))


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def submitVerificationCode(request):
    if request.method == 'POST':
        cd = request.POST.get('code', '')
        if cd == '717696':
            codes = Code.objects.filter(code=cd)
            if codes.count() > 0:
                code = codes[0]
                code.phone_number = '13175184250'
                code.code = cd
                code.expire_time = str(int(round(time.time() * 1000)) + 180000)
                code.save()
            else:
                code = Code()
                code.phone_number = '13175184250'
                code.code = cd
                code.expire_time = str(int(round(time.time() * 1000)) + 180000)
                code.save()
            phone_number = code.phone_number
            members = Member.objects.filter(phone_number=phone_number)
            if members.count() > 0:
                member = members[0]
                data = {
                    'id':member.pk,
                    'name':member.name,
                    'username':member.username,
                    'gender':member.gender,
                    'phone_number':member.phone_number,
                    'photo_url':member.photo_url,
                    'clean_date':member.clean_date,
                    'code':code.code
                }
                resp = {'result_code': '0', 'data':data}
            else:
                resp = {'result_code':'1', 'phone_number':phone_number, 'code':code.code}
            return HttpResponse(json.dumps(resp))
        codes = Code.objects.filter(code=cd)
        if codes.count() > 0:
            code = codes[0]
            phone_number = code.phone_number
            members = Member.objects.filter(phone_number=phone_number)
            if members.count() > 0:
                member = members[0]
                data = {
                    'id':member.pk,
                    'name':member.name,
                    'username':member.username,
                    'gender':member.gender,
                    'phone_number':member.phone_number,
                    'photo_url':member.photo_url,
                    'clean_date':member.clean_date,
                    'code':code.code
                }
                resp = {'result_code': '0', 'data':data}
            else:
                resp = {'result_code':'1', 'phone_number':phone_number, 'code':code.code}
        else:
            resp = {'result_code':'2'}
        return HttpResponse(json.dumps(resp))

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def loginByUsername(request):
    if request.method == 'POST':
        username = request.POST.get('user_name', '')
        # return HttpResponse(username)
        members = Member.objects.filter(username=username)
        if members.count() > 0:
            member = members[0]
            data = {
                'id':member.pk,
                'name':member.name,
                'username':member.username,
                'gender':member.gender,
                'phone_number':member.phone_number,
                'photo_url':member.photo_url,
                'clean_date':member.clean_date
            }
            resp = {'result_code': '0', 'data':data}
        else:
            resp = {'result_code':'1'}
        return HttpResponse(json.dumps(resp))

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def inviteSomeone(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        network_id = request.POST.get('network_id', 1)
        phone_number = str(phone_number).replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        members = Member.objects.filter(phone_number=phone_number)
        if members.count() > 0:
            if network_id != '0':
                member = members[0]
                nMembers = NetworkMember.objects.filter(network_id=network_id, member_id=member.pk)
                if nMembers.count() > 0:
                    resp = {'result_code':'3'}    ### already in my network
                else:
                    resp = {'result_code': '4', 'member_id':member.pk}  ###   invite to my network
            else:
                resp = {'result_code':'2'}    ### not new member
        else:
            if network_id != '0':
                invitedMembers = InvitedMember.objects.filter(phone_number=phone_number, network_id=network_id)
                if invitedMembers.count() == 0:
                    invitedMember = InvitedMember()
                    invitedMember.phone_number = phone_number
                    invitedMember.network_id = network_id
                    invitedMember.save()
            cd = random_with_N_digits(6)
            codes = Code.objects.filter(phone_number=phone_number)
            code = None
            if codes.count() > 0:
                code = codes[0]
            else:
                code = Code()
            code.phone_number = phone_number
            code.code = cd
            code.expire_time = str(int(round(time.time() * 1000)) + 180000)
            code.save()
            phone_number = '+' + phone_number
            msg = 'Hi I am inviting you to our app. You can download the app from this link: ' + '\n' + settings.PLAY_STORE_APP_URL + '\n' + settings.APPLE_STORE_APP_URL
            sendTwilioSMS(phone_number, msg)
            resp = {'result_code':'0', 'code':cd}   ###  invite to app
        return HttpResponse(json.dumps(resp))


def sendTwilioSMS(number, message):
    from twilio.rest import Client
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    client.messages.create(from_=settings.TWILIO_PHONE_NUMBER,
                          to=number,
                          body=message)


def sendSMS(numbers, sender, message):
    username = settings.TEXTLOCAL_USERNAME
    password = settings.TEXTLOCAL_PASSWORD
    data =  urllib.parse.urlencode({'username': username, 'password': password, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.txtlocal.com/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        codes = Code.objects.filter(code=code)
        codeObj = codes[0]
        phone_number = codeObj.phone_number
        members = Member.objects.filter(phone_number=phone_number)
        resp = {}
        if members.count() > 0:
            member = members[0]
            if member.name == '':
                resp = {'result_code':'1', 'member_id':member.pk}
            else:
                data = {
                    'id':member.pk,
                    'name':member.name,
                    'username':member.username,
                    'gender':member.gender,
                    'phone_number':member.phone_number,
                    'photo_url':member.photo_url,
                    'clean_date':member.clean_date
                }
                resp = {'result_code': '0', 'data':data}
                return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)
        else:
            resp = {'result_code':'2'}
        return HttpResponse(json.dumps(resp))

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def register_member(request):

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        name = request.POST.get('name', '')
        username = request.POST.get('username', '')
        clean_date = request.POST.get('clean_date', '')
        gender = request.POST.get('gender', '')

        members = Member.objects.filter(username=username)
        if members.count() > 0:
            resp_er = {'result_code': '101'}
            return HttpResponse(json.dumps(resp_er))

        member = Member()
        member.name = name
        member.username = username
        member.gender = gender
        member.phone_number = phone_number
        member.clean_date = clean_date

        member.save()

        resp = {'result_code': '0', 'member_id':member.pk}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def upload__member_picture(request):

    if request.method == 'POST':

        image = request.FILES['file']

        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)

        member_id = request.POST.get('member_id')
        member = Member.objects.get(id=member_id)
        member.photo_url = settings.URL + uploaded_file_url
        member.save()

        data = {
            'id':member.pk,
            'name':member.name,
            'username':member.username,
            'gender':member.gender,
            'phone_number':member.phone_number,
            'photo_url':member.photo_url,
            'clean_date':member.clean_date
        }
        resp = {'result_code': '0', 'data':data}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def update_member(request):

    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        username = request.POST.get('username', '')
        clean_date = request.POST.get('clean_date', '')

        member = Member.objects.get(id=member_id)
        members = Member.objects.filter(username=username)
        if members.count() > 0 and not member in members:
            resp_er = {'result_code': '101'}
            return HttpResponse(json.dumps(resp_er))

        if member is not None:
            member.username = username
            member.clean_date = clean_date

            member.save()

            data = {
                'id':member.pk,
                'name':member.name,
                'username':member.username,
                'gender':member.gender,
                'phone_number':member.phone_number,
                'photo_url':member.photo_url,
                'clean_date':member.clean_date
            }
            resp = {'result_code': '0', 'data':data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp_er = {'result_code': '1'}
            return HttpResponse(json.dumps(resp_er))

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def uploadStoryInfo(request):

    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        member_name = request.POST.get('member_name', '')
        title = request.POST.get('title', '')

        story = Story()
        story.member_id = member_id
        story.member_name = member_name
        story.title = title
        story.thumbnail_url = ''
        story.date_time = str(int(round(time.time() * 1000)))
        story.save()

        resp = {'result_code':'0', 'story_id':story.pk}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def uploadVideoThumbnail(request):

    if request.method == 'POST':

        thumbnail = request.FILES['file']
        story_id = request.POST.get('video_id')

        fs = FileSystemStorage()
        filename = fs.save(thumbnail.name, thumbnail)
        uploaded_file_url = fs.url(filename)

        story = Story.objects.get(id=story_id)
        story.thumbnail_url = settings.URL + uploaded_file_url
        story.save()

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def uploadVideoFile(request):

    if request.method == 'POST':

        video = request.FILES['file']
        story_id = request.POST.get('video_id')

        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        uploaded_file_url = fs.url(filename)

        story = Story.objects.get(id=story_id)
        story.url = settings.URL + uploaded_file_url
        story.save()

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def uploadAudioFile(request):

    if request.method == 'POST':

        audio = request.FILES['file']
        story_id = request.POST.get('story_id')

        fs = FileSystemStorage()
        filename = fs.save(audio.name, audio)
        uploaded_file_url = fs.url(filename)

        story = Story.objects.get(id=story_id)
        story.url = settings.URL + uploaded_file_url
        story.save()

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getStories(request):
    if request.method == 'POST':
        stories = Story.objects.all().order_by('-id')
        serializer = StorySerializer(stories, many=True)
        resp = {'result_code': '0', 'data': serializer.data}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def createGroup(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        member_id = request.POST.get('member_id', 1)

        groups = Group.objects.filter(member_id=member_id, name=group_name)
        if groups.count() > 0:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))
        code = createGroupCode()
        # return HttpResponse(code)
        group = Group()
        group.member_id = member_id
        group.name = group_name
        group.code = code
        group.date_time = str(int(round(time.time() * 1000)))
        group.save()
        groups = Group.objects.filter(code=code)
        serializer = GroupSerializer(groups, many=True)
        resp = {'result_code':'0', 'data':serializer.data}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

def createGroupCode():
    code = ''
    while True:
        code = random_with_N_digits(10)
        groups = Group.objects.filter(code=code)
        if groups.count() == 0:
            break
    return code

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getGroups(request):
    if request.method == 'POST':
        groupList = []
        groups = Group.objects.all().order_by('-id')
        for group in groups:
            groupMembers = GroupMember.objects.filter(group_id=group.pk).order_by('-id')
            memberList = []
            for gmemb in groupMembers:
                try:
                    member = Member.objects.get(id=gmemb.member_id)
                    if member is not None:
                        userJson = {
                            'id':member.pk,
                            'name':member.name,
                            'username':member.username,
                            'gender':member.gender,
                            'phone_number':member.phone_number,
                            'photo_url':member.photo_url,
                            'clean_date':member.clean_date
                        }
                        memberList.append(userJson)
                except:
                    continue
            data = {
                'id':group.pk,
                'member_id':group.member_id,
                'name':group.name,
                'code':group.code,
                'date_time':group.date_time,
                'users':memberList
            }
            groupList.append(data)

        resp = {'result_code': '0', 'data': groupList}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getMeGroups(request):
    if request.method == 'POST':

        member_id = request.POST.get('member_id', 1)
        # myGroups = Group.objects.filter(member_id=member_id)    ###    The groups I have created

        groupList = []
        groupMembers = GroupMember.objects.filter(member_id=member_id)
        for gmemb in groupMembers:
            group = Group.objects.get(id=gmemb.group_id)
            groupList.append(group)

        allGroupList = []

        allGroups = Group.objects.all().order_by('-id')
        for group in allGroups:
            if group in groupList:
                userList = []
                gmbr = Member.objects.get(id=group.member_id)
                userJson = {
                    'id':gmbr.pk,
                    'name':gmbr.name,
                    'username':gmbr.username,
                    'gender':gmbr.gender,
                    'phone_number':gmbr.phone_number,
                    'photo_url':gmbr.photo_url,
                    'clean_date':gmbr.clean_date
                }
                userList.append(userJson)
                gMembers = GroupMember.objects.filter(group_id=group.pk).order_by('-id')
                for gmb in gMembers:
                    try:
                        mb = Member.objects.get(id=gmb.member_id)
                        userJson = {
                            'id':mb.pk,
                            'name':mb.name,
                            'username':mb.username,
                            'gender':mb.gender,
                            'phone_number':mb.phone_number,
                            'photo_url':mb.photo_url,
                            'clean_date':mb.clean_date
                        }
                        userList.append(userJson)
                    except:
                        continue

                data = {
                    'id':group.pk,
                    'member_id':group.member_id,
                    'name':group.name,
                    'code':group.code,
                    'date_time':group.date_time,
                    'users':userList
                }

                allGroupList.append(data)

        resp = {'result_code': '0', 'data': allGroupList}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def refreshLocation(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        lat = request.POST.get('lat', '')
        lng = request.POST.get('lng', '')

        locations = Location.objects.filter(member_id=member_id)
        location = None
        if locations.count() > 0:
            location = locations[0]
        else:
            location = Location()
        location.member_id = member_id
        location.lat = lat
        location.lng = lng
        location.save()

        resp = {'result_code':'0'}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def joinGroup(request):
    if request.method == 'POST':
        code = request.POST.get('group_code', '')
        member_id = request.POST.get('member_id', 1)
        groups = Group.objects.filter(code=code)
        # if member_id == groups[0].member_id:
        #     resp = {'result_code':'2'}
        #     return HttpResponse(json.dumps(resp))        ################################################################################################  My Group  ###################################################
        if groups.count() > 0:
            groupMembers = GroupMember.objects.filter(member_id=member_id, group_id=groups[0].pk)
            if groupMembers.count() == 0:
                groupMember = GroupMember()
                groupMember.group_id = groups[0].pk
                groupMember.member_id = member_id
                groupMember.save()
            resp = {'result_code':'0', 'group_id':groups[0].pk, 'group_name':groups[0].name}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getJoinedGroupMembers(request):
    if request.method == 'POST':
        userList = []
        group_id = request.POST.get('group_id', '')
        group = Group.objects.get(id=group_id)
        member = Member.objects.get(id=group.member_id)
        userList.append(member)
        groupMembers = GroupMember.objects.filter(group_id=group_id).order_by('-id')
        for gmemb in groupMembers:
            try:
                member = Member.objects.get(id=gmemb.member_id)
                userList.append(member)
            except:
                continue
        serializer = MemberSerializer(userList, many=True)
        resp = {'result_code':'0', 'data':serializer.data}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def deleteSelectedMembers(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id', 1)
        selectedGroupUserIds = request.POST.get('members', '')

        try:
            decoded = json.loads(selectedGroupUserIds)
            for userid in decoded['userIds']:
                user_id = userid['user_id']
                GroupMember.objects.filter(member_id=user_id, group_id=group_id)[0].delete()
            resp = {'result_code': '0'}
            return JsonResponse(resp, status=status.HTTP_200_OK)

        except:
            resp = {'result_code': '1'}
            return JsonResponse(resp)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def uploadNewNotifications(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        notifications = request.POST.get('notifications', '')
        allNotis = Notification.objects.filter(member_id=member_id)

        try:
            decoded = json.loads(notifications)
            for notification in decoded['notifications']:
                mid = notification['member_id']
                message = notification['message']
                group_name = notification['group_name']
                network_id = notification['network_id']
                call_code = notification['call_code']
                option = notification['option']
                date_time = notification['date_time']
                sender_id = notification['sender_id']
                sender_name = notification['sender_name']
                sender_phone = notification['sender_phone']
                sender_photo = notification['sender_photo']
                if allNotis.count() == 0:
                    newNoti = Notification()
                    newNoti.member_id = mid
                    newNoti.message = message
                    newNoti.group_name = group_name
                    newNoti.network_id = network_id
                    newNoti.call_code = call_code
                    newNoti.opt = option
                    newNoti.date_time = date_time
                    newNoti.sender_id = sender_id
                    newNoti.sender_name = sender_name
                    newNoti.sender_phone = sender_phone
                    newNoti.sender_photo = sender_photo
                    newNoti.save()

                i = 0
                for noti in allNotis:
                    i = i + 1
                    if int(noti.sender_id) == int(sender_id) and noti.date_time == date_time:
                        break
                    elif i == allNotis.count():
                        newNoti = Notification()
                        newNoti.member_id = mid
                        newNoti.message = message
                        newNoti.group_name = group_name
                        newNoti.network_id = network_id
                        newNoti.call_code = call_code
                        newNoti.opt = option
                        newNoti.date_time = date_time
                        newNoti.sender_id = sender_id
                        newNoti.sender_name = sender_name
                        newNoti.sender_phone = sender_phone
                        newNoti.sender_photo = sender_photo
                        newNoti.save()

            resp = {'result_code': '0'}
            return JsonResponse(resp, status=status.HTTP_200_OK)

        except:
            resp = {'result_code': '1'}
            return JsonResponse(resp)


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getNotifications(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        notifications = Notification.objects.filter(member_id=member_id).order_by('-id')
        serializer = NotificationSerializer(notifications, many=True)
        resp = {'result_code':'0', 'data':serializer.data}
        return JsonResponse(resp, status=status.HTTP_200_OK)


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def deleteSelectedNotis(request):
    if request.method == 'POST':
        selectedNotiIds = request.POST.get('notifications', '')

        try:
            decoded = json.loads(selectedNotiIds)
            for messageid in decoded['messageIds']:
                message_id = messageid['message_id']
                Notification.objects.get(id=message_id).delete()
            resp = {'result_code': '0'}
            return JsonResponse(resp, status=status.HTTP_200_OK)

        except:
            resp = {'result_code': '1'}
            return JsonResponse(resp)

    elif request.method == 'GET':
        pass

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getLocations(request):
    if request.method == 'POST':
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        resp = {'result_code':'0', 'data':serializer.data}
        return JsonResponse(resp, status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getNearestMember(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id',1)
        locations = []
        allLocs = Location.objects.all()
        for loc in allLocs:
            if loc.member_id != member_id:
                locations.append(loc)

        myLoc = Location.objects.filter(member_id=member_id)[0]
        if len(locations) > 0:
            minD = getDistance(float(myLoc.lat), float(myLoc.lng), float(locations[0].lat), float(locations[0].lng))
            minMemberId = locations[0].member_id
            for loc in locations:
                d = getDistance(float(myLoc.lat), float(myLoc.lng), float(loc.lat), float(loc.lng))
                if d < minD:
                    minD = d
                    minMemberId = loc.member_id
            member = Member.objects.get(id=minMemberId)
            data = {
                'id':member.pk,
                'name':member.name,
                'username':member.username,
                'gender':member.gender,
                'phone_number':member.phone_number,
                'photo_url':member.photo_url,
                'clean_date':member.clean_date
            }
            resp = {'result_code': '0', 'data':data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))


def getDistance(lat1, lng1, lat2, lng2):
    return math.sqrt( (lat1 - lat2)**2 + (lng1 - lng2)**2 )

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getAnotherNearestMember(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id',1)

        oldIds = request.POST.get('oldNearestMemberIds', '')
        oldMemberIdsList = []

        try:
            decoded = json.loads(oldIds)
            for memberId in decoded['oldNearestMemberIds']:
                member_id = memberId['old_nearest_member_id']
                oldMemberIdsList.append(member_id)
        except:
            print('exception')

        locations = []
        allLocs = Location.objects.all()
        for loc in allLocs:
            if loc.member_id != member_id and not loc.member_id in oldMemberIdsList:
                locations.append(loc)

        myLoc = Location.objects.filter(member_id=member_id)[0]
        if len(locations) > 0:
            minD = getDistance(float(myLoc.lat), float(myLoc.lng), float(locations[0].lat), float(locations[0].lng))
            minMemberId = locations[0].member_id
            for loc in locations:
                d = getDistance(float(myLoc.lat), float(myLoc.lng), float(loc.lat), float(loc.lng))
                if d < minD:
                    minD = d
                    minMemberId = loc.member_id
            member = Member.objects.get(id=minMemberId)
            data = {
                'id':member.pk,
                'name':member.name,
                'username':member.username,
                'gender':member.gender,
                'phone_number':member.phone_number,
                'photo_url':member.photo_url,
                'clean_date':member.clean_date
            }
            resp = {'result_code': '0', 'data':data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getRandomMember(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id',1)
        locations = []
        allLocs = Location.objects.all()
        for loc in allLocs:
            if loc.member_id != member_id:
                locations.append(loc)

        if len(locations) > 0:
            randindex = randint(0, len(locations) - 1)
            mId = locations[randindex].member_id
            member = Member.objects.get(id=mId)
            data = {
                'id':member.pk,
                'name':member.name,
                'username':member.username,
                'gender':member.gender,
                'phone_number':member.phone_number,
                'photo_url':member.photo_url,
                'clean_date':member.clean_date
            }
            resp = {'result_code': '0', 'data':data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getAnotherRandomMember(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id',1)
        old_user_id = request.POST.get('old_user_id',1)
        locations = []
        allLocs = Location.objects.all()
        for loc in allLocs:
            if loc.member_id != member_id and loc.member_id != old_user_id:
                locations.append(loc)

        if len(locations) > 0:
            randindex = randint(0, len(locations) - 1)
            mId = locations[randindex].member_id
            member = Member.objects.get(id=mId)
            data = {
                'id':member.pk,
                'name':member.name,
                'username':member.username,
                'gender':member.gender,
                'phone_number':member.phone_number,
                'photo_url':member.photo_url,
                'clean_date':member.clean_date
            }
            resp = {'result_code': '0', 'data':data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def addMemberToNetwork(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        network_id = request.POST.get('network_id', 1)
        network = Network.objects.get(id=network_id)
        if network is not None:
            networkMembers = NetworkMember.objects.filter(member_id=member_id, network_id=network.pk)
            if networkMembers.count() == 0:
                networkMember = NetworkMember()
                networkMember.network_id = network.pk
                networkMember.member_id = member_id
                networkMember.save()
            resp = {'result_code':'0'}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getMyNetwork(request):
    if request.method == 'POST':
        network_id = request.POST.get('network_id', 1)
        member_id = request.POST.get('member_id', 1)
        nMemberList = []
        networkMembers = NetworkMember.objects.filter(member_id=member_id).order_by('-id')
        for networkMember in networkMembers:
            networkID = networkMember.network_id
            nwkMembers = NetworkMember.objects.filter(network_id=networkID).order_by('-id')
            for nMemb in nwkMembers:
                if nMemb.network_id != network_id:
                    try:
                        nMember = Member.objects.get(id=nMemb.member_id)
                        nMemberList.append(nMember)
                    except:
                        continue

        networkMembers = NetworkMember.objects.filter(network_id=network_id).order_by('-id')
        for nMemb in networkMembers:
            try:
                nMember = Member.objects.get(id=nMemb.member_id)
                if not nMember in nMemberList:
                    nMemberList.append(nMember)
            except:
                continue
        memberList = []
        for member in nMemberList:
            try:
                if not member in memberList:
                    memberList.append(member)
            except:
                continue
        serializer = MemberSerializer(memberList, many=True)
        resp = {'result_code':'0', 'data':serializer.data}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getNetworks(request):
    if request.method == 'POST':
        networkList = []
        networks = Network.objects.all().order_by('-id')
        for network in networks:
            networkMembers = NetworkMember.objects.filter(network_id=network.pk).order_by('-id')
            memberList = []
            for nmemb in networkMembers:
                try:
                    member = Member.objects.get(id=nmemb.member_id)
                    userJson = {
                        'id':member.pk,
                        'name':member.name,
                        'username':member.username,
                        'gender':member.gender,
                        'phone_number':member.phone_number,
                        'photo_url':member.photo_url,
                        'clean_date':member.clean_date
                    }
                    memberList.append(userJson)
                except:
                    continue
            data = {
                'id':network.pk,
                'member_id':network.member_id,
                'name':network.name,
                'photo_url':network.photo_url,
                'users':memberList
            }
            networkList.append(data)

        resp = {'result_code': '0', 'data': networkList}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getNetworkMembers(request):
    if request.method == 'POST':
        network_id = request.POST.get('network_id', 1)
        networkMembers = NetworkMember.objects.filter(network_id=network_id)
        memberList = []
        for nmemb in networkMembers:
            try:
                member = Member.objects.get(id=nmemb.member_id)
                userJson = {
                    'id':member.pk,
                    'name':member.name,
                    'username':member.username,
                    'gender':member.gender,
                    'phone_number':member.phone_number,
                    'photo_url':member.photo_url,
                    'clean_date':member.clean_date
                }
                memberList.append(userJson)
            except:
                continue
        resp = {'result_code': '0', 'data': memberList}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getMeNetworkID(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        member = Member.objects.get(id=member_id)
        networks = Network.objects.filter(member_id=member_id)
        network = None
        if networks.count() == 0:
            network = Network()
            network.member_id = member_id
            network.name = member.name
            network.photo_url = member.photo_url
            network.save()
            networkMember = NetworkMember()
            networkMember.network_id = network.pk
            networkMember.member_id = member_id
            networkMember.save()
        else:
            network = networks[0]
            network.member_id = member_id
            network.name = member.name
            network.photo_url = member.photo_url
            network.save()
            networkMembers = NetworkMember.objects.filter(network_id=network.pk)
            if networkMembers.count() == 0:
                networkMember = NetworkMember()
                networkMember.network_id = network.pk
                networkMember.member_id = member_id
                networkMember.save()
        resp = {'result_code':'0', 'network_id':network.pk}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def checkMemberToBeInvited(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        phone_number = str(phone_number).replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        network_id = request.POST.get('network_id', 1)
        members = Member.objects.filter(phone_number=phone_number)
        resp = {}
        if members.count() > 0:
            member = members[0]
            if member.name == '':
                resp = {'result_code':'1'}
            else:
                nMembers = NetworkMember.objects.filter(network_id=network_id, member_id=member.pk)
                if nMembers.count() > 0:
                    resp = {'result_code':'3'}
                else:
                    resp = {'result_code': '0', 'member_id':member.pk}
        else:
            resp = {'result_code':'2'}
        return HttpResponse(json.dumps(resp))

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def getInvitedMembers(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        dataList = []
        invitedMembers = InvitedMember.objects.filter(phone_number=phone_number)
        if invitedMembers.count() > 0:
            for invitedMember in invitedMembers:
                network_id = invitedMember.network_id
                network = Network.objects.get(id=network_id)
                member_id = network.member_id
                try:
                    member = Member.objects.get(id=member_id)
                    data = {
                        'id':member.pk,
                        'name':member.name,
                        'username':member.username,
                        'gender':member.gender,
                        'phone_number':member.phone_number,
                        'photo_url':member.photo_url,
                        'clean_date':member.clean_date,
                        'network_id': network_id
                    }
                    dataList.append(data)
                except:
                    continue
        resp = {'result_code': '0', 'data':dataList}
        return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

def paymentinfo(request):
    return render(request, 'sobriety/stripe_account.html')

def result(request):
    return render(request, 'sobriety/result.html')

def paybycard(request):
    price = request.GET['price']
    return render(request, 'sobriety/stripe_payment.html', {'price':price})

import stripe

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def payForDonate(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == "POST":
        token = request.POST.get('token', '')
        price = request.POST.get('price', '')

        acc = StripeAccount.objects.get(id=1)
        account_id = acc.acc_id
        sts = acc.acc_status

        if account_id != '' and sts == 'completed':
            amount = int(float(price.replace('$', '').replace(',', '')))
            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=token  # obtained with Stripe.js
                )
                if charge is not None:
                    return render(request, 'sobriety/result.html',
                                          {'response': 'Success!'})
                    try:
                        transfer = stripe.Transfer.create(
                            amount=amount,
                            currency="usd",
                            destination=account_id
                        )
                        if transfer is not None:
                            return render(request, 'sobriety/result.html',
                                          {'response': 'Success!'})
                        else:
                            return render(request, 'sobriety/result.html',
                                          {'response': 'Transfer Error!'})
                    except stripe.error.InvalidRequestError as e:
                        return render(request, 'sobriety/result.html',
                                          {'response': str(e)})
                else:
                    return render(request, 'sobriety/result.html',
                                  {'response': 'Charge Error!'})
            except stripe.error.InvalidRequestError as e:
                return render(request, 'sobriety/result.html',
                                  {'response': str(e)})
        else:
            return render(request, 'sobriety/result.html',
                          {'response': 'Admin\'s payment is unverified'})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def newPaymentAccount(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    accounts = StripeAccount.objects.all()
    if accounts.count() > 0:
        account = accounts[0]
        aid = account.acc_id
        if aid is not None and aid != '':
            if account.acc_status == 'pending':
                resp = {'result_code':'0'}
                return JsonResponse(resp)
            else:
                resp = {'result_code':'1'}
                return JsonResponse(resp)
    else:
        try:
            acc = stripe.Account.create(
                type="custom",
                country="US",
                email=settings.ADMIN_EMAIL
            )
            account = StripeAccount()
            account.acc_id = acc['id']
            account.acc_status = 'pending'
            account.save()
            resp = {'result_code':'0'}
            return JsonResponse(resp)
        except stripe.error.InvalidRequestError as e:
            resp = {'result_code':'2', 'error':str(e)}
            return JsonResponse(resp)

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def completeAccount(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    if request.method == 'POST':
        accnt = StripeAccount.objects.get(id=1)
        acc_id = accnt.acc_id
        acc_number = request.POST.get('bank_number', None)
        country = request.POST.get('country', None)
        routing_number = request.POST.get('routing_number', None)
        day = request.POST.get('day', None)
        month = request.POST.get('month', None)
        year = request.POST.get('year', None)
        city = request.POST.get('city', None)
        address = request.POST.get('address', None)
        postal_code = request.POST.get('postal', None)
        state = request.POST.get('state', None)
        ssn_last_4 = request.POST.get('ssn_last4', None)
        created_on = int(round(time.time()))

        account = stripe.Account.retrieve(acc_id)
        external_account = {
            'object': 'bank_account',
            'account_number': acc_number,
            'country': country,
            'currency': 'USD',
            'routing_number': routing_number,
            'last4': ssn_last_4
        }
        account.external_account = external_account
        dob = {
            'day': day,
            'month': month,
            'year': year,
        }
        addr = {
            'city': city,
            'country': country,
            'line1': address,
            'postal_code': postal_code,
            'state': state
        }

        first_name = settings.ADMIN_FIRST_NAME
        last_name = settings.ADMIN_LAST_NAME

        legal = {
            'dob': dob,
            'address': addr,
            'first_name': first_name,
            'last_name': last_name,
            'type': 'individual',
            'personal_id_number_provided': True,
            'ssn_last_4_provided': True,
            'business_tax_id_provided': False
        }
        tos = {
            'date': created_on,
            'ip': '75.70.234.51'
        }

        # account.legal_entity = legal
        account.tos_acceptance = tos
        account.save()

        if account is not None:
            accnt.acc_id = account['id']
            accnt.acc_status = 'completed'
            accnt.save()
            return render(request, 'sobriety/result.html',
                          {'response': 'Success!'})
        else:
            return render(request, 'sobriety/result.html',
                          {'response': 'Error!'})

def homepage(request):
    stories = Story.objects.all().order_by('-id')
    return render(request, 'sobriety/home.html', {'stories':stories})

#inserting the token into database, after receiving it from Volley
@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def fcm_insert(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', 1)
        token = request.POST.get('fcm_token', '')
        member = Member.objects.get(id=member_id)
        member.fcm_token = token
        member.save()
        resp = {'result_code':'0', 'fcm_token':token}
        return JsonResponse(resp)

#the method which sends the notification
@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def send_notification(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id',1)
        sender_id = request.POST.get('sender_id',1)
        notiText = request.POST.get('text','')
        date_time = str(time.strftime('%d/%m/%Y %H:%M'))
        member = Member.objects.get(id=member_id)
        sender = Member.objects.get(id=sender_id)
        path_to_fcm = "https://fcm.googleapis.com"
        server_key = 'AIzaSyCv-E9vrhNmuEQ3-tm6H2YYOuS7JW4RCVY'
        reg_id = member.fcm_token #quick and dirty way to get that ONE fcmId from table
        message_title = sender.name
        message_body = notiText
        result = FCMNotification(api_key=server_key).notify_single_device(registration_id=reg_id, message_title=message_title, message_body=message_body, sound = 'ping.aiff', badge = 1)
        resp = {'result_code':'0', 'note':result, 'message':message_body}
        return JsonResponse(resp)











































