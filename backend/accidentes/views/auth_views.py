import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

USUARIOS_ROLES = {
    'operador_sga': {'nombre': 'Laura Mendoza', 'rol': 'Operador'},
    'admin_sga': {'nombre': 'Carlos Gomez', 'rol': 'Administrador'},
    'analista_sga': {'nombre': 'Patricia Vega', 'rol': 'Consumidor Analítico'},
    'despachador_sga': {'nombre': 'David Torres', 'rol': 'Despachador'},
}


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('usuario', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Usuario y contraseña requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, user.password):
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        perfil = USUARIOS_ROLES.get(username, {'nombre': 'Operador', 'rol': 'Operador'})

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': username,
            'nombre': perfil['nombre'],
            'rol': perfil['rol'],
        })


class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh', '').strip()
        if not refresh_token:
            return Response({'error': 'Refresh token requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            return Response({'access': str(token.access_token)})
        except Exception as exc:
            logger.warning('Refresh token invÃ¡lido: %s', exc)
            return Response({'error': 'Token invÃ¡lido o expirado'}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        perfil = USUARIOS_ROLES.get(user.username, {'nombre': 'Operador', 'rol': 'Operador'})
        return Response({
            'usuario': user.username,
            'nombre': perfil['nombre'],
            'rol': perfil['rol'],
        })
