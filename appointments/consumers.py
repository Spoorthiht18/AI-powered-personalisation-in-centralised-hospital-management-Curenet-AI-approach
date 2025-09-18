import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import QueueToken
from hospitals.models import Doctor, HospitalProfile

class QueueTokenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.hospital_id = self.scope['url_route']['kwargs']['hospital_id']
        self.room_group_name = f'queue_{self.hospital_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current queue status
        await self.send_queue_status()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'get_queue_status':
            await self.send_queue_status()
        elif message_type == 'update_token_status':
            token_id = text_data_json.get('token_id')
            new_status = text_data_json.get('status')
            await self.update_token_status(token_id, new_status)
    
    async def send_queue_status(self):
        """Send current queue status to the client."""
        queue_data = await self.get_queue_data()
        
        await self.send(text_data=json.dumps({
            'type': 'queue_status',
            'data': queue_data
        }))
    
    async def update_token_status(self, token_id, new_status):
        """Update token status and notify all clients."""
        token = await self.get_token(token_id)
        if token:
            await self.update_token(token, new_status)
            
            # Notify all clients in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'token_status_update',
                    'token_id': token_id,
                    'new_status': new_status
                }
            )
    
    async def token_status_update(self, event):
        """Handle token status update and send to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'token_status_update',
            'token_id': event['token_id'],
            'new_status': event['new_status']
        }))
    
    @database_sync_to_async
    def get_queue_data(self):
        """Get current queue data for the hospital."""
        try:
            hospital = HospitalProfile.objects.get(id=self.hospital_id)
            
            # Get active tokens
            active_tokens = QueueToken.objects.filter(
                hospital=hospital,
                status__in=['WAITING', 'CALLING', 'IN_PROGRESS']
            ).select_related('patient', 'doctor').order_by('created_at')
            
            # Get completed tokens for today
            today = timezone.now().date()
            completed_tokens = QueueToken.objects.filter(
                hospital=hospital,
                status='COMPLETED',
                completed_at__date=today
            ).select_related('patient', 'doctor').order_by('-completed_at')[:10]
            
            queue_data = {
                'hospital_name': hospital.name,
                'current_time': timezone.now().isoformat(),
                'active_tokens': [
                    {
                        'id': token.id,
                        'token_number': token.token_number,
                        'patient_name': token.patient.profile.full_name if hasattr(token.patient, 'profile') else f"Patient {token.patient.id}",
                        'doctor_name': token.doctor.name,
                        'department': token.department or token.doctor.specialization,
                        'status': token.status,
                        'priority': token.priority,
                        'created_at': token.created_at.isoformat(),
                        'estimated_wait_time': token.estimated_wait_time,
                        'position': token.get_position_in_queue()
                    }
                    for token in active_tokens
                ],
                'completed_tokens': [
                    {
                        'id': token.id,
                        'token_number': token.token_number,
                        'patient_name': token.patient.profile.full_name if hasattr(token.patient, 'profile') else f"Patient {token.patient.id}",
                        'doctor_name': token.doctor.name,
                        'completed_at': token.completed_at.isoformat() if token.completed_at else None
                    }
                    for token in completed_tokens
                ],
                'stats': {
                    'waiting': active_tokens.filter(status='WAITING').count(),
                    'calling': active_tokens.filter(status='CALLING').count(),
                    'in_progress': active_tokens.filter(status='IN_PROGRESS').count(),
                    'completed_today': completed_tokens.count()
                }
            }
            
            return queue_data
        except HospitalProfile.DoesNotExist:
            return {'error': 'Hospital not found'}
    
    @database_sync_to_async
    def get_token(self, token_id):
        """Get token by ID."""
        try:
            return QueueToken.objects.get(id=token_id)
        except QueueToken.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_token(self, token, new_status):
        """Update token status."""
        token.status = new_status
        
        if new_status == 'CALLING':
            token.called_at = timezone.now()
        elif new_status == 'COMPLETED':
            token.completed_at = timezone.now()
        
        token.save()

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'video_call_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        event_type = message.get('type')

        # Forward the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'forward_message',
                'message': message
            }
        )

    async def forward_message(self, event):
        # Don't send the message back to the original sender
        if self.channel_name != self.channel_layer.channels.get(event['message'].get('sender_channel_name')):
            await self.send(text_data=json.dumps(event['message']))
