import json
import urllib.request
import requests
import re

ANKI_CONNECT_URL = 'http://localhost:8765'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    request_json = json.dumps(request(action, **params)).encode('utf-8')
    res = json.load(urllib.request.urlopen(urllib.request.Request(ANKI_CONNECT_URL, request_json)))
    if len(res) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in res:
        raise Exception('response is missing required error field')
    if 'result' not in res:
        raise Exception('response is missing required result field')
    if res['error'] is not None:
        raise Exception(res['error'])
    return res['result']


def get_all_notes():
    cards = invoke('findCards', query='"deck:全::1.日本語::2.語彙"')
    notes = invoke('cardsToNotes', cards=cards)
    return notes


notes = get_all_notes()

for note in notes:
    print(note)