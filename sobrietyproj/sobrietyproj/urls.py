from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from sobriety import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^sobriety/', include('sobriety.urls')),
    # url(r'^$', views.index, name='index'),
    url(r'^loadPhoneNumber',views.loadPhoneNumber,  name='loadPhoneNumber'),
    url(r'^submitVerificationCode',views.submitVerificationCode,  name='submitVerificationCode'),
    url(r'^login',views.login,  name='login'),
    url(r'^usernameLogin',views.loginByUsername,  name='loginByUsername'),
    url(r'^registerMember',views.register_member,  name='register_member'),
    url(r'^updateMember',views.update_member,  name='update_member'),
    url(r'^uploadMemberPicture',views.upload__member_picture,  name='upload__member_picture'),
    url(r'^uploadStoryInfo',views.uploadStoryInfo,  name='uploadStoryInfo'),
    url(r'^uploadVideoThumbnail',views.uploadVideoThumbnail,  name='uploadVideoThumbnail'),
    url(r'^uploadVideoFile',views.uploadVideoFile,  name='uploadVideoFile'),
    url(r'^uploadAudioFile',views.uploadAudioFile,  name='uploadAudioFile'),
    url(r'^getStories',views.getStories,  name='getStories'),
    url(r'^createGroup',views.createGroup,  name='createGroup'),
    url(r'^getGroups',views.getGroups,  name='getGroups'),
    url(r'^getMeGroups',views.getMeGroups,  name='getMeGroups'),
    url(r'^refreshLocation',views.refreshLocation,  name='refreshLocation'),
    url(r'^joinGroup',views.joinGroup,  name='joinGroup'),
    url(r'^getJoinedGroupMembers',views.getJoinedGroupMembers,  name='getJoinedGroupMembers'),
    url(r'^deleteSelectedMembers',views.deleteSelectedMembers,  name='deleteSelectedMembers'),
    url(r'^uploadNewNotifications',views.uploadNewNotifications,  name='uploadNewNotifications'),
    url(r'^getNotifications',views.getNotifications,  name='getNotifications'),
    url(r'^deleteSelectedNotis',views.deleteSelectedNotis,  name='deleteSelectedNotis'),
    url(r'^getLocations',views.getLocations,  name='getLocations'),
    url(r'^getNearestMember',views.getNearestMember,  name='getNearestMember'),
    url(r'^getAnotherNearestMember',views.getAnotherNearestMember,  name='getAnotherNearestMember'),
    url(r'^getRandomMember',views.getRandomMember,  name='getRandomMember'),
    url(r'^getAnotherRandomMember',views.getAnotherRandomMember,  name='getAnotherRandomMember'),
    url(r'^addMemberToNetwork',views.addMemberToNetwork,  name='addMemberToNetwork'),
    url(r'^getMyNetwork',views.getMyNetwork,  name='getMyNetwork'),
    url(r'^getNetworks',views.getNetworks,  name='getNetworks'),
    url(r'^getNetworkMembers',views.getNetworkMembers,  name='getNetworkMembers'),
    url(r'^getMeNetworkID',views.getMeNetworkID,  name='getMeNetworkID'),
    url(r'^checkMemberToBeInvited',views.checkMemberToBeInvited,  name='checkMemberToBeInvited'),
    url(r'^inviteSomeone',views.inviteSomeone,  name='inviteSomeone'),
    url(r'^getInvitedMembers',views.getInvitedMembers,  name='getInvitedMembers'),
    url(r'^paymentinfo',views.paymentinfo,  name='paymentinfo'),
    url(r'^paybycard',views.paybycard,  name='paybycard'),
    url(r'^result',views.result,  name='result'),
    url(r'^newPaymentAccount',views.newPaymentAccount,  name='newPaymentAccount'),
    url(r'^completeAccount',views.completeAccount,  name='completeAccount'),
    url(r'^payForDonate',views.payForDonate,  name='payForDonate'),

    url(r'^uploadfcmtoken',views.fcm_insert,  name='fcm_insert'),
    url(r'^sendnotification',views.send_notification,  name='send_notification'),

    url(r'^$',views.homepage,  name='homepage'),
]


urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns=format_suffix_patterns(urlpatterns)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)