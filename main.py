import gspread
from oauth2client.service_account import ServiceAccountCredentials
import settings
import urllib.request
import os
import json
import math
import ast
import sys
sys.setrecursionlimit(10000)

SETLIST_API_KEY = settings.SETLIST_API_KEY
api_scope = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']

# get Credentials
credentials_path = os.path.join(os.path.expanduser('~'),'Downloads/sample-data-309705-d2a4f513fd15.json')
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, api_scope)

# get client
gspread_client = gspread.authorize(credentials)
spread_sheet_name = "jeff"

sheet = gspread_client.open_by_key('1Ddrzu4LpVRaSwO8vECcbEjlXjL5fxEtQfxPG9gMLNnE')
ss = sheet.worksheet('jeff')

url = f'https://api.setlist.fm/rest/1.0/artist/e6e879c0-3d56-4f12-b3c5-3ce459661a8e/setlists'
headers ={
        'Accept': 'application/json',
        'X-API-Key': SETLIST_API_KEY
}

colnames = ['eventDate','url','venueName','cityName','CountryName']
target_props = ['eventDate', 'url']
target_list = []

def main():
    fetch_all_setlist()

    last_row =len(target_list)
    ss.update('A1:B{}'.format(last_row), target_list)

def fetch_all_setlist() -> None:
    max_page_num =15
    for page_num in range(1, 15):
        url_with_params = f'https://api.setlist.fm/rest/1.0/artist/e6e879c0-3d56-4f12-b3c5-3ce459661a8e/setlists?p={page_num}'
        req = urllib.request.Request(url_with_params, headers=headers)

        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode('utf8'))
            print(page_num)
            if page_num == 1:
                itemsPerPage = body['itemsPerPage']
                total = body['total']
                max_page_num = calcu_max_page_num(total, itemsPerPage)
            dict_setlists = body['setlist']
            for setlist in dict_setlists:
                object_to_flat_array(setlist)

def object_to_flat_array(target:dict) -> None:
    item_array = []
    for key, value in target.items():
        if isinstance(value, str):
            if key in target_props:
                item_array.append(value)
        elif isinstance(value, dict):
            if key == 'venue':
                item_array.append(value['name'])
                item_array.append(value['city']['name'])
                item_array.append(value['city']['country']['name'])
        else:
            print(value)
    target_list.append(item_array)

def calcu_max_page_num(total:int, itemPerPage:int) -> int:
    return math.ceil(total / itemPerPage)

main()
