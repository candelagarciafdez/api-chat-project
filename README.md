# api-chat-project
----------------------------------
En este proyecto, tuvimos que hacer una API mediante la cual introducir datos en una base de datos de Mongo. La API la construimos usando la librería `flask`.

En mi API, creé los diferentes decoradores con los *endopoints*  a los que quería "atacar" y poder modificar de esta forma los datos almacenados.

El primer paso fue unir la API con MongoDB mediante MongoClient en mi servidor local y crear las *collections* que tuve que usar más tarde.

Después de eso, uní mi API a mi puerto local 5000 para poder comprobardesde el navegador que funcionaba. Cuando comprobé que sí, empecé a modificar los endpoints de los decoradores y a añadir las funciones que más tarde usaría.

Un ejemplo de función dentro de un decorador sería:
```
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
```

Por último, después de añadir las funciones de añadir usuario, crear chat, crear mensaje, etc., realizamos un análisis de lenguaje natural con NLTK (en concreto análisis de sentimientos). La función que realicé para ello fue la siguiente:

```
@app.route("/chat/sentiment/<nombre_chat>")
def analyze_sentiments(nombre_chat):
    sia = SentimentIntensityAnalyzer()
    scores = {}
    messages = list(db.messages.find({"nombre_chat":{nombre_chat}}))
    for message in messages:
        scores[message]=sia.polarity_scores(message.message.text)
    return json_util.dumps(scores)
```


El principal problema que he encontrado, es que me sale un error 500 (error inespecífico) cuando intento ejecutar los comandos desde Jupyter (desde el navegador funciona correctamente). He intentado solucionarlo y leer qué podría causarlo, pero no he conseguido entender el motivo. Al principio me daba un error (también 500) que pude solucionar mediante la información aportada por la terminal, pero ese último no conseguí solventarlo.

Como mejoras para el futuro (aparte de la evidente de solucionar eso) me gustaría poder crear una interfaz gráfica para la API para que fuese más amigable con el usuario que quiera trabajar con ella.