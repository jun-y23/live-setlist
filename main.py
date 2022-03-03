import ast
import csv
import json
import math
import os
import settings
import urllib.request

setlist_api_key = settings.SETLIST_API_KEY

# out csv
# get id from musicbrainz
url = 'https://api.setlist.fm/rest/1.0/artist/e6e879c0-3d56-4f12-b3c5-3ce459661a8e/setlists'
# musicbrainz ID
artist_mbid = '03ad1736-b7c9-412a-b442-82536d63a5c4'
artist_name = 'elliottsmith'

headers ={
        'Accept': 'application/json',
        'X-API-Key': setlist_api_key
}

target_props = ['eventDate', 'url']
target_list = []

def main():
    fetch_all_setlist()

    write_csv(target_list)

def fetch_all_setlist() -> None:
    url_with_params = 'https://api.setlist.fm/rest/1.0/artist/{}/setlists'.format(artist_mbid)
    req = urllib.request.Request(url_with_params, headers=headers)

    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read().decode('utf8'))
        itemsPerPage = body['itemsPerPage']
        total = body['total']
        max_page_num = calcu_max_page_num(total, itemsPerPage)
        dict_setlists = body['setlist']
        for setlist in dict_setlists:
            object_to_flat_array(setlist)

    for page_num in range(2, max_page_num):
        print(page_num)
        url_with_params = 'https://api.setlist.fm/rest/1.0/artist/{}/setlists?p={}'.format(artist_mbid, page_num)
        req = urllib.request.Request(url_with_params, headers=headers)

        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode('utf8'))
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
                if 'city' in value:
                    if 'name' in value['city']:
                        item_array.append(value['city']['name'])
                    if 'name' in value['city']['country']:
                        item_array.append(value['city']['country']['name'])
        else:
            print(value)
    target_list.append(item_array)

def calcu_max_page_num(total:int, itemPerPage:int) -> int:
    return math.ceil(total / itemPerPage)

csv_columns = ['date', 'venue', 'city', 'country', 'uri']
filename = 'setlists_{}.csv'.format(artist_name)

def write_csv(list):
    try:
        with open(filename, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(csv_columns)
            w.writerows(list)
        f.close()
    except IOError:
        print("I/O error")

if __name__ == "__main__":
    main()
