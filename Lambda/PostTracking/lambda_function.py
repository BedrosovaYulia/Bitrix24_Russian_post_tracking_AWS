import json
from zeep import Client
from botocore.vendored import requests
from urllib.parse import parse_qs
import os

def lambda_handler(event, context):
    
    url = os.environ['post_url']
    barcode = event['barcode']
    my_login = os.environ['login']
    my_password = os.environ['password']
    
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
    #Send data to the B24:
    data = {
            "user_id": 1,
            "message": barcode+' '+info+'\n '+FinalStatus
        }

    hook=os.environ['hook']
    response = requests.get(hook,data)
    
    return {
        'statusCode': 200,
    }
