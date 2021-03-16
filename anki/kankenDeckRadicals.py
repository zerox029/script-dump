import json
import urllib.request
import requests
import re
from bs4 import BeautifulSoup

# TODO: Keep track of previously searched for kanji to reduce the amount of calls to the dictionnary

ANKI_CONNECT_URL = 'http://localhost:8765'
KANJI_DICT_URL = "https://dictionary.goo.ne.jp/word/kanji/"

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


def get_all_kanken_notes():
    cards = invoke('findCards', query='"deck:全::1.日本語::1.漢字::漢字検定::Level 10-4::2. Level 8"')
    notes = invoke('cardsToNotes', cards=cards)
    return notes


def get_radical_for_kanji(pKanji):
    print("Searching for " + pKanji)

    split_word = list(pKanji)
    regex = re.compile("([^ぁ-んァ-ンヶa-zA-Z1-9.!?\\-])")
    kanji_chars = list(filter(regex.match, split_word))

    radical_list = []
    for i, kanji in enumerate(kanji_chars):
        url = KANJI_DICT_URL + kanji
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")

        try:
            info_box = soup.find_all("div", {"class": "info"})[0]
            radical_section = info_box.find_all("dd")[0]

            radical = radical_section.text.replace(" ", "").replace("\n", "")
            radical_list.append("(" + str(i + 1) + ") " + radical)
        except IndexError:
            print(f"{bcolors.WARNING}Encountered illegal character{bcolors.ENDC}")
            return ""

    return " ".join(radical_list)


def add_radical(note_id):
    fields = invoke('notesInfo', notes=[note_id])[0]['fields']
    kanji = fields['Kanji']['value']
    radicals = get_radical_for_kanji(kanji)

    print("Adding radicals to card")
    invoke('updateNoteFields', note={"id": note_id, "fields": {"Radical": radicals}})
    print(f"{bcolors.OKBLUE}Successfully added radicals to card{bcolors.ENDC}")


kanken_notes = get_all_kanken_notes()
for i, note in enumerate(kanken_notes):
    print(f"{bcolors.HEADER}--------- Card #" + str(i + 1) + f" ---------{bcolors.ENDC}")
    add_radical(note)
