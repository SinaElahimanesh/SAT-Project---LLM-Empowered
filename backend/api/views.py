from datetime import timezone
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Message
from .serializers import UserSerializer, MessageSerializer
from .bot.utils import StateMachine
from rest_framework.decorators import api_view, permission_classes
from .bot.Memory.LLM_Memory import MemoryManager
from .bot.simple_bot import simple_bot_response

import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .bot.ASR.ASRPipeline import feed_audio_to_ASR_modal

import random

# Create shared instances at module level
state_machine = StateMachine()
memory_manager = MemoryManager()

class RegisterView(APIView):
    def post(self, request):
        data = request.data.copy()
        # Assign group if not provided
        if 'group' not in data:
            data['group'] = random.choice(['control', 'intervention'])
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # Return group in response
            response_data = serializer.data
            response_data['group'] = user.group
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'group': user.group,
            })
        return Response({"error": "Invalid credentials"}, status=400)

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def keep_only_numbers(self, s):
        if s is None:
            return None
        return ''.join(char for char in s if char.isdigit())

    def post(self, request):
        # user = request.user
        text = request.data.get('text')
        user = request.user
        print(user)
        # latest_message = Message.objects.filter(user=user).order_by('-timestamp').first()
        # session_id = latest_message.session_id if latest_message and (timezone.now() - latest_message.timestamp).seconds < 300 else (latest_message.session_id + 1 if latest_message else 1)
        
        # Save message
        # message = Message.objects.create(user=user, text=text, session_id=session_id)

        # State machine logic using shared instance
        response_text, recommendations, state, explainibility, excercise_number = state_machine.execute_state(text, user)
        excercise_number = self.keep_only_numbers(excercise_number)

        return Response({"response": response_text, "recommendations":recommendations, "state": state, "explainibility": explainibility, "excercise_number": excercise_number}, status=200)

class SimpleBotView(APIView):
    def post(self, request):
        history = request.data.get('history', [])
        text = request.data.get('text')
        response_text, recommendations, updated_history = simple_bot_response(history, text)
        return Response({
            "response": response_text,
            "recommendations": recommendations,
            "history": updated_history
        }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    history = memory_manager.get_chat_history(request.user)
    return Response({
        'messages': [
            {
                'text': msg.text,
                'is_user': msg.is_user,
                'timestamp': msg.timestamp
            } for msg in history
        ]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_memory(request):
    memory = memory_manager.get_current_memory(request.user)
    return Response({'memory': memory})

# @api_view(['POST'])
# def add_message(request):
#     # Add user message
#     memory_manager.add_message(
#         user=request.user,
#         text=request.data['message'],
#         is_user=True
#     )
    
#     # Add LLM response (you'll need to generate this)
#     llm_response = "Your LLM response here"
#     memory_manager.add_message(
#         user=request.user,
#         text=llm_response,
#         is_user=False
#     )
    
#     return Response({'response': llm_response})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request):
    """Handle browser close or explicit session end"""
    state_machine.handle_session_end(request.user)
    return Response({'status': 'success'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_audio_message(request):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        file_path = default_storage.save("temp_audio.wav", ContentFile(audio_file.read()))
        audio_path = default_storage.path(file_path)
        result = feed_audio_to_ASR_modal(audio_path)
        os.remove(audio_path)  # Cleanup
        return JsonResponse({"transcription": result})
