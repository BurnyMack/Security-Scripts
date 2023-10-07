import requests, json

class TSS:

    def GetToken(username, password):
        token_url = 'INSERTSSSURLHERE'
        token_headers = {'Accept':'application/json',
                        'content-type':'application/x-www-form-token_urlencoded'}
        token_payload = {'username':username,
                        'password':password, 
                        'grant_type':'password'}
        auth = requests.post(token_url, data=token_payload, headers=token_headers)
        if auth.status_code == 200  and 'An error has occurred' not in auth.text:
            authresponse = json.loads(auth.text)
            token = authresponse['access_token']
            return token
        elif auth.status_code != 200:
            print(' Error retrieving token', 'Status Code: '+str(auth.status_code), 'Details: '+str(auth.text), sep='\n')
            exit()
        else:
            print(' Error retrieveing token: Authentication provided is either incorrect or not supplied, consider reviewing.','Status Code: '+str(auth.status_code), 'Details: '+str(auth.content), sep='\n')
            exit()

    def GetSecret(token,tokenID):
        headers = {'Authorization':'Bearer '+ token, 'content-type':'application/json'}
        secrequest = requests.get ('INSERTSSSURLHERE' + str(tokenID), headers=headers)
        secresponse =json.loads(secrequest.text)
        if secrequest.status_code == 200:
            data_dict = {'name':'', 'user':'', 'pass':'', 'location':'', 'notes': [],
                            'tenantid':'', 'clientid':'', 'clientsecret':''}
            data_dict['name'] = secresponse['name']
            for item in secresponse['items']:
                try:
                    if item['fieldName'] == 'Username':
                        data_dict['user'] = item['itemValue']
                    if item['fieldName'] == 'Password':
                        data_dict['pass'] = item['itemValue']
                    if item['fieldName'] == 'Location':
                        data_dict['location'] = item['itemValue']
                    if item['fieldName'] == 'Notes':
                        data_dict['notes'] = item['itemValue']
                    if item['fieldName'] == 'Directory (tenant) ID':
                        data_dict['tenantid'] = item['itemValue']
                    if item['fieldName'] == 'Application (client) ID':
                        data_dict['clientid'] = item['itemValue']
                    if item['fieldName'] == 'Client Secret':
                        data_dict['clientsecret'] = item['itemValue']
                except Exception:
                    pass
            return data_dict
        else:
            print('Error retrieving secret!!!!','Token ID: '+str(tokenID), 'Status Code: '+str(secrequest.status_code), 'Response: '+secrequest.text, sep='\n')