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

last_seen_id = 0

send_message = js.document.getElementById("send_message")
connect_chat = js.document.getElementById("connect_chat")
sender = js.document.getElementById("sender")
message_text = js.document.getElementById("message_text")
chat_window = js.document.getElementById("chat_window")

# Добавляет новое сообщение в список сообщений
def append_message(message):
    global mes_ids
    if message["msg_id"] not in mes_ids:
        # Создаем HTML-элемент представляющий сообщение
        item = js.document.createElement("li")  # li - это HTML-тег для элемента списка
        item.className = "list-group-item"   # className - определяет как элемент выглядит
        # Добавляем его в список сообщений (chat_window)
        item.innerHTML = f'[<b>{message["sender"]}</b>]: <span>{message["text"]}</span><span class="badge text-bg-light text-secondary">{message["time"]}</span>'
        chat_window.prepend(item)
        mes_ids.append(message["msg_id"])

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
    await load_fresh_messages()

# Загружает новые сообщения с сервера и отображает их
async def load_fresh_messages():
    global last_seen_id
    # 1. Загружать все сообщения каждую секунду (большой трафик)
    result = await fetch(f"/get_messages?after={last_seen_id}", method="GET")  # Делаем запрос
    # chat_window.innerHTML = ""  # Очищаем окно с сообщениями
    data = await result.json()
    all_messages = data["messages"]  # Берем список сообщений из ответа сервера
    for msg in all_messages:
        last_seen_id = msg["msg_id"]  # msg_id Последнего сообщение
        append_message(msg)
    set_timeout(1, load_fresh_messages) # Запускаем загрузку заново через секунду
    # 2. Загружать только новые сообщения


# Устнаваливаем действие при клике
send_message.onclick = send_message_click
connect_chat.onclick = connect_chat_click
#append_message({"sender":"Елена Борисовна", "text":"Присылаем в чат только рабочие сообщения!!!", "time": "00:01"})
#load_fresh_messages()

