import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from accidentes.shared.utils import ok_response, error_response, unauthorized_response
from accidentes.shared.permissions import USUARIOS_ROLES

logger = logging.getLogger(__name__)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('usuario', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return error_response('Usuario y contraseña requeridos')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return unauthorized_response()

        if not check_password(password, user.password):
            return unauthorized_response()

        refresh = RefreshToken.for_user(user)
        perfil = USUARIOS_ROLES.get(username, {'nombre': 'Operador', 'rol': 'Operador'})

        return ok_response({
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
            return error_response('Refresh token requerido')
        try:
            token = RefreshToken(refresh_token)
            return ok_response({'access': str(token.access_token)})
        except Exception as exc:
            logger.warning('Refresh token inválido: %s', exc)
            return unauthorized_response('Token inválido o expirado')


class VerifyTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        perfil = USUARIOS_ROLES.get(user.username, {'nombre': 'Operador', 'rol': 'Operador'})
        return ok_response({
            'usuario': user.username,
            'nombre': perfil['nombre'],
            'rol': perfil['rol'],
        })
