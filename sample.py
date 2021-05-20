import gspread
from oauth2client.service_account import ServiceAccountCredentials
import settings
import urllib.request
import os
import json
import math
import ast

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
maxPageNum = 2

colnames = ['eventDate','url','venueName','cityName','CountryName']
target_props = ['eventDate', 'url']
target_list = []

def main():
    # fetch_first_page_setlist()
    fetch_all_setlist()

    last_row =len(target_list)
    ss.update('A1:B{}'.format(last_row), target_list)

def calcu_max_page_num(total:int, itemPerPage:int) -> int:
    return math.ceil(total / itemPerPage)

def fetch_first_page_setlist():
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        body = res.read()
        dict_str = body.decode("UTF-8")
        dict_body = ast.literal_eval(dict_str)
        dict_setlists = dict_body["setlist"]
        for setlist in dict_setlists:
            object_to_flat_array(setlist)

def fetch_all_setlist():
    for page_num in range(1, max_page_num):
        url_with_params = f'https://api.setlist.fm/rest/1.0/artist/e6e879c0-3d56-4f12-b3c5-3ce459661a8e/setlists?p={page_num}'
        req = urllib.request.Request(url_with_params, headers=headers)

        with urllib.request.urlopen(req) as res:
            body = res.read()
            dict_str = body.decode("UTF-8")
            dict_body = ast.literal_eval(dict_str)
            if page_num == 1:
                itemsPerPage = dict_body["itemsPerPage"]
                total = dict_body["total"]
                max_page_num = calcu_max_page_num(total, itemsPerPage)
            dict_setlists = dict_body["setlist"]
            for setlist in dict_setlists:
                object_to_flat_array(setlist)

def object_to_flat_array(target:dict) -> None:
    item_array = []
    for key, value in target.items():
        if isinstance(key, str):
            if key == "eventDate" or key == "url":
                item_array.append(value)
        elif isinstance(target, dict):
            object_to_flat_array(target)
        else:
    target_list.append(item_array)
