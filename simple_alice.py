# импортируем библиотеки
from flask import Flask, request
import logging

# библиотека, которая нам понадобится для работы с JSON
import json
from random import randint

with open("rooms.json", "r", encoding="utf-8") as file:
    rooms = json.loads(file.read())
# создаём приложение
# мы передаём __name__, в нем содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например,
# произошло внутри модуля logging, то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info(f'Request: {request.json!r}')

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи
    # библиотеки json преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'rooms': [],
            'room': "",
            'choice': False,
            'suggests': ["Да", "Не сегодня, друг."],
            'score': 0
        }

        # Заполняем текст ответа
        res['response']['text'] = 'Приветствую тебя в текстовом квесте *название*! Готов ли ты начать игру?'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    elif req['request']['original_utterance'].lower() in [
        'ладно',
        'да',
        'давай',
        'хорошо',
        'старт',
        'начать',
        'конечно'
    ] or 'да' in req['request']['nlu']['tokens']:
        # Пользователь согласился, начинаем квест
        sessionStorage[user_id]['room'] = "0"
        sessionStorage[user_id]['choice'] = True
        sessionStorage[user_id]['suggests'] = rooms["0"]["actions"]
        res['response']['text'] = rooms["0"]["description"]
        res['response']['buttons'] = get_suggests(user_id)
        return
    elif 'нет' in req['request']['nlu']['tokens'] or 'не' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Еще увидимся!'
        res['response']['end_session'] = True
        return
    elif not sessionStorage[user_id]['choice']:
        active_room = sessionStorage[user_id]['room']
        answer = req['request']['original_utterance']
        sessionStorage[user_id]['choice'] = True
        sessionStorage[user_id]['suggests'] = rooms["0"]["actions"]
        sessionStorage[user_id]['score'] += rooms[active_room]["points"][answer]
        res['response']['text'] = rooms[active_room]["answers"][answer]
        res['response']['buttons'] = get_suggests(user_id)
        return
    elif sessionStorage[user_id]['choice']:
        if len(sessionStorage[user_id]['rooms']) == 5:
            sessionStorage[user_id]['rooms'] = []
            sessionStorage[user_id]['room'] = ''
            sessionStorage[user_id]['suggests'] = ["Да", "Нет"]
            if sessionStorage[user_id]['score'] <= -3:
                res['response']['text'] = rooms["ending"]["bad"]
            elif -2 <= sessionStorage[user_id]['score'] <= 2:
                res['response']['text'] = rooms["ending"]["middle"]
            elif sessionStorage[user_id]['score'] >= 3:
                res['response']['text'] = rooms["ending"]["good"]
            res['response']['text'] += ' Хочешь еще раз пройти этот квест'
            res['response']['buttons'] = get_suggests(user_id)
            return
        while True:
            active_room = randint(1, 7)
            if str(active_room) not in sessionStorage[user_id]['rooms']:
                sessionStorage[user_id]['rooms'].append(str(active_room))
                break
        sessionStorage[user_id]['room'] = str(active_room)
        sessionStorage[user_id]['choice'] = False
        sessionStorage[user_id]['suggests'] = rooms[str(active_room)]["actions"]
        res['response']['text'] = rooms[str(active_room)]["description"]
        res['response']['buttons'] = get_suggests(user_id)
        return


# Функция возвращает подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    return suggests


if __name__ == '__main__':
    app.run()
