import requests, json, os


def GetToken(username, password):
    token_url = os.getenv("<ENDPOINT URL>")
    token_headers = {
        "Accept": "application/json",
        "content-type": "application/x-www-form-token_urlencoded",
    }
    token_payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    auth = requests.post(token_url, data=token_payload, headers=token_headers)
    if auth.status_code == 200 and "An error has occurred" not in auth.text:
        authresponse = json.loads(auth.text)
        token = authresponse["access_token"]
        return token
    elif auth.status_code != 200:
        print(
            " Error retrieving token",
            "Status Code: " + str(auth.status_code),
            "Details: " + str(auth.text),
            sep="\n",
        )
        exit()
    else:
        print(
            " Error retrieveing token: Authentication provided is either incorrect or not supplied, consider reviewing.",
            "Status Code: " + str(auth.status_code),
            "Details: " + str(auth.content),
            sep="\n",
        )
        exit()


def GetSecret(token, tokenID):
    headers = {"Authorization": "Bearer " + token, "content-type": "application/json"}
    secrequest = requests.get("<ENDPOINT URL>" + str(tokenID), headers=headers)
    secresponse = json.loads(secrequest.text)
    if secrequest.status_code == 200:
        data_dict = {
            "name": "",
            "user": "",
            "pass": "",
            "location": "",
            "notes": [],
            "tenantid": "",
            "clientid": "",
            "clientsecret": "",
        }
        data_dict["name"] = secresponse["name"]
        for item in secresponse["items"]:
            try:
                if item["fieldName"] == "Username":
                    data_dict["user"] = item["itemValue"]
                if item["fieldName"] == "Password":
                    data_dict["pass"] = item["itemValue"]
                if item["fieldName"] == "Location":
                    data_dict["location"] = item["itemValue"]
                if item["fieldName"] == "Notes":
                    data_dict["notes"] = item["itemValue"]
                if item["fieldName"] == "Directory (tenant) ID":
                    data_dict["tenantid"] = item["itemValue"]
                if item["fieldName"] == "Application (client) ID":
                    data_dict["clientid"] = item["itemValue"]
                if item["fieldName"] == "Client Secret":
                    data_dict["clientsecret"] = item["itemValue"]
            except Exception:
                pass
        return data_dict
    else:
        print(
            "Error retrieving secret!!!!",
            "Token ID: " + str(tokenID),
            "Status Code: " + str(secrequest.status_code),
            "Response: " + secrequest.text,
            sep="\n",
        )


def UpdateSecret(server_url, token, tokenID, new_secret_value):
    update_url = f"{server_url}/Secrets/{tokenID}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    updated_secret_data = {
        "SecretId": secret_id,
        "Items": [{"FieldName": "Password", "Value": new_secret_value}],
    }
    updated_secret_json = json.dumps(updated_secret_data)
    response = requests.put(update_url, headers=headers, data=updated_secret_json)
    if response.status_code == 200:
        print("Secret updated successfully")
    else:
        print(f"Failed to update secret. Status code: {response.status_code}")
        print(response.text)
