import json
from zeep import Client
from botocore.vendored import requests
from urllib.parse import parse_qs

def lambda_handler(event, context):
    
    url = 'https://tracking.russianpost.ru/rtm34?wsdl'
    barcode = event['barcode']
    my_login = '************'
    my_password = '************'
    
    client = Client(url)
    
    OperationHistoryRequest= {
        "Barcode":barcode,
        "MessageType":0,
        "Language":"RUS"
        }
                
    AuthorizationHeader= {
        "login":my_login,
        "password":my_password
        }
        
    with client.settings(strict=False):       
        result = client.service.getOperationHistory(OperationHistoryRequest,AuthorizationHeader)
    
    info='\n'
    FinalStatus=''
    
    for item in result:
        try:
            info=info+' '+str(item['OperationParameters']['OperDate'])[:10]+' '
        except:
            pass
        
        try:
            info=info+' '+str(item['AddressParameters']['OperationAddress']['Index'])+' '
        except:
            pass
        
        try:
            info=info+' '+str(item['OperationParameters']['OperAttr']['Name'])+' '
        except:
            pass
        
        try:
            FinalStatus=str(item['OperationParameters']['OperAttr']['Name'])
        except:
            pass
        
        info=info+'\n'
    
    #print(info)
    #Отправляем результат в Битрикс24:
    data = {
            "user_id": 1,
            "message": barcode+' '+info+'\n '+FinalStatus
        }

    response = requests.get('https://bedrosova.bitrix24.ru/rest/1/*****************/im.message.add.json',data)
    
    return {
        'statusCode': 200,
    }
