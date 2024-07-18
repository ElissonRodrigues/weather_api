from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Station, RegistrationData
from .serializers import StationSerializer, RegistrationDataSerializer, StationUpdateSerializer
from typing import Optional, Dict, Any, List
import pandas as pd
import statsmodels.api as sm
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.http import HttpRequest
from users.models import User
from warnings import filterwarnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tools.sm_exceptions import ValueWarning
import logging

# ---------------------------- Suprimir avisos específicos ---------------------------- #

filterwarnings("ignore", category=UserWarning, module="statsmodels")
filterwarnings("ignore", category=FutureWarning, module="statsmodels")
filterwarnings("ignore", category=ValueWarning, module="statsmodels")
filterwarnings("ignore", category=ConvergenceWarning, module="statsmodels")

# --------------------------------- Funções auxiliares --------------------------------- #
def is_user_admin(user: User) -> bool:
    """
    Verifica se o usuário é um administrador.

    Esta função determina se um usuário específico tem privilégios de administrador. 
    Um usuário é considerado administrador se estiver autenticado e marcado como 
    membro da equipe administrativa (is_staff).

    Args:
        user (User): O objeto de usuário a ser verificado.

    Returns:
        bool: True se o usuário for um administrador, False caso contrário.
    """
    return user.is_authenticated and user.is_staff


def response_template(data: List[Dict[str, Any]] = None, errors: Dict[str, Any]= None, status: status = status.HTTP_200_OK):
    """
    Cria uma resposta padronizada para as requisições da API.

    Esta função auxiliar é usada para criar respostas HTTP padronizadas em toda a API. 
    Ela aceita dados e mensagens de erro como parâmetros e retorna uma resposta 
    formatada de acordo com esses parâmetros. A presença de erros determina se a 
    resposta é considerada bem-sucedida ou não.

    Args:
        data (dict, optional): Dados a serem incluídos na resposta. Padrão é None, indicando que não há dados a serem retornados.
        errors (dict, optional): Mensagens de erro a serem incluídas na resposta. Padrão é None, indicando que não há erros.
        status (int): O código de status HTTP a ser retornado. Padrão é 200 (OK).

    Returns:
        Response: Uma instância de Response do Django REST Framework contendo os dados ou erros formatados com o código de status HTTP
    """
    response_data = {
        'success': errors is None,#type: ignore
        'data': data if errors is None else [], #type: ignore
        'errors': errors if errors is not None else False, #type: ignore
    }

    
    return Response(response_data, status=status)


# --------------------------------- Estações --------------------------------- #   
@extend_schema(
    description="Esse endpoint permite a listagem de todas as estações cadastradas",
    methods=['GET', 'POST'],
    request=StationSerializer,
    responses={
        200: OpenApiResponse(description="Lista de todas as estações cadastradas", response=StationSerializer),
        400: OpenApiResponse(description="Erro na requisição"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
    },
)
@api_view(["GET"])
def stations(request: HttpRequest) -> Optional[Response]:
    """
    Lista todas as estações disponíveis.

    Este endpoint responde a uma requisição GET retornando uma lista de todas as estações cadastradas no projeto. 
    Cada estação é serializada utilizando o StationSerializer, que converte os objetos da estação 
    em um formato JSON adequado para resposta HTTP.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        Response: Um objeto de resposta HTTP contendo uma lista de todas as estações em formato JSON. Se não houver estações, a lista retornada estará vazia.
    """
    try:
        if request.method == "GET":
            stations = Station.objects.all()
            serializer = StationSerializer(stations, many=True)
            return response_template(data=serializer.data)
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    methods=['GET'],
    description="Lista os dados detalhados da estação por ID",
    responses={
        200: OpenApiResponse(description="Lista os dados detalhados da estação por ID"),
        404: OpenApiResponse(description="Estação não encontrada"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
    }
)
@extend_schema(
    methods=['PUT'],
    description="Atualiza o nome de uma estação específica por ID",
    request=StationUpdateSerializer,
    responses={
        202: OpenApiResponse(description="Estação atualizada com sucesso."),
        400: OpenApiResponse(description="Erro na requisição"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
        403: OpenApiResponse(description="Acesso negado. Apenas administradores podem modificar os dados."),
        404: OpenApiResponse(description="Estação não encontrada"),
    }
)
@extend_schema(
    methods=['DELETE'],
    description="Exclui uma estação específica por ID",
    responses={
        204: OpenApiResponse(description="Estação deletada com sucesso."),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
        403: OpenApiResponse(description="Acesso negado. Apenas administradores podem modificar os dados."),
        404: OpenApiResponse(description="Estação não encontrada"),
    }
)
@api_view(["GET", "PUT", "DELETE"])
def stations_by_id(request: HttpRequest, pk: int) -> Optional[Response]:
    """
    Gerencia as operações GET, PUT e DELETE para uma estação específica.

    Este endpoint permite visualizar os detalhes de uma estação específica (GET), atualizar o nome de 
    uma estação (PUT) ou deletar uma estação (DELETE). A atualização e a exclusão são restritas a usuários administradores.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        pk (int): O ID (chave primária) da estação a ser manipulada.

    Returns:
        Response: Dependendo do método HTTP:
            - GET: Retorna os detalhes da estação, incluindo os últimos dados de registro, se disponíveis.
            - PUT: Atualiza o nome da estação e retorna uma mensagem de sucesso (Usuário administrador é necessário).
            - DELETE: Deleta a estação e retorna uma mensagem de sucesso (Usuário administrador é necessário).
            Se a estação especificada não for encontrada, retorna um erro 404.
            Se o método PUT ou DELETE é chamado por um usuário não administrador, retorna um erro 403.
    """
    try:
        if request.method in ["PUT", "DELETE"] and not is_user_admin(request.user):
            return response_template(errors={"message": "Acesso negado! apenas adminstradores podem modificar esses dados."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            station = Station.objects.get(pk=pk)
        except Station.DoesNotExist:
            return response_template(errors={"message": "Estação não encontrada, verifique o ID da estação"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            station_serializer = StationSerializer(station)
            response_data = station_serializer.data
            
            return response_template(data=response_data, status=status.HTTP_200_OK)

        elif request.method == "PUT":
            data_value = ['station_name', 'city', 'owner', 'latitude', 'longitude', 'uf']

            if not any(field in request.data for field in data_value):
                return response_template(errors={"message": "é necessário informar pelo menos um campo para a atualização."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = StationUpdateSerializer(station, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_fields = ', '.join(serializer.validated_data.keys())
                return response_template(data={"message": f"{updated_fields} foram atualizados na estação {pk}"}, status=status.HTTP_202_ACCEPTED)
        
            else:
                return response_template(errors=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                #return response_template(errors={"message": "é necessário informar pelo menos um campo para a atualização."}, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == "DELETE":
            station.delete()
            return response_template(data={"message": "Estação deletada com sucesso."}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    description="Cria uma nova estação com os dados fornecidos.",
    request=StationSerializer,
    responses={
        201: StationSerializer,
        400: OpenApiResponse(description="Erro na requisição"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
    }
)
@api_view(["POST"])
def station_create(request: HttpRequest) -> Optional[Response]:
    """
    Cria uma nova estação com os dados fornecidos.

    Este endpoint aceita uma requisição POST com os dados da estação a ser criada. 
    Utiliza o serializer StationSerializer para validar . 

    Args:
        request (HttpRequest): O objeto de requisição HTTP

    Returns:
        Response: Um objeto de resposta HTTP. Se a criação for bem-sucedida, retorna os dados da estação 
        criada e um status HTTP 201. Se a validação falhar, retorna uma mensagem de erro e um status HTTP 400.
    """
    try:
        if request.method == "POST":
            serializer = StationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return response_template(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                erros = ', '.join(serializer.errors.keys())

                return response_template(errors={"message": f"Erro ao criar a estação. Campos obrigatórios: [{erros}]"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------- Dados históricos --------------------------------- #
@extend_schema(
    description="Recupera e retorna os dados históricos de registro para todas as estações.",
    methods=['GET'],
    responses={200: RegistrationDataSerializer(many=True)}
)
@api_view(["GET"])
def historical_data(request: HttpRequest) -> Optional[Response]:
    """
    Recupera e retorna os dados históricos de registro para todas as estações.

    Este endpoint busca todos os dados de registro associados a todas as estações e retorna esses dados em formato serializado.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.

    Returns:
        Response: Um objeto de resposta HTTP contendo os dados históricos de registro de todas as estações em formato serializado.
    """
    try:
        data = RegistrationData.objects.all()
        serializer = RegistrationDataSerializer(data, many=True)
        return response_template(data=serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    description="Recupera e retorna os dados históricos de registro para uma estação específica.",
    methods=['GET'],
    responses={
        200: RegistrationDataSerializer(many=True),
        404: OpenApiResponse(description="Estação não encontrada"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
    }
)
@api_view(["GET"])
def historical_data_by_id(request: HttpRequest, pk: int) -> Optional[Response]:
    """
    Recupera e retorna os dados históricos de registro para uma estação específica.

    Este endpoint busca todos os dados de registro associados a uma estação específica, identificada 
    pelo seu ID (chave primária). Se a estação não for encontrada, retorna um erro 404. Caso contrário, 
    retorna os dados de registro em formato serializado.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        pk (int): O ID (chave primária) da estação onde os dados históricos de registro são solicitados.

    Returns:
        Response: Um objeto resposta HTTP contendo os dados históricos de registro da estação em formato serializado, 
        se a estação for encontrada. Caso contrário, retorna uma mensagem de erro indicando que a estação não foi encontrada.
    """
    try:
        try:
            Station.objects.get(pk=pk)
        except Station.DoesNotExist:
            return response_template(errors={"message": "Estação não encontrada, verifique o ID da estação"}, status=status.HTTP_404_NOT_FOUND)

        data = RegistrationData.objects.filter(station_id=pk)
        serializer = RegistrationDataSerializer(data, many=True)
        return response_template(data=serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------------------- Análise e Previsão --------------------------------- #
@extend_schema(
    description="Realiza uma previsão de 7 dias dados especificos da uma estação.",
    methods=['GET'],
    responses={
        200: OpenApiResponse(description="Previsão de temperatura para os próximos 7 dias"),
        404: OpenApiResponse(description="Estação não encontrada ou sem dados para a analise"),
        400: OpenApiResponse(description="Erro na requisição"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
    },
)
@api_view(["GET"])
def predict(request: HttpRequest, pk: int) -> Optional[Response]:
    """
    Realiza uma previsão de 7 dias para vários parâmetros de uma estação específica.

    Este endpoint busca os dados de registro de uma estação específica pelo seu ID (chave primária) 
    e utiliza um modelo ARIMA para fazer uma previsão de 7 dias para vários parâmetros, incluindo 
    temperatura, voltagem da bateria, nível da régua e precipitação.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        pk (int): O ID (chave primária) da estação para a qual a previsão será realizada.

    Returns:
        Response: Um objeto de resposta HTTP contendo a previsão dos parâmetros para os próximos 7 dias, 
        incluindo o valor previsto, o erro padrão e o intervalo de confiança para cada dia, ou uma mensagem 
        de erro se a estação especificada não for encontrada ou se houver dados faltantes.
    """
    try:
        try:
            Station.objects.get(pk=pk)
        except Station.DoesNotExist:
            return response_template(errors={"message": "Estação não encontrada, verifique o ID da estação"}, status=status.HTTP_404_NOT_FOUND)

        data = RegistrationData.objects.filter(station_id=pk)
        serializer = RegistrationDataSerializer(data, many=True)

        if serializer.data:
            df = pd.DataFrame(serializer.data)
            df['data'] = pd.to_datetime(df['DataHora_GMT'])
            df.set_index('data', inplace=True)

            previsoes = {}

            # Função auxiliar para fazer previsão
            def fazer_previsao(serie, nome): #type: ignore
                ts = serie.astype(float).dropna()
                if ts.empty:
                    return None
                model = sm.tsa.ARIMA(ts, order=(5, 1, 0))
                results = model.fit()
                forecast = results.get_forecast(steps=7)
                previsao = forecast.predicted_mean
                erro_padrao = forecast.se_mean
                intervalo_confianca = forecast.conf_int(alpha=0.05)
                return {
                    'previsao': [round(val, 2) for val in previsao],
                    'erro_padrao': [round(val, 4) for val in erro_padrao],
                    'intervalo_confianca': {
                        'limite_inferior': [round(val, 2) for val in intervalo_confianca.iloc[:, 0]],
                        'limite_superior': [round(val, 2) for val in intervalo_confianca.iloc[:, 1]]
                    }
                }

            # Verificar e fazer previsões para cada campo
            campos = ['TempAr_C', 'Bateria_volts', 'NivRegua_m', 'Pluvio_mm']
            for campo in campos:
                if df[campo].isnull().sum() == 0:
                    previsoes[campo] = fazer_previsao(df[campo], campo)

            if not previsoes:
                return response_template(errors={'mensagem': 'Não há dados suficientes para fazer previsões.'}, status=status.HTTP_400_BAD_REQUEST)

            return response_template(data={
                'mensagem': 'Previsão para os próximos 7 dias.',
                'dados': previsoes
            }, status=status.HTTP_200_OK)
        
        else:
            return response_template(errors={"message": "Sem dados históricos para analisar. Tente novamente com outro ID"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@extend_schema(
    description="Realiza uma análise estatística dos dados de uma estação específica.",
    methods=['GET'],
    responses={
        200: OpenApiResponse(description="Análise estatística dos dados"),
        404: OpenApiResponse(description="Estação não encontrada ou sem dados para a analise"),
        401: OpenApiResponse(description="Não autorizado - Autenticação falhou ou não foi fornecida"),
    },
)
@api_view(["GET"])
def analyze(request: HttpRequest, pk: int) -> Optional[Response]:
    """
    Realiza uma análise estatística detalhada dos dados de uma estação específica.

    Este endpoint busca todos os registros de dados associados a uma estação pelo seu ID (chave primária) e realiza uma análise estatística descritiva detalhada desses dados, focando nos campos 'Pluvio_mm', 'NivRegua_m' e 'Bateria_volts'.

    Args:
        request (HttpRequest): O objeto de requisição HTTP.
        pk (int): O ID (chave primária) da estação cujos dados serão analisados.

    Returns:
        Response: 
            200: Um objeto de resposta HTTP contendo um dicionário com os resultados da análise estatística ou uma mensagem de erro se a estação especificada não for encontrada.
            500: Erro interno no servidor.
    """  
    try:  
        try:
            Station.objects.get(pk=pk)
        except Station.DoesNotExist:
            return response_template(errors={"message": "Estação não encontrada, verifique o ID da estação"}, status=status.HTTP_404_NOT_FOUND)

        data = RegistrationData.objects.filter(station_id=pk)
        serializer = RegistrationDataSerializer(data, many=True)

        if serializer.data:
            df = pd.DataFrame(serializer.data)
            if df.empty:
                return response_template(errors={"message": "Sem dados históricos para analisar. Tente novamente com outro ID"}, status=status.HTTP_404_NOT_FOUND)

            campos_interesse = ['Pluvio_mm', 'NivRegua_m', 'Bateria_volts']
            
            df[campos_interesse] = df[campos_interesse].apply(pd.to_numeric, errors='coerce')

            # Estatísticas descritivas básicas
            analysis_result = df[campos_interesse].describe().to_dict()

            # Estatísticas adicionais
            analysis_result['mediana'] = df[campos_interesse].median().to_dict()
            analysis_result['valor_mais_frequente'] = df[campos_interesse].mode().iloc[0].to_dict()  
            analysis_result['quantis '] = df[campos_interesse].quantile([0.25, 0.5, 0.75]).to_dict()
            analysis_result['variancia'] = df[campos_interesse].var().to_dict()
            analysis_result['desvio_padrao'] = df[campos_interesse].std().to_dict()
            analysis_result['assimetria'] = df[campos_interesse].skew().to_dict()
            analysis_result['curtose'] = df[campos_interesse].kurtosis().to_dict()
            analysis_result['contagem_nao_nulos'] = df[campos_interesse].count().to_dict()

            return response_template(data=analysis_result, status=status.HTTP_200_OK)
        else:
            return response_template(errors={"message": "Sem dados históricos para analisar. Tente novamente com outro ID"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return response_template(errors={"message": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)