import json  # Importa a biblioteca JSON, que pode ser usada para trabalhar com dados no formato JSON.
import os  # Importa a biblioteca 'os' para lidar com variáveis de ambiente e operações do sistema.
import boto3  # Importa a biblioteca boto3, que é usada para interagir com serviços da AWS.
import logging  # Importa a biblioteca de logging para registrar mensagens informativas e de erro.

# Configuração de logging
logging.basicConfig(level=logging.INFO)  # Configura o nível de logging para INFO (mensagens informativas).

# A seguir, temos uma série de funções definidas no código:

# Função para obter a região AWS atual da variável de ambiente 'AWS_REGION'.
def get_aws_region():
    try:
        return os.environ['AWS_REGION']
    except KeyError:
        logging.error("Variável de ambiente 'AWS_REGION' não está configurada.")
        return None

# Função para validar quais EBS entrarão na validação de AVAILABLE
def has_ebs_validator_available_tag(volume):
    if volume.tags is None:
        return False
    
    for tag in volume.tags:
        if tag['Key'].upper() == 'EBSVALIDATORAVAILABLE' and tag['Value'].upper() == 'FALSE':
            return True
    return False

# Função para obter volumes EBS não utilizados em uma região AWS específica.
def get_unused_ebs_volumes(region):
    ec2 = boto3.resource('ec2', region_name=region)  # Cria um cliente boto3 para o serviço EC2 na região especificada.
    volumes = ec2.volumes.all()  # Obtém uma lista de todos os volumes EBS na região.
    unused_volumes = [vol for vol in volumes if vol.state == "available" and not has_ebs_validator_available_tag(vol)]  # Filtra apenas os volumes em estado "available" e que não tem a tag EBSVALIDATORAVAILABLE=FALSE.
    return unused_volumes  # Retorna a lista de volumes não utilizados.

# Função principal para AWS Lambda que orquestra o processo.
def lambda_handler(event, context):
    region = get_aws_region()  # Obtém a região AWS do ambiente.

    if not region:  # Verifica se a região não foi obtida com sucesso.
        return

    unused_volumes = get_unused_ebs_volumes(region)  # Obtém volumes não utilizados na região.
    if unused_volumes:
        print(f'[ALERT] VOLUMES AVAILABLE') 
        print(unused_volumes)
    else:
        print(f'NO VOLUMES ARE AVAILABLE')
        

    return  # Retorna o resultado da função Lambda.
