import json

from channels.generic.websocket import AsyncWebsocketConsumer


class JobMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'job_monitor_messages'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    async def send_message(self, event):
        message = event['message']
        message_type = event.get('message_type')  # task_status
        monitor_pk = event['monitor_pk']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message_type': message_type,
            'message': message,
            'monitor_pk': monitor_pk
        }))
