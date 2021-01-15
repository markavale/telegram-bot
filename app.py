import re
from time import sleep
from flask import Flask, request
import telegram
from telebot.ai import generate_smart_reply
from decouple import config
import requests
import smtplib
from email.message import EmailMessage

# from credentials import bot_token, bot_user_name,URL
bot_token = config('bot_token')
bot_user_name = config('bot_user_name')
email_username = config('email_username')
email_pass = config('email_pass')
URL = config('URL')
global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)



app = Flask(__name__)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id

   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()
   telegram_data = {
    "text": text
    }
   requests.post("http://markanthonyvale.herokuapp.com/api/telegram/", telegram_data)

   # for debugging purposes only
   print("got text message :", text)
   reply = generate_smart_reply(text)
   bot.sendMessage(chat_id=chat_id, text=reply, reply_to_message_id=msg_id)
   # the first time you chat with the bot AKA the welcoming message
   if text == "/start":
       
       # print the welcoming message
       bot_welcome = """
       Welcome to MAV bot, please enter a name and the bot will reply with an avatar for your name.
       """
       # send the welcoming message
       bot.sendChatAction(chat_id=chat_id, action="typing")
       sleep(1.5)
       bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)


   else:
       
        try:
           
           # clear the message we got from any non alphabets
           text = re.sub(r"\W", "_", text)
           print(text)
           # create the api link for the avatar based on http://avatars.adorable.io/
           url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
           # reply with a photo to the name the user sent,
           # note that you can send photos by url and telegram will fetch it for you
           bot.sendChatAction(chat_id=chat_id, action="upload_photo")
           sleep(2)
           bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
           # Create EmailMessage Object
           email = EmailMessage()
            # Who is the email from
           email["from"] = email_username
            # To which email you want to send the email
           email["to"] = email_username
            # Subject of the email
           email["subject"] = "Telegram Bot"
           email.set_content(text)

            # Create smtp server
           with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
               smtp.ehlo()
                # Connect securely to server
               smtp.starttls()
                # Login using username and password to dummy email. Remember to set email to allow less secure apps if using Gmail
               smtp.login(email_username, email_pass)
                # Send email.
               smtp.send_message(email)
        except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="There was a problem, please try again", reply_to_message_id=msg_id)
           # Create EmailMessage Object
           email = EmailMessage()
            # Who is the email from
           email["from"] = email_username
            # To which email you want to send the email
           email["to"] = email_username
            # Subject of the email
           email["subject"] = "Telegram Bot"
           email.set_content(text)

            # Create smtp server
           with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
               smtp.ehlo()
                # Connect securely to server
               smtp.starttls()
                # Login using username and password to dummy email. Remember to set email to allow less secure apps if using Gmail
               smtp.login(email_username, email_pass)
                # Send email.
               smtp.send_message(email)

   return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
   s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
   if s:
       return "webhook setup ok"
   else:
       return "webhook setup failed"

@app.route('/')
def index():
   return '.'


if __name__ == '__main__':
   app.run(threaded=True)