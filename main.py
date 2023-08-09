import json
import smartsheet
import requests

smartsheet_client = smartsheet.Smartsheet()

function_call_settings = [
    {'scopeObjectId': 3726089754988420,  'function_to_call': "add_to_group_demo", 'field': '?email='},
    {'scopeObjectId': 9999999999999999, 'function_to_call': "call_other_fuction", 'field': '?sheet_id='}
    ]
function_url = 'https://us-central1-smartsheet-api-functions.cloudfunctions.net/'

def ss_callback_url(request):
    request_json = request.get_json()
    print('request_json', request_json)

    # for a webhook challenge, return verification
    if request.args and "challenge" in request.args:
        return 'not smartsheet challenge'
    elif request_json and "challenge" in request_json:
        return json.dumps({
            "smartsheetHookResponse": request_json['challenge']
        })

    # if this is a callback
    elif request_json and "scopeObjectId" in request_json:
        sheet_id = request_json["scopeObjectId"]
        print("sheet_id : ", sheet_id)
        for setting in function_call_settings:
            if sheet_id == setting['scopeObjectId']:
                function_to_call = setting['function_to_call']
                print(function_to_call)
                field = setting['field']
                print(field)
        events = request_json["events"]
        for event in events:
            print('---- event -----')
            for key in event.keys():
                if key == 'rowId':
                    rowId = event[key]
                    print(key, rowId)
                if key == 'columnId':
                    columnId = event[key]
                    print(key, columnId)
        if sheet_id and rowId and columnId:
            # Get the specific row
            row = smartsheet_client.Sheets.get_row(sheet_id, rowId)
            # Extract the cell value directly based on the column ID
            cell = next((c for c in row.cells if c.column_id == columnId), None)
            if cell:
                print(f"Cell value: {cell.value}")
                print(f"Cell display_value: {cell.display_value}")
                # URL of the calleeFunction (replace with your function's URL)
                url = function_url + function_to_call + field + cell.display_value
                print(url)
                response = requests.get(url)
                if response.status_code == 200:
                    return f'CallerFunction received: {response.text}'
                else:
                    return f'Error: {response.status_code}'
            else:
                print(f"No cell found with column_id: {columnId}")
        return json.dumps({
             "callback from smartsheet sheet_idd ": sheet_id
        })
    else:
      	return 'neither smartsheet challenge nor callback'
