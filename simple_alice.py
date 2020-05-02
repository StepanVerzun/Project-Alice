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
room = 0
score = 0


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
    global room, score

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
    if (req['request']['original_utterance'].lower() in [
        'ладно',
        'да',
        'давай',
        'хорошо',
        'старт',
        'начать',
        'конечно'
    ] or 'да' in req['request']['nlu']['tokens']) and room == 0:
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
        sessionStorage[user_id]['game_started'] = True
    if 'первая' in req['request']['nlu']['tokens'] and room == 0:
        room = 1
        sessionStorage[user_id] = {
            'suggests': [
                "Ничего",
                "Посмотришь внутрь автомобиля",
                "Сядешь в автомобиль",
            ]
        }
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '1030494/54d252522a56d03b897a'
        res['response']['card']['title'] = 'Ты оказался(лась) в гараже.'
        res['response']['card']['description'] = \
            'Видишь перед собой красный автомобиль, в котором открыта дверь. Что ты сделаешь?'
        res['response']['text'] = 'первая комната комната'
        res['response']['buttons'] = get_suggests(user_id)
    elif 'вторая' in req['request']['nlu']['tokens'] and room == 0:
        room = 2
        sessionStorage[user_id] = {
            'suggests': [
                "Осмотришь камин",
                "Выпьешь напиток",
                "Ничего",
            ]
        }
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '213044/940eee14c76ec65cbbc1'
        res['response']['card']['title'] = 'Ты попал(а) в комнату.'
        res['response']['card']['description'] = \
            'В центре стоит небольшой стол, а вокруг него диван и ещё 4 кресла, будто тут проводились какие-то важные встречи или собрания. Ты видишь, что на столе стоит бокал с напитком, а слева расположен камин, наполненный бревнами. Что ты сделаешь?'
        res['response']['text'] = 'вторая комната'
        res['response']['buttons'] = get_suggests(user_id)
    elif 'третья' in req['request']['nlu']['tokens'] and room == 0:
        room = 3
        sessionStorage[user_id] = {
            'suggests': [
                "Снимешь ткань со стула",
                "Посмотришься в зеркало",
                "Ляжешь на кровать",
            ]
        }
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '1656841/e9b28b88b3649bc0e693'
        res['response']['card']['title'] = 'Ты оказался(лась) в довольно старой комнате.'
        res['response']['card']['description'] = \
            'Перед тобой стоят две красивые кровати, так и хочется лечь на них, отдохнуть. Рядом с кроватями стоит стул, на который накинута странная белая ткань. В левой части комнаты находится антикварное зеркало. Что ты сделаешь?'
        res['response']['text'] = 'третья комната'
        res['response']['buttons'] = get_suggests(user_id)
    elif 'четвертая' in req['request']['nlu']['tokens'] and room == 0:
        room = 4
        sessionStorage[user_id] = {
            'suggests': [
                "Просто уйду из комнаты и ничего не отвечу",
                '"Ничего, просто зашёл"',
                '"Здравствуйте, извините за беспокойство, я по ошибке сюда зашёл(ла)"',
            ]
        }
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '1030494/7d66f72baf9fe8dac989'
        res['response']['card']['title'] = 'Ты вошёл(ла) в полностью темную комнату.'
        res['response']['card']['description'] = \
            'Вдруг ты слышишь чей-то голос, и он спрашивает: "Что ты тут делаешь?" Что ты ему ответишь?'
        res['response']['text'] = 'четвертая комната'
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
