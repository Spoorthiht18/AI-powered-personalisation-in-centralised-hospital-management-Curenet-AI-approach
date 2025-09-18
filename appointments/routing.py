from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/queue/(?P<hospital_id>\w+)/$', consumers.QueueTokenConsumer.as_asgi()),
    re_path(r'ws/video_call/(?P<room_id>\w+)/$', consumers.VideoCallConsumer.as_asgi()),
]
