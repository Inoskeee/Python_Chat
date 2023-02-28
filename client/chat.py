import asyncio
from pyodide.http import pyfetch
import json

import js as js

async def fetch(url, method, payload=None):
    kwargs = {
        "method": method
    }
    if method == "POST":
        kwargs["body"] = json.dumps(payload)
        kwargs["headers"] = {"Content-Type": "application/json"}
    return await pyfetch(url, **kwargs)


def set_timeout(delay, callback):
    def sync():
        asyncio.get_running_loop().run_until_complete(callback())

    asyncio.get_running_loop().call_later(delay, sync)

mes_ids = []
user_ids = []

send_message = js.document.getElementById("send_message")
connect_chat = js.document.getElementById("connect_chat")
sender = js.document.getElementById("sender")
message_text = js.document.getElementById("message_text")
chat_window = js.document.getElementById("chat_window")
chat_users = js.document.getElementById("chat_users")

# Добавляет новое сообщение в список сообщений
def append_message(message):
    global mes_ids
    if message["msg_id"] not in mes_ids:
        # Создаем HTML-элемент представляющий сообщение
        item = js.document.createElement("li")  # li - это HTML-тег для элемента списка
        item.className = "list-group-item"   # className - определяет как элемент выглядит
        item.id = f'message_{message["msg_id"]}'
        # Добавляем его в список сообщений (chat_window)
        if message['sender'] == sender.value:

            removeButton = js.document.createElement("a")
            removeButton.className = "btn btn-primary"
            removeButton.id = message["msg_id"]
            removeButton.innerHTML = "Удалить у себя"
            removeButton.onclick = remove_self_message

            removeButtonAll = js.document.createElement("a")
            removeButtonAll.className = "btn btn-warning"
            removeButtonAll.id = message["msg_id"]
            removeButtonAll.innerHTML = "Удалить у всех"
            removeButtonAll.onclick = remove_message_all

            item.innerHTML = f'[<b>{message["sender"]}</b>]: <span>{message["text"]}</span>' \
                             f'<span class="badge text-bg-light text-secondary">{message["time"]}</span>'
            item.append(removeButton)
            item.append(removeButtonAll)
        else:
            item.innerHTML = f'[<b>{message["sender"]}</b>]: <span>{message["text"]}</span><span class="badge text-bg-light text-secondary">{message["time"]}</span>'
        chat_window.prepend(item)
        mes_ids.append(message["msg_id"])

def append_users(user):
    if user['id'] not in user_ids:
        item = js.document.createElement("span")  # li - это HTML-тег для элемента списка
        item.className = "input-group-text"  # className - определяет как элемент выглядит
        # Добавляем его в список сообщений (chat_window)
        item.innerHTML = f'{user["sender"]}'
        chat_users.append(item)
        user_ids.append(user['id'])


async def remove_self_message(e):
    id = e.target.id
    message = js.document.getElementById(f'message_{id}')
    message.remove()

async def remove_message_all(e):
    id = e.target.id
    message = js.document.getElementById(f'message_{id}')
    message.remove()
    await fetch(f"/remove_message?id={id}", method="GET")

# Вызывается при клике на send_message
async def send_message_click(e):
    # Отправляем запрос
    await fetch(f"/send_message?sender={sender.value}&text={message_text.value}", method="GET")
    # Очищаем поле
    message_text.value = ""

async def connect_chat_click(e):
    connect_chat.hidden = True
    sender.disabled = True
    message_text.hidden = False
    send_message.hidden = False
    chat_window.hidden = False
    chat_users.hidden = False
    await fetch(f"/connect_user?sender={sender.value}", method="GET")
    await load_fresh_messages()

# Загружает новые сообщения с сервера и отображает их
async def load_fresh_messages():
    global sender
    # 1. Загружать все сообщения каждую секунду (большой трафик)
    result = await fetch(f"/get_messages?sender={sender.value}", method="GET")  # Делаем запрос
    users = await fetch(f"/get_users", method="GET")  # Делаем запрос

    usersData = await users.json()
    connected_users = usersData["users"]
    for user in connected_users:
        append_users(user)
    # chat_window.innerHTML = ""  # Очищаем окно с сообщениями
    data = await result.json()
    all_messages = data["messages"]  # Берем список сообщений из ответа сервера

    last_seen_ids = []
    for msg in all_messages:
        last_seen_ids.append(msg["msg_id"])  # msg_id Последнего сообщение
        append_message(msg)
    try:
        for msg in mes_ids:
            if msg not in last_seen_ids:
                message = js.document.getElementById(f'message_{msg}')
                if message != None:
                    message.remove()
    except Exception as e:
        print(e)
    set_timeout(1, load_fresh_messages) # Запускаем загрузку заново через секунду
    # 2. Загружать только новые сообщения


# Устнаваливаем действие при клике
send_message.onclick = send_message_click
connect_chat.onclick = connect_chat_click
#append_message({"sender":"Елена Борисовна", "text":"Присылаем в чат только рабочие сообщения!!!", "time": "00:01"})
#load_fresh_messages()

