from rest_framework import serializers
from .models import Member, Story, Group, Network, Location, Notification


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', 'name', 'username', 'gender', 'phone_number', 'photo_url', 'clean_date')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'member_id', 'name', 'code', 'date_time')

class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ('id', 'member_id', 'name', 'photo_url')

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'title', 'member_id', 'member_name', 'date_time', 'url', 'thumbnail_url')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'member_id', 'lat', 'lng')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'member_id', 'message', 'group_name', 'network_id', 'call_code', 'opt', 'date_time', 'sender_id', 'sender_name', 'sender_phone', 'sender_photo')









































