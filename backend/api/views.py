from datetime import timezone
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Message
from .serializers import UserSerializer, MessageSerializer
from .bot.utils import StateMachine

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
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
            })
        return Response({"error": "Invalid credentials"}, status=400)

class MessageView(APIView):
    # permission_classes = [IsAuthenticated]
    state_machine = StateMachine()

    def post(self, request):
        # user = request.user
        text = request.data.get('text')
        # latest_message = Message.objects.filter(user=user).order_by('-timestamp').first()
        # session_id = latest_message.session_id if latest_message and (timezone.now() - latest_message.timestamp).seconds < 300 else (latest_message.session_id + 1 if latest_message else 1)
        
        # Save message
        # message = Message.objects.create(user=user, text=text, session_id=session_id)

        # State machine logic
        response_text = self.state_machine.execute_state(text)

        return Response({"response": response_text}, status=200)
