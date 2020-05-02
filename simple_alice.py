# импортируем библиотеки
from flask import Flask, request
import logging

# библиотека, которая нам понадобится для работы с JSON
import json

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
            'suggests': [
                "Да",
                "Не сегодня, друг.",
            ]
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
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'да',
        'давай',
        'хорошо',
        'старт',
        'начать',
        'конечно'
    ]:
        # Пользователь согласился, начинаем квест.
        sessionStorage[user_id] = {
            'suggests': [
                "Первая.",
                "Вторая.",
                "Третья.",
                "Четвертая.",
            ]
        }
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '1533899/111916359298fd5d753b'
        res['response']['card']['title'] = \
            'По неизвестной тебе причине ты оказался в пустой комнате с 4 дверями. В какую дверь ты пойдешь?'
        res['response']['text'] = \
            'По неизвестной тебе причине ты оказался в пустой комнате с 4 дверями. В какую дверь ты пойдешь?'
        res['response']['buttons'] = get_suggests(user_id)
    else:
        res['response']['text'] = 'Еще увидимся!'
        res['response']['end_session'] = True
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
