from rest_framework.response import Response
from rest_framework import status as http_status


def ok_response(data, status=http_status.HTTP_200_OK):
    return Response(data, status=status)


def error_response(mensaje, codigo="ERROR", status=http_status.HTTP_400_BAD_REQUEST):
    return Response({'error': mensaje, 'codigo': codigo}, status=status)


def validation_error_response(errors, status=http_status.HTTP_400_BAD_REQUEST):
    return Response({'errores': errors, 'codigo': 'VALIDACION_FALLIDA'}, status=status)


def not_found_response(mensaje="No encontrado"):
    return error_response(mensaje, "NO_ENCONTRADO", http_status.HTTP_404_NOT_FOUND)


def server_error_response(mensaje="Error interno"):
    return error_response(mensaje, "ERROR_INTERNO", http_status.HTTP_500_INTERNAL_SERVER_ERROR)


def unauthorized_response(mensaje="Credenciales inválidas"):
    return error_response(mensaje, "NO_AUTORIZADO", http_status.HTTP_401_UNAUTHORIZED)
