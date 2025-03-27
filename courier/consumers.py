#this file and code is for the live tracking of the parcel

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TrackingConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        self.group_name = None
        self.tracking_number = None

    async def connect(self):
        self.tracking_number = self.scope["url_route"]["kwargs"]["tracking_number"]
        self.group_name = f"tracking_{self.tracking_number}"

        # Join a group specific to this tracking number.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group on disconnect.
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # If the consumer receives a message from the group, send it to the client.
    async def tracking_update(self, event):
        await self.send(text_data=json.dumps({
            "tracking_number": self.tracking_number,
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "timestamp": event["timestamp"],
        }))
