from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpRequest
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAdminUser
from typing import Optional
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers
import logging

@extend_schema(
    description="Registra um novo usuário no sistema.",
    methods=['POST'],
    request=inline_serializer(
        name='RegisterUser',
        fields={
            'username': serializers.CharField(),
            'password': serializers.CharField(),
        }
    ),
    responses={
        201: inline_serializer(
            name="RegisterUserResponse",
            fields={
                "refresh": serializers.CharField(),
                "access": serializers.CharField(),
            },
        ),
        400: OpenApiResponse(description="Erro na requisição."),
    },
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def register_user(request: HttpRequest) -> Optional[Response]:
    """
    Registra um novo usuário no sistema.

    Este endpoint aceita uma requisição POST com os dados do usuário a ser registrado. Os dados esperados são 'username' e 'password'. Se os dados estiverem ausentes ou o nome de usuário já estiver em uso, uma mensagem de erro apropriada será retornada. Caso contrário, um novo usuário será criado e tokens de acesso e atualização serão gerados e retornados.

    Args:
        request (HttpRequest): O objeto de requisição HTTP, esperando um método POST com 'username' e 'password' no corpo da requisição.

    Returns:
        Response: Um objeto de resposta HTTP contendo tokens de acesso e atualização se o registro for bem-sucedido, ou uma mensagem de erro se houver problemas com os dados fornecidos.
    """
    try:
        if request.method == 'POST':
            
            username = request.data.get('username')
            password = request.data.get('password')

            if username is None or password is None:
                return Response({'error': 'é necessário informar o "username" e password'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return Response({'error': 'Esse usuário já existe. Escolha outro usuário'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, password=password)
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logging.error(e)
        return Response({"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        