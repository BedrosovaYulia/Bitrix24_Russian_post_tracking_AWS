import json
from zeep import Client
from botocore.vendored import requests
from urllib.parse import parse_qs

def http_build_query(params, topkey = ''):
  from urllib.parse import quote
 
  if len(params) == 0:
    return ""
 
  result = ""
 
  # is a dictionary?
  if type (params) is dict:
    for key in params.keys():
      newkey = quote (key)
      if topkey != '':
        newkey = topkey + quote('[' + key + ']')
 
      if type(params[key]) is dict:
        result += http_build_query (params[key], newkey)
 
      elif type(params[key]) is list:
        i = 0
        for val in params[key]:
          result += newkey + quote('[' + str(i) + ']') + "=" + quote(str(val)) + "&"
          i = i + 1
 
      # boolean should have special treatment as well
      elif type(params[key]) is bool:
        result += newkey + "=" + quote (str(int(params[key]))) + "&"
 
      # assume string (integers and floats work well)
      else:
        result += newkey + "=" + quote (str(params[key])) + "&"
 
  # remove the last '&'
  if (result) and (topkey == '') and (result[-1] == '&'):
    result = result[:-1]
 
  return result

def lambda_handler(event, context):
    
    ib_id=event['ib_id']
    el_id=event['id']
    
    url = 'https://tracking.russianpost.ru/rtm34?wsdl'
    barcode = event['barcode']
    my_login = '*************'
    my_password = '**************'
    
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
            info=info+' '+str(item['OperationParameters']['OperType']['Name'])+' '+str(item['OperationParameters']['OperAttr']['Name'])+' '
        except:
            pass
        
        try:
            FinalStatus=str(item['OperationParameters']['OperType']['Name'])+' '+str(item['OperationParameters']['OperAttr']['Name'])
        except:
            pass
        
        #print(item['OperationParameters'])
        
        info=info+'\n'
        
    #Отправляем результат в Битрикс24:
    data = {
            "user_id": 1,
            "message": barcode+' '+info+'\n '+FinalStatus
        }

    response = requests.get('https://bedrosova.bitrix24.ru/rest/1/**************/im.message.add.json',data)
    
    data={
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': ib_id,
        'ELEMENT_ID': el_id,
    }
    
    response = requests.get('https://bedrosova.bitrix24.ru/rest/1/****************/lists.element.get',data)
    list_data=response.json()
    
    print(list_data['result'][0])
    
    fields={
        "NAME":list_data['result'][0]['NAME']
    }
    
    for k in list_data['result'][0]:
        if(k.startswith('PROPERTY')):
            for k2 in list_data['result'][0][k]:
                fields[k]=list_data['result'][0][k][k2]
    
    fields['PROPERTY_447']=FinalStatus
    
    print(fields)
    
    data={
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': ib_id,
        'ELEMENT_ID': el_id,
        'FIELDS':fields
    }
    
    response = requests.get('https://bedrosova.bitrix24.ru/rest/1/****************/lists.element.update',http_build_query(data))
    result=response.json()
    #print(result)
    
    return {
        'statusCode': 200
    }