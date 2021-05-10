from django.db import models

# Create your models here.

class Member(models.Model):
    name = models.CharField(max_length=50)
    username=models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=1000)
    clean_date = models.CharField(max_length=50)
    fcm_token = models.CharField(max_length=1000)

class Story(models.Model):
    title = models.CharField(max_length=50)
    member_id=models.CharField(max_length=11)
    member_name = models.CharField(max_length=50)
    date_time = models.CharField(max_length=50)
    url = models.CharField(max_length=1000)
    thumbnail_url = models.CharField(max_length=1000)

class Network(models.Model):
    member_id=models.CharField(max_length=11)
    name = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=1000)

class NetworkMember(models.Model):
    network_id=models.CharField(max_length=11)
    member_id = models.CharField(max_length=11)

class Group(models.Model):
    member_id=models.CharField(max_length=11)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    date_time = models.CharField(max_length=50)

class GroupMember(models.Model):
    group_id=models.CharField(max_length=11)
    member_id = models.CharField(max_length=11)

class Code(models.Model):
    phone_number=models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    expire_time = models.CharField(max_length=50)

class Location(models.Model):
    member_id=models.CharField(max_length=11)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)

class Notification(models.Model):
    member_id = models.CharField(max_length=11)
    message = models.CharField(max_length=3000)
    group_name = models.CharField(max_length=50)
    network_id = models.CharField(max_length=11)
    call_code = models.CharField(max_length=50)
    opt = models.CharField(max_length=20)
    date_time = models.CharField(max_length=50)
    sender_id = models.CharField(max_length=11)
    sender_name = models.CharField(max_length=50)
    sender_phone = models.CharField(max_length=50)
    sender_photo = models.CharField(max_length=1000)

class InvitedMember(models.Model):
    phone_number=models.CharField(max_length=50)
    network_id = models.CharField(max_length=11)

class StripeAccount(models.Model):
    acc_id=models.CharField(max_length=100)
    acc_status = models.CharField(max_length=50)


































