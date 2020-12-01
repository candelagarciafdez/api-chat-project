from flask import Flask, request
from pymongo import MongoClient
from bson import json_util
import requests
import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
nltk.download("vader_lexicon")
nltk.download("stopwords")

app = Flask(__name__)
client = MongoClient()
db = client.get_database("apichat")
# Decorators
@app.route("/welcome")
def hello_world():
    return "hola"

@app.route("/user/create/")
def create_user():
    username = request.args.get("username")
    newuser= {"user_name": username}
    otherusers= db.user.distinct("user_name")
    if username in otherusers:
        raise ValueError ("Username already exists.Please, try another username.")
    else:
        add_user = db.user.insert_one(newuser)
        return json_util.dumps(f"User created succesfully! user_name:{username} , user_id: {add_user.inserted_id}")

@app.route("/chat/create")
def create_chat():
    nombre_chat = request.args.get("nombre_chat")
    usuarios_chat = request.args.getlist("participantes")
    today = datetime.datetime.now()

    #Obtenemos el id de los participantes y creamos un diccionario donde los usuarios se relacionen con su id
    participantes = {}
    for usuario in usuarios_chat:
        res = db.users.find({"username":usuario},{"_id":1})
        participantes[usuario] = list(res)[0]["_id"]

    newchat= {"nombre_chat": nombre_chat, "participantes": participantes, "date": today}
    otherchats= db.chats.distinct("chat")
    if nombre_chat in otherchats:
        raise ValueError ("Chat already exists. Please, try another.")
    else:
        add_chat = db.chats.insert_one(newchat)
        return json_util.dumps(f"Chat created succesfully! nombre_chat:{nombre_chat} , chat_id: {add_chat.inserted_id}, participantes: {participantes}, date: {today}")

@app.route("/message/create/<nombre_chat>")
def create_message(nombre_chat):
    username  = request.args.get("username")
    message = request.args.get("message")
    today = datetime.datetime.now()

    chat_exists = db.chats.find({"nombre_chat":nombre_chat},{"_id":1})
    if len(list(chat_exists)) == 0:
        raise KeyError(f"Chat {nombre_chat} does not exist. Please, specify one that does.")

    usuario_en_chat = db.chats.find({"nombre_chat":nombre_chat},{"participantes":username})
    if len(list(usuario_en_chat)) == 0:
        raise KeyError(f"User '{username}' not a participant in chat '{nombre_chat}'")

    newmessage= {"nombre_chat": nombre_chat, "date": today, "user_name": username, "message": message}
    add_message = db.messages.insert_one(newmessage)
    return json_util.dumps(f"Message created succesfully! nombre_chat:{nombre_chat} , chat_id: {add_message.inserted_id},user_name: {username} date: {today} , message: {message}")

@app.route("/list/chat/<nombre_chat>")
def list_chat(nombre_chat):
    mensajes = []
    messages = list(db.messages.find({"nombre_chat":{nombre_chat}}))
    for message in messages:
        mensajes.append(message.message.text)
    return json_util.dumps(mensajes)

@app.route("/chat/sentiment/<nombre_chat>")
def analyze_sentiments(nombre_chat):
    sia = SentimentIntensityAnalyzer()
    scores = {}
    messages = list(db.messages.find({"nombre_chat":{nombre_chat}}))
    for message in messages:
        scores[message]=sia.polarity_scores(message.message.text)
    return json_util.dumps(scores)


if __name__ == '__main__':
    app.run(debug=True, port=5000)



