import requests
import audioread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import random
import time


TOKEN = "1659046401:AAHBN-l_sex3X5arCwHmRIuvWpgGzbecok0"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"Message From " + message.chat.first_name)
    bot.send_message(message.chat.id,
                     "Hello " + message.chat.first_name + " Welcome To Speech-to-Text Bot\n\n"
                                                          "How To Use :\n"
                                                          "1. Send Your Audio Using Document or Voice Note,\n"
                                                          "2. Select Language And Waitting Bot send Text\n"
                                                          "\n<b>Don't Send Audio File Up to 10 MB</b>\n\n"
                                                          "Author : <a href='https://t.me/Sandroputraaa'>Sandro Putraa</a>",
        disable_web_page_preview=True
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    calldata = call.data
    splitcall = calldata.split("|")

    bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                              text="You Select " + splitcall[0] + " Language, Please Wait Processing Your Audio 😁")
    AudioRandom = splitcall[1]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    url = "http://192.168.0.106/API/AudioText.php"
    headers = {
        "Auth": "sandrocods",
    }

    with open(str(AudioRandom) + '.mp3', 'rb') as mp3:

        with audioread.audio_open(str(AudioRandom) + ".mp3") as baca:
            send_files = {'uploaded_file': ('1.mp3', mp3.read(), 'audio/mpeg'),
                          'Option': (None, 'Upload'),
                          'sampleRateHertz': (None, str(baca.samplerate)),
                          'audioChannelCount': (None, str(baca.channels)),
                          'lang': (None, str(splitcall[0]))
                          }

            response = requests.request("POST", url, files=send_files, headers=headers)
            JsonResponse = response.json()
            print(JsonResponse['Message'] + " Sample Rate : " + str(baca.samplerate), flush=True)
            bot.send_chat_action(call.message.chat.id, 'typing')
            bot.send_message(call.message.chat.id, "Success Upload " + str(AudioRandom) + ".mp3\n\nAudio Information :\n\n1. Sample Rate : " + str(
                baca.samplerate) + "\n2. Duration : " + str(
                baca.duration) + "\n\n<b>Please Wait Trying Decode From Audio To Text </b>")

            baca.close()
        mp3.close()
        os.remove(str(AudioRandom) + ".mp3")
    if "Success Upload Audio" == JsonResponse['Message']:
        for x in range(100):
            req = requests.request("POST", url, files={
                'Option': (None, "Process"),
                'Data': (None, JsonResponse['Data'])
            }, headers=headers
                                   )
            JsonResponse2 = req.json()
            if "Processing " + str(JsonResponse['Data']) == JsonResponse2['Message']:
                print(JsonResponse2['Message'] + " ~ " + str(JsonResponse2['Timestamp']), flush=True)
                bot.send_chat_action(call.message.chat.id, 'typing')
            else:
                bot.send_chat_action(call.message.chat.id, 'typing')
                bot.send_message(call.message.chat.id, "<b>Success Decode " + str(AudioRandom) + ".mp3 To Text\n\n<code>" + str(JsonResponse2['Text'] + "</code></b>"))
                print(req.text, flush=True)
                break

            if x > 20:
                bot.reply_to(call.message.chat.id, "Failed Decode Audio To Text\nTry Another Audio Files\nTry Again Later")
                break
    else:
        print(f"Failed")




@bot.message_handler(content_types=['document', 'audio', 'voice'])
def handle_docs_audio(message):
    try:
        print(f"Message From " + message.chat.first_name)
        if (message.content_type == 'voice'):
            print(f"Getting Voice File message : " + str(message.voice.file_id), flush=True)
            file_info = bot.get_file(message.voice.file_id)
        else:
            print(f"Getting Audio File message : " + str(message.audio.file_id), flush=True)
            file_info = bot.get_file(message.audio.file_id)
        AudioRandom = "Audio" + str(random.randint(0,1000))
        file = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN,
                                                              file_info.file_path))
        with open(AudioRandom + ".mp3", 'wb') as simpan:
            simpan.write(file.content)
            simpan.close()

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("Indonesia", callback_data="id-ID|" + AudioRandom + ""),
            InlineKeyboardButton("Jawa", callback_data="jv-ID|" + AudioRandom + ""),
            InlineKeyboardButton("Russia", callback_data="ru-RU|" + AudioRandom + ""),
            InlineKeyboardButton("Inggris United States", callback_data="en-US|" + AudioRandom + ""),
            InlineKeyboardButton("Malaysia", callback_data="ms-MY|" + AudioRandom + ""))

        bot.send_message(message.chat.id, "Select Language :", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "Only Mp3 format can be process Bot")



@bot.message_handler(content_types=['text'])
def command_default(m):
    bot.send_chat_action(m.chat.id, 'typing')
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")


try:
    print(f"Bot Still Running", flush=True)
    bot.infinity_polling(timeout= int(20), long_polling_timeout= int(30))
except:
    time.sleep(3)
