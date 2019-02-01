from asgiref.sync import async_to_sync
from jobmonitor.message import IMMessageBackend
from .models import MonitorLog


class WSMessageBackend(IMMessageBackend):

    def __init__(self, channel_layer, group_name, monitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer = channel_layer
        self.group_name = group_name
        self.monitor = monitor

    def send_raw_message(self, content):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_message',
                'message': content,
                'monitor_pk': self.monitor.pk
            }
        )


class DbMessageBackend(IMMessageBackend):

    def __init__(self, monitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = monitor

    def send_raw_message(self, content):
        MonitorLog.objects.create(monitor=self.monitor, message=content)
