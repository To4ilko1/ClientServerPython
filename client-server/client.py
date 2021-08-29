# -*- coding: utf-8 -*-
import socket
import json  # Подключаем библиотеку для преобразования данных в формат JSON
from datetime import datetime# реализовать всё для клиента добавление удаление заказов, просмотр услуг, скидок, заказов, чатов и тд
import re
import win32event
import win32api
from winerror import ERROR_ALREADY_EXISTS
from sys import exit

def start_client():  # Основная функция, запускающая клиента. Эта функция вызывается в конце файла, после определения всех нужных деталей

    SERVER = "127.0.0.1"
    PORT = 8080
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    isauth = 0
    token = ""
    print("Подключились к серверу")
    while True:
        print("Главное меню:")
        print("1 - Авторизоваться")
        print("2 - Зарегистрироваться")
        print("3 - Посмотреть отзывы")
        print("4 - Выйти из программмы")
        print("5 - Выключить сервер")
        if isauth == 1:
            print("6 - Просмотреть список животных")
            print("7 - Добавить заказ")
            print("8 - Добавить животное")
            print("9 - Добавить отзыв")
            print("10 - Смотреть свой профиль")#!
            print("11 - Выйти из профиля")
            print("12 - Просмотреть журнал")
            print("13 - Смена пароля")
            print("14 - Посмотреть заказы")
            print("15 - Отправить сообщение в чат")
            print("16 - Смотреть чат")
            print("17 - Смотреть список животных в отеле")
            print("18 - Смотреть информацию о работнике")
        task = input()
        if not task.isdigit() or int(task) > 18:
            print("Неправильная команда!")
            continue
        task = int(task)
        msg = {}
        if task == 1:
            msg["command"] = "auth"
            msg["login"] = input("Введите логин:")
            msg["password"] = input("Введите пароль:")
        if task == 2:
            msg["command"] = "addperson"
            msg["object"] = create_person()#!
        if task == 3:
            msg["command"] = "readreviews"
        if task == 4:
            msg["command"] = "bye"
        if task == 5:
            msg["command"] = "stop"
        if task == 6:
            msg["command"] = "readanimals"
            msg["token"] = token
        if task == 7:
            msg["command"] = "addorder"
            msg["token"] = token
            msg["object"] = create_order()
        if task == 8:
            msg["command"] = "addanimal"
            msg["token"] = token
            msg["object"] = create_animal()
        if task == 9:
            msg["command"] = "addreview"
            msg["token"] = token
            msg["object"] = create_review()
        if task == 10:
            msg["command"] = "lookaccount"
            msg["token"] = token
        if task == 11:
            msg["command"] = "logout"
            msg["token"] = token
            isauth = 0
        if task == 12:
            msg["command"] = "readjournals"
            msg["token"] = token
            msg["animalid"] = input("Введите ID животного:\n")
        if task == 13:
            while True:
                password1 = input("Введите пароль:")
                password2 = input("Повторите пароль:")
                if password1 == password2:
                    msg["command"] = "changepswd"
                    msg["token"] = token
                    msg["password"] = password1
                    break
                else:
                    print("Пароли не совпадают, повторите попытку")
                    continue
        if task == 14:
            msg["command"] = "readorders"
            orderdatestart = str(input("Введите начальную дату для поиска в формате\nгггг-мм-дд: "))
            if orderdatestart !="":
                while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdatestart) == []:
                    orderdatestart = input(("Неправильный формат! Введите начальную дату для поиска в формате\nгггг-мм-дд: "))
            msg["DateStart"] = orderdatestart
            orderdateend = str(input("Введите конечную дату для поиска в формате\nгггг-мм-дд: "))
            if orderdateend !="":
                while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdateend) == []:
                    orderdateend = input(("Неправильный формат! Введите конечную дату для поиска в формате\nгггг-мм-дд: "))
            msg["DateEnd"] = orderdateend
            msg["token"] = token
        if task == 15:
            msg["command"] = "addmessage"
            msg["token"] = token
            msg["object"] = create_message()
        if task == 16:
            msg["command"] = "readmessages"
            msg["token"] = token
            msg["DateStart"] = ""
            msg["DateEnd"] = ""
            msg["Status"] = int(input("Показать непрочитанные сообщения? 0 - нет, 1 - да: "))
            if msg["Status"] == 0:
                sorting = int(input("Осортировать сообщния по дате? 0 - нет, 1 - да: "))
                if sorting == 1:
                    msgdatestart = str(input("Введите начальную дату для поиска в формате\nгггг-мм-дд-чч-мм : "))
                    while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}', msgdatestart) == []:
                        msgdatestart = input(("Неправильный формат! Введите начальную дату для поиска в формате\nгггг-мм-дд: "))
                    msg["DateStart"] = msgdatestart
                    msgdateend = str(input("Введите конечную дату для поиска в формате\nгггг-мм-дд-чч-мм: "))
                    while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}', msgdateend) == []:
                        msgdateend = input(("Неправильный формат! Введите конечную дату для поиска в формате\nгггг-мм-дд-чч-мм: "))
                    msg["DateEnd"] = msgdateend
        if task == 17:
            msg["command"] = "readanimalsinhotel"
            msg["token"] = token
        if task == 18:
            msg["command"] = "lookaccountworker"
            msg["token"] = token
            msg["_id"] = str(input("Введите ID работника: "))
        js_string = json.dumps(msg)
        client.sendall(bytes(js_string, 'UTF-8'))

        content = {}

        if task < 19:
            in_data = client.recv(9000).decode("utf-8")  # Получаем данные от сервера
            try:
                # Преобразываем данные из строки в формат словаря Python
                content = json.loads(in_data)
                if content == None:
                    print("Сервер занят, повторите попытку позже")
                    print("Клиент выключается...")
                    client.close()  # Закрываем соединение с сервером
                    exit(0)
            except Exception as error:
                print("Ошибка получения данных от сервера: ", error)
                print("Клиент выключается...")
                client.close()  # Закрываем соединение с сервером
                exit(0)

        # Начинаем обработку данных, полученных от сервера
        if task == 1:
            if content["Auth"] == 1:
                isauth = 1
                token = content["Token"]
                print("Вы авторизовались, %s" % content["UserName"])
            elif content == "Попробуйте позже":
                client.close()  # Закрываем соединение с сервером
                exit(0)  # Выключаем программу
            else:
                print("Неправильный логин или пароль")
        if task == 2:
            print(content)
        if task == 3:
            if content:
                print_reviews(content)
            else:
                print("Список пуст")
        if task == 4:
            print("Клиент выключается...")
            client.close()  # Закрываем соединение с сервером
            exit(0)  # Выключаем программу
        if task == 5:
            print("Сервер выключен, клиент выключается...")
            client.close()
            exit(0)
        if task == 6:
            if content:
                print_animals(content)
            else:
                print("Список пуст")
        if task == 7:
            print(content)
        if task == 8:
            print(content)
        if task == 9:
            print(content)
        if task == 10:
            print_account(content)
        if task == 12:
            if content:
                print_journals(content)
            else:
                print("Список пуст")
        if task == 13:
            if content:
                print(content)
            else:
                print("Ошибка сервера")
        if task == 14:
            if content:
                print_orders(content)
            else:
                print("Список пуст")
        if task == 15:
            if content:
                print(content)
        if task == 16:
            if content:
                print_messages(content)
            else:
                print("Сообщений нет")
        if task == 17:
            if content:
                print_animals_in_hotel(content)
            else:
                print("Список пуст")
        if task == 18:
            if content:
                print_account(content)
            else:
                print("Такого сотрудника нет")


def print_messages(messages):
    print("="*45)
    for message in messages:
        time = message["Time"][0:10] + " " + message["Time"][11:19]
        if message["FilePath"] == None:
            print("Время: %s\nТекст: %s\nID человека: %s\n" %(time, message["Text"], message["PersonID"]))
        else:
            print("Время: %s\nТекст: %s\nID человека: %s\nФото: %s\n" % (time, message["Text"], message["PersonID"], message["FilePath"]))

def print_animals(animals):
    print("="*45)
    for animal in animals:
        typean = animal["AnimalTypes"]
        if animal["Sex"] == 0:
            animalsex = "Мужской"
        else:
            animalsex = "Женский"
        print("ID животного: %s\nКличка: %s\nТип животного: %s\nПол: %s\nКомментарий: %s\nДата рождения: %s\n" % (animal["_id"], animal["Name"], typean["NameIfType"], animalsex, animal["Comment"], animal["Birthday"]))

def print_animals_in_hotel(animals):
    print("="*45)
    for animal in animals:
        typean = animal["AnimalTypes"]
        if animal["Sex"] == 0:
            animalsex = "Мужской"
        else:
            animalsex = "Женский"
        print("ID животного: %s\nКличка: %s\nТип животного: %s\nПол: %s\nКомментарий: %s\nДата рождения: %s\n" % (animal['_id'], animal['Name'], typean["NameIfType"], animalsex, animal['Comment'], animal['Birthday']))

def print_journals(journals):
    print("="*30)
    for journal in journals:
        tstart = journal["TimeStart"][0:10]
        tend = journal["TimeEnd"][0:10]
        print("ID журнала: %s\nВремя начала: %s\nВремя конца: %s\nID заказа: %s\nЖивотное: %s\nID работника: %s\nПоручение: %s\nКомментарий: %s\nФото: %s\n" % (
            journal["_id"],  tstart, tend, journal["OrderID"], journal["Animal"], journal["WorkerID"], journal["Task"], journal["Comment"], journal["Filepath"]))

def print_orders(orders):
    print("="*45)
    for order in orders:
        datestart = order["DateStart"][0:10]
        dateend = order["DateEnd"][0:10]
        if (order["DeliveryToTheHotel"] == 1) & (order["DeliveryFromHotel"] == 1):
            print("ID заказа: %s\nЦена: %s\nID животного: %s\nДата заезда: %s\nДата выезда: %s\nДоставка до отеля: %s\nДоставка из отеля: %s\nАдрес доставки до отеля: %s\nАдрес доставки из отеля: %s\nВремя доставки до отеля: %s\nВремя доставки из отеля: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["AnimalID"], datestart, dateend, order["DeliveryToTheHotel"], order["DeliveryFromHotel"], order["FromDeliveryAddress"], order["ToDeliveryAddress"], order["FromDeliveryTime"], order["ToDeliveryTime"], order["Comment"], order["Status"]))
        if (order["DeliveryToTheHotel"] == 0) & (order["DeliveryFromHotel"] == 0):
            print("ID заказа: %s\nЦена: %s\nID животного: %s\nДата заезда: %s\nДата выезда: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["AnimalID"], datestart, dateend, order["Comment"], order["Status"]))
        if (order["DeliveryToTheHotel"] == 1) & (order["DeliveryFromHotel"] == 0):
            print("ID заказа: %s\nЦена: %s\nID животного: %s\nДата заезда: %s\nДата выезда: %s\nДоставка до отеля: %s\nАдрес доставки до отеля: %s\nВремя доставки до отеля: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["AnimalID"], datestart, dateend, order["DeliveryToTheHotel"], order["FromDeliveryAddress"], order["FromDeliveryTime"], order["Comment"], order["Status"]))
        if (order["DeliveryToTheHotel"] == 0) & (order["DeliveryFromHotel"] == 1):
            print("ID заказа: %s\nЦена: %s\nID животного: %s\nДата заезда: %s\nДата выезда: %s\nДоставка из отеля: %s\nАдрес доставки из отеля: %s\nВремя доставки из отеля: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["AnimalID"], datestart, dateend,  order["DeliveryFromHotel"], order["ToDeliveryAddress"], order["ToDeliveryTime"], order["Comment"], order["Status"]))

def print_reviews(reviews):
    print("="*45)
    for review in reviews:
        animaltypes = review["AnimalTypes"]
        time = review["AddTime"][0:10] + " " + review["AddTime"][11:19]
        # time = datetime.strptime(review["AddTime"],"%Y-%m-%d %I:%M")
        print("ID отзыва: %s\nТекст: %s\nТип животного: %s\nВремя добавления: %s\n" % (
            review["_id"], review["Body"], animaltypes["NameIfType"], time))

def print_account(account):
    print("="*45)
    for acc in account:
        if acc["State"] == 1:
            print("ID: %s\nФИО: %s\nАдрес: %s\nТелефон: %s\nE-mail: %s\nДата рождения: %s\nЛогин: %s\nПароль: %s\n" %(acc["_id"], acc["Name"], acc["Address"], acc["Phone"], acc["Email"], acc["Birthday"], acc["Login"], acc["Password"]))
        if acc["State"] == 0:
            print("ID: %s\nФИО: %s\nТелефон: %s\nE-mail: %s\nДата рождения: %s\n" %(acc["_id"], acc["Name"], acc["Phone"], acc["Email"], acc["Birthday"]))

def create_person():
    person = {}
    person["Login"] = str(input("Введите логин:\n"))
    person["Password"] = str(input("Введите пароль:\n"))
    person["Name"] = str(input("Введите ФИО:\n"))
    person["Phone"] = str(input("Введите телефон:\n"))
    person["Email"] = str(input("Введите e-mail:\n"))
    person["Birthday"] = str(input("Введите дату рождения:\n"))
    person["Address"] = str(input("Введите адрес:\n"))
    return person

def create_message():
    message = {}
    message['FilePath'] = str(input("Введите путь до файла:"))
    if message['FilePath'] == "":
        message['FilePath'] = None
    message['Text'] = str(input("Введите текст сообщения:"))
    return message

def create_animal():
    animal = {}
    animal['Name'] = str(input("Введите кличку животного:\n"))
    animal['TypeID'] = int(
        input("Введите тип животного: 1-кошка, 2-собака, 3-попугай\n"))
    animal['Sex'] = int(input("Введите пол животного: 0-мужской, 1-женский\n"))
    animal['Comment'] = str(input("Введите комментарий:\n"))
    animal['Birthday'] = str(input("Введите дату рождения:\n"))
    return animal

def create_review():
    review = {}
    review["AnimalTypeID"] = int(
        input("Введите тип животного: 1-кошка\n2-собака\n3-попугай\n"))  # animaltype
    review["Body"] = str(input("Введите текст отзыва:\n"))
    return review

def create_order():
    order = {}
    order["AnimalID"] = int(input("Введите ID животного:"))
    orderdatestart = str(input("Введите дату заезда в отель в формате\nгггг-мм-дд: "))
    while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdatestart) == []:
        orderdatestart = input(("Неправильный формат! Введите дату заезда в отель в формате\nгггг-мм-дд: "))
    order["DateStart"] = orderdatestart
    orderdateend = str(
        input("Введите дату отъезда из отеля в формате\nгггг-мм-дд: "))
    while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdateend) == []:
        orderdateend = input(("Неправильный формат! Введите дату заезда в отель в формате\nгггг-мм-дд: "))
    order["DateEnd"] = orderdateend
    order["DeliveryToTheHotel"] = int(input("Вы согласны на доставку животного до отеля: 0-нет, 1-да "))
    if order["DeliveryToTheHotel"] == 1:
        order["FromDeliveryAddress"] = str(input("Введите адрес, откуда мы сможем забрать вашего питомца: "))
        order["FromDeliveryTime"] = str(input("Во сколько мы можем забрать вашего питомца: "))
    else:
        order["FromDeliveryAddress"] = None
        order["FromDeliveryTime"] = None
    order["DeliveryFromHotel"] = int(input("Вы согласны на доставку животного из отеля к вам: 0-нет, 1-да "))
    if order["DeliveryFromHotel"] == 1:
        order["ToDeliveryAddress"] = str(input("Введите адрес, куда мы можем привезти вашего питомца: "))
        order["ToDeliveryTime"] = str(input("Во сколько мы можем привезти вашего питомца: "))
    else:
        order["ToDeliveryAddress"] = None
        order["ToDeliveryTime"] = None
    order["Comment"] = str(input("Введите комментарий к заказу: "))
    return order
start_client()  # Запускаем функцию старта клиента. Вызов функции должен быть ниже, чем определение этой функции в файле
