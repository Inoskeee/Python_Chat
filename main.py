from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__, static_folder="./client", template_folder="./client")  # Настройки приложения

msg_id = 1
all_messages = []

usr_id = 1
users = []

@app.route("/chat")
def chat_page():
    return render_template("chat.html")


def add_message(sender, text):
    global msg_id
    new_message = {
        "sender": sender,
        "text": text,
        "time": datetime.now(),
        "msg_id": msg_id
    }
    msg_id += 1
    all_messages.append(new_message)
    message = f"{new_message['time']} - {new_message['sender']}: {new_message['text']}\n"
    with open('allmessages.txt', 'a') as file:
        file.write(message)

# API для получения списка сообщений

@app.route("/get_messages")
def get_messages():
    sender = request.args["sender"]
    connect_time = None
    for user in users:
        if user["sender"] == sender:
            connect_time = user["connect_time"]
    messages = []
    for message in all_messages:
        if message["time"] >= connect_time:
            messages.append(message)
    return {"messages": messages}

@app.route("/connect_user")
def connect_user():
    global usr_id
    sender = request.args["sender"]
    users.append({"id": usr_id, "sender" : sender, "connect_time": datetime.now()})
    usr_id += 1
    return users

@app.route("/get_users")
def get_users():
    return {"users": users}

@app.route("/remove_message")
def remove_message():
    id = request.args["id"]
    index = None
    for i in range(0, len(all_messages)):
        if all_messages[i]['msg_id'] == int(id):
            index = i
            break
    print(all_messages[0])
    print(index)
    if index != None:
        all_messages.pop(index)
    return id

# HTTP-GET
# API для получения отправки сообщения  /send_message?sender=Mike&text=Hello
@app.route("/send_message")
def send_message():
    sender = request.args["sender"]
    text = request.args["text"]
    add_message(sender, text)
    return {"result": True}


# Главная страница
@app.route("/")
def hello_page():
    return "New text goes here"


app.run()
