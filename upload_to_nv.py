import requests
import os
from bs4 import BeautifulSoup
import time
# import json
from generate_image import generate_image

GROUP_ID = 352

isFree = True

cookies = {
    '_ym_d': '1757020482',
    '_ym_isad': '1',
    '_ym_uid': '1757020482489896953',
    'auth_key': 'phcT6i48ICVGeI5zXqcEC31t4y%2BRio2quegeGG6AkNiIAQraP9hsaC3VJ5cjgt0l',
    'beget': 'begetok',
    'device_id': '0f3714b36a0da8298ec4eac27dfd623f',
    'first_id': '11139',
    'PHPSESSID': '641a20dd1e69f3c7cd6b200e14e4a383',
    'theme': 'dark',
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": f"https://nolvoprosov.ru/groups/{GROUP_ID}",
}

session = requests.Session()
session.cookies.update(cookies)

def send_message(image_url: str):

    if image_url == "Генерирую...":
        msg = "<b>Генерирую...</b>"
    elif image_url:
        msg = f'<img src="{image_url}" />'
    else: 
        msg = "Пожалуйста, отправьте текст для генерации"

    """Отправляем сообщение"""
    url = "https://nolvoprosov.ru/functions/ajaxes/messages/act.php"
    payload = {
        "rs[parent_id]": str(GROUP_ID),
        "rs[group]": "message",
        "rs[type]": "group_message",
        "rs[mode]": "add",
        "rs[plan]": "simple",
        "text": msg,
    }
    r = session.post(url, data=payload, headers=headers)
    r.raise_for_status()

def upload_image (image_path):
    """Загружает изображение на сервер и возвращает URL"""

    # URL для загрузки
    url = "https://nolvoprosov.ru/functions/ajaxes/uploads/upload_files.php?method=device&type=image"

    try:

        # Открываем файл для загрузки
        with  open(image_path, 'rb') as file:
            files = {
                'file-0': (os.path.basename(image_path), file, 'image/webp')
            }
            
            # Отправляем POST запрос
            response = session.post(
                url,
                headers=headers,
                cookies=cookies,
                files=files
            )
            
        # Проверяем ответ
        if response.status_code == 200:

            result = response.json()

            # Проверяем успешность
            if result["3"] is True and 'data' in result:
                image_data = result['data'][0]
                send_message(image_data['url'])
            else:
                print(f"Ошибка загрузки: {result}")
                return "Бот не смог заргрузить файл"
            
                
        else:
            print(f"HTTP ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
        return None

def get_last_message(group_id: int):
    """Парсим страницу и достаем последнее сообщение с максимальным контекстом"""
    url = f"https://nolvoprosov.ru/groups/{group_id}"
    r = session.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    container = soup.find("div", class_="box rss messages groups_messages compact in_main")


    messages = container.find_all("div", attrs={"data-rs": True})


    # Получаем последнее сообщение
    last_msg = messages[-1]

    text_box = last_msg.find("div", class_="box text ce basic")
    text = text_box.get_text(strip=True) if text_box else ""

    return text

while isFree:
    
    try:
        last_msg = get_last_message(GROUP_ID)

        if last_msg.startswith("@"):
            if len(last_msg) > 1:
                send_message("Генерирую...")
                isFree = False
                generate_image(last_msg)
                upload_image("./image.jpg")
                isFree = True
    except Exception as e:
        print(e)

    time.sleep(1)