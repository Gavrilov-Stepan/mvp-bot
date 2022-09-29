from __future__ import print_function

import os.path
import telebot

from time import sleep
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SAMPLE_SPREADSHEET_ID = '1k3Oh1z7LcvEFBlV6POmePPQsphRUa_SEXCGGJe2V0L8'
SAMPLE_RANGE_NAME = 'List1!A2:B'
TimerIsSet = False


#следующая функция почти полносью взята из документации Google Sheets for Developers
def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        global values
        values = result.get('values', [])
        if values == []:
            return
    except HttpError as err:
        print(err)
    print('yoy')


if __name__ == '__main__':
    main()
    bot_token = open('BOT_token.txt').read()
    TGbot = telebot.TeleBot(bot_token)


def video_materials(message):
    global values
    videos = []
    for row in values:
        try:
            videos.append(row[0])
        except IndexError:
            break
    reply_mess = 'Here is videos URL list:'
    for i in range(len(videos)):
        reply_mess += f'\n{i+1}) ' + videos[i]
    TGbot.send_message(message.chat.id, reply_mess)


def additional_materials(message):
    global values
    additionals = []
    for row in values:
        try:
            additionals.append(row[1])
        except IndexError:
            break
    reply_mess = 'Here is additional materials URL list:'
    for i in range(len(additionals)):
        reply_mess += f'\n{i + 1}) ' + additionals[i]
    TGbot.send_message(message.chat.id, reply_mess)


def send_remind(interval, message):
    sleep(interval)
    reply_mess = "It's studying time!"
    TGbot.send_message(message.chat.id, reply_mess)
    send_remind(interval, message)


@TGbot.message_handler(commands=['start'])
def start(message):
    reply_mess1 = "Welcome, {user_name}! It's Google Sheets Bot.".format(user_name=message.from_user.first_name)
    reply_mess2 = 'Please enter the interval between reminds in the format: hrs.min.sec'

    buttons = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = telebot.types.KeyboardButton("Видеоматериалы")
    button2 = telebot.types.KeyboardButton("Дополнительные Материалы")
    buttons.add(button1, button2)

    TGbot.send_message(message.chat.id, reply_mess1)
    TGbot.send_message(message.chat.id, reply_mess2)
    TGbot.send_message(message.chat.id, "также можете выбрать одну из функций:", reply_markup=buttons)


@TGbot.message_handler(content_types=['text'])
def content(message):
    global TimerIsSet
    message_text = message.text
    if message_text.lower() == 'видеоматериалы':
            video_materials(message)
    elif message_text.lower() == 'дополнительные материалы':
            additional_materials(message)
    else:
        if message_text.replace('.', '').isdigit() and message_text.count('.') == 2 and not TimerIsSet:
            points_count = 0
            dimension = [0, 0, 0]
            for symbol in message_text:
                if symbol != '.':
                    dimension[points_count] *= 10
                    dimension[points_count] += int(symbol)
                else:
                    points_count += 1
                    if points_count > 2:
                        break
            global interval
            if dimension[0]*3600 + dimension[1]*60 + dimension[2] > 0:
                interval = dimension[0]*3600 + dimension[1]*60 + dimension[2]
                TGbot.send_message(message.chat.id, f"Interval was set {dimension[0]} hours, {dimension[1]} minutes, {dimension[2]} seconds,")
            else:
                TGbot.send_message(message.chat.id, "Interval must be at least 1 second!")
            print(dimension)
            TimerIsSet = True
            send_remind(interval, message)


TGbot.polling(none_stop=True)
