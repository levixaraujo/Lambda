import json  # Importa a biblioteca JSON, que pode ser usada para trabalhar com dados no formato JSON.
import os  # Importa a biblioteca 'os' para lidar com variáveis de ambiente e operações do sistema.
import boto3  # Importa a biblioteca boto3, que é usada para interagir com serviços da AWS.
from datetime import datetime  # Importa a classe 'datetime' da biblioteca 'datetime' para lidar com datas e horários.
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

# Função para obter o ARN do tópico SNS da variável de ambiente 'SNSTOPIC_ARN'.
def get_sns_topic_arn():
    try:
        return os.environ.get("SNSTOPIC_ARN")
    except KeyError:
        logging.error("Variável de ambiente 'SNSTOPIC_ARN' não está configurada.")
        return None

# Função para obter volumes EBS não utilizados em uma região AWS específica.
def get_unused_ebs_volumes(region):
    ec2 = boto3.resource('ec2', region_name=region)  # Cria um cliente boto3 para o serviço EC2 na região especificada.
    volumes = ec2.volumes.all()  # Obtém uma lista de todos os volumes EBS na região.
    unused_volumes = [vol for vol in volumes if vol.state == "available"]  # Filtra apenas os volumes em estado "available".
    return unused_volumes  # Retorna a lista de volumes não utilizados.

# Função para enviar um relatório SNS com informações sobre os volumes EBS não utilizados.
def send_sns_report(region, sns_topic_arn, unused_volumes, today):
    if not sns_topic_arn:
        logging.warning("Tópico SNS ARN não configurado. Relatório não enviado.")
        return

    if not unused_volumes:
        logging.info("Nenhum volume EBS não utilizado encontrado. Nenhum relatório será enviado.")
        return

    sns = boto3.client('sns', region_name=region)  # Cria um cliente boto3 para o serviço SNS na região especificada.

    ebs_report = f"The Following EBS Volumes are Unused ({today}):\n"  # Cria um cabeçalho do relatório com a data.
    for vol in unused_volumes:
        ebs_report += f"- {vol.id} - Size: {vol.size} - Created: {vol.create_time.strftime('%Y/%m/%d %H:%M')}\n"  # Adiciona informações de cada volume ao relatório.

    response = sns.publish(
        TargetArn=sns_topic_arn,
        Message=ebs_report,
        Subject=f'Unused EBS Volumes Report: {today}',
        MessageStructure='string'
    )  # Publica o relatório no tópico SNS especificado.

    logging.info("Relatório enviado com sucesso.")  # Registra uma mensagem de sucesso no log.

# Função principal para AWS Lambda que orquestra o processo.
def lambda_handler(event, context):
    region = get_aws_region()  # Obtém a região AWS do ambiente.
    sns_topic_arn = get_sns_topic_arn()  # Obtém o ARN do tópico SNS do ambiente.

    if not region:  # Verifica se a região não foi obtida com sucesso.
        return

    unused_volumes = get_unused_ebs_volumes(region)  # Obtém volumes não utilizados na região.
    today = datetime.now().date()  # Obtém a data atual.

    send_sns_report(region, sns_topic_arn, unused_volumes, today)  # Envia o relatório SNS.

    return  # Retorna o resultado da função Lambda.
