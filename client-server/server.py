import random
import string
import datetime
import json  # Подключаем библиотеку для преобразования данных в формат JSON
import socket
import os # Подключаем библиотеку для работы с функциями операционной системы (для проверки файла)
import pymongo
from bson.json_util import dumps, loads
from bson import json_util
import win32event
import win32api
from winerror import ERROR_ALREADY_EXISTS
from sys import exit
import threading

mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
dblist = mongoclient.list_database_names()
db = mongoclient["ChillForAnimals"]
def check_database():
    if "ChillForAnimals" in dblist:
        print("База данных найдена")
    else:
        db = mongoclient["ChillForAnimals"]
        creationdata = {"test":"test"}
        col = db["Persons"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["Animals"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["Reviews"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["Journals"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["Chat"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["Orders"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["ChatMessages"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        col = db["AnimalTypes"]
        col.insert_one(creationdata)
        col.delete_one(creationdata)
        print("База данных не найдена\nСоздана новая база данных")
client_count = threading.BoundedSemaphore(4)
def start_server():
    serv_sock = create_serv_sock(8080)
    cid = 0
    while True:
        client = accept_client_conn(serv_sock, cid)#сокет сервера и клиент айди
        client_sock = client[0]
        client_addr = client[1]#ip и порт
        t = threading.Thread(target=serve_client, args=(client_sock, cid, client_addr))#создает поток
        t.start()
        cid += 1
def create_serv_sock(serv_port):
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,  proto=0)
    serv_sock.bind(('', serv_port))
    serv_sock.listen()
    check_database()
    print('Сервер запущен')
    print('Ожидаем подключения')
    return serv_sock
def accept_client_conn(serv_sock, cid):
    client_sock, client_addr = serv_sock.accept()#подключение клиента к серверу
    print(f'Клиент #{cid} подключен 'f'{client_addr[0]}:{client_addr[1]}')#ip и порт
    client_count.acquire() # уменьшает счетчик (-1)
    print(client_count._value)
    return client_sock, client_addr
def serve_client(client_sock, cid, client_addr):#?????????????????вот тут код
    while True:
        if (client_count._value !=0):
            answer = fulfill_request(client_sock, client_addr, cid)
            if answer is None:
                client_count.release()#увеличивает значение счетчика (+1)
                print(f'Клиент #{cid} преждевременно отключился')
                break
            else:
                client_sock.send(bytes(json.dumps(answer, default = myconverter), 'UTF-8'))#отправка данных клиенту
        else:
            client_count.release()#увеличивает значение счетчика (+1)
            client_sock.send(bytes(json.dumps(None), 'UTF-8'))
            # client_sock.close()
            print(f'Клиент #{cid} отключен, т.к. сервер занят')
            break
def fulfill_request(clientConnection, clientAddress, cid):
    try:
        in_data = clientConnection.recv(4096)# Получение данных от клиента
    except:
        return None 
        
    msg = in_data.decode() # Декодирование данных от клиента
    data = json.loads(msg) # Преобразование данных из формата JSON в словарь Python
    answer = None 

    if data["command"] == 'bye': # Получена команда отключение клиента
        print("Клиент отключен....")
        add_operation_in_journal("bye", clientAddress)
        clientConnection.close() # Закрываем соединение с клиентом
    if data["command"] == 'stop': # Получена команда остановки сервера
        print("Отключаем сервер")
        add_operation_in_journal("stop", clientAddress)
        clientConnection.close() # Закрываем соединение с клиентом
        exit(0) # Выходим из программы
    if data["command"] == 'auth':
        print("Попытка авторизоваться")
        add_operation_in_journal("auth", clientAddress)
        if user_auth(data["login"], data["password"]):
            print("Попытка авторизоваться прошла успешно")
            token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
            x = db["Persons"].find_one({"Login":data["login"], "Password":data["password"]})
            x["Token"] = token
            x["DateOfIssueToken"] = datetime.datetime.now()
            db["Persons"].save(x)
            answer = {}
            answer["Auth"] = 1
            answer["Token"] = x["Token"]
            answer["UserName"] = x["Name"]
        else:
            print("Попытка авторизоваться прошла неудачно")
            answer = {}
            answer["Auth"] = 0
    if data["command"] == 'logout':
        db["Persons"].update({"Token" : data["token"]},{"$set": {"Token" : None,"DateOfIssueToken": None}})
        add_operation_in_journal('logout', clientAddress)
        print("Клиент вышел из профиля:", clientAddress)
    if data["command"] == 'changepswd':
        x = db["Persons"].find_one({"Token":data["token"]})
        if check_token(x):
            x["Password"] = data["password"]
            db["Persons"].save(x)
            add_operation_in_journal('changepswd', clientAddress)
            print("Попытка смены пароля прошла успешно ", clientAddress)
            answer = "Ваш пароль был успешно изменён"
        else:
            answer = "Вы не авторизованы"
    if data["command"] == 'addorder':
        print("Добавляем заказ")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('addorder', clientAddress)
            answer = add_order(person, data["object"])
        else:
            answer = "Вы не авторизированы"
    if data["command"] == 'addanimal':
        print("Добавляем животное")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('addanimal', clientAddress)
            answer = add_animal(person, data["object"])
        else:
            answer = "Вы не авторизированы"
    if data["command"] == 'readorders':
        print("Считываем список заказов")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('readorders', clientAddress)
            answer = read_orders(person, data["DateStart"], data["DateEnd"])
        else:
            answer == "Вы не авторизованы"
    if data["command"] == 'addreview':
        print("Добавляем отзыв")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('addanimal', clientAddress)
            answer = add_review(person, data["object"])
        else:
            answer = "Вы не авторизированы"
    if data["command"] == 'addmessage':
        print("Добавляем сообщение")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('addmessage', clientAddress)
            answer = add_message(person, data["object"])
        else:
            answer = "Вы не авторизированы"
    if data["command"] == 'readanimals':
        print("Считываем список животных")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('readanimals', clientAddress)
            answer = read_animals(person)
        else:
            answer == "Вы не авторизованы"
    if data["command"] == 'readjournals':
        print("Считываем список записей журнала")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('readjournals', clientAddress)
            answer = read_journal(person, data["animalid"])
        else:
            answer == "Вы не авторизованы"
    if data["command"] == 'readreviews':
        print("Считываем список отзывов")
        add_operation_in_journal('readreviews', clientAddress)
        answer = read_reviews()
    if data["command"] == 'readmessages':
        print("Считываем сообщения")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('readmessages', clientAddress)
            answer = read_msg(person, data["DateStart"], data["DateEnd"],data["Status"])
        else:
            answer == "Вы не авторизованы"
    if data["command"] == 'readanimalsinhotel':
        print("Считываем список животных")
        if check_token(data["token"]):
            person - find_by_token(data["token"])
            add_operation_in_journal('readanimalsinhotel', clientAddress)
            answer = read_animals_in_hotel(person)
        else:
            answer == "Вы не авторизованы"
    if data["command"] == 'lookaccountworker':
        print("Считываем данные профиля")
        if check_token(data["token"]):
            add_operation_in_journal('lookaccountworker', clientAddress)
            answer = look_account_worker(data["_id"])
        else:
            answer == "Вы не авторизованы"
    if data["command"] == 'lookaccount':
        print("Считываем данные профиля")
        if check_token(data["token"]):
            person = find_by_token(data["token"])
            add_operation_in_journal('lookaccount', clientAddress)
            answer = look_account(person)
        else:
            answer == "Вы не авторизованы"
    return answer
def find_by_token(token):
    for y in db["Persons"].find({"Token": token}):
        answer = y
    return answer
def check_token(token):
    if ((len(token)) > 0):
        col = find_by_token(token)
        chekingToken = col["Token"]
        if chekingToken == token:
            return True
    return False
def user_auth(login, password):
    col = db["Persons"]
    for x in col.find():
        if x["Login"] == login and x["Password"] == password:
            return True
        else:
            continue
    return False
def read_animals(person):
    answer = []
    col = db["Animals"]
    for x in col.find({"ClientID":person["_id"]}):
        print(x)
        answer.append(x)
    return answer
def read_reviews():
    answer = []
    col = db["Reviews"]
    for x in col.find():
        print(x)
        answer.append(x)
    return answer
def read_animals_in_hotel(person):
    answer = []
    col = db["Animals"]
    col1 = db["Orders"]
    for z in col1.find({"ClientID" : person["_id"], "DateStart": {"$lt": datetime.datetime.now()}, "DateEnd": {"$gte": datetime.datetime.now()}}):
        for y in col.find({"_id" : z["AnimalID"]}):
            print(y)
            answer.append(y)
    return answer
def read_journal(person, animalid):
    answer = []
    journals = db["Journals"]
    # animals = db["Animals"]
    orders = db["Orders"]
    if animalid != "":
        animal = db["Animals"].find_one({"_id":int(animalid)})
        for order in orders.find({"AnimalID":int(animalid)}):
            for journal in journals.find({"OrderID":order["_id"]}):
                journal["Animal"] = animal["Name"]
                print(journal)
                answer.append(journal)

        # for a in journals.find({"AnimalID":int(animalid)}):
        #     print(a)
        #     answer.append(a)
    else:
        
        for order in orders.find({"ClientID":person["_id"]}):
            for journal in journals.find({"OrderID":order["_id"]}):
                animal = db["Animals"].find_one({"_id":order["AnimalID"]})
                journal["Animal"] = animal["Name"]
                print(journal)
                answer.append(journal)
        # for animal in animals.find({"ClientID":person["_id"]}):
        #     for y in journals.find({"AnimalID":x["_id"]}):
        #         print(y)
        #         answer.append(y)
    return answer
def look_account(person):
    answer = []
    print(person)
    answer.append(person)
    return answer
def look_account_worker(workerid):
    col = db["Persons"]
    if workerid!="":
        answer = []
        for x in col.find({"_id": int(workerid), "State": 0}):
            print(x)
            answer.append(x)
    else:
        answer = []
        for x in col.find({"State": 0}):
            print(x)
            answer.append(x)
    return answer
def read_orders(person, stringdatestart, stringdateend):
    if (stringdatestart != "") & (stringdateend != ""):
        answer = []
        date1 = stringdatestart.split('-')
        date2 = stringdateend.split('-')
        from_date = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]))
        to_date = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]))
        for x in db["Orders"].find({"DateStart": {"$gte": from_date, "$lt": to_date}, "DateEnd": {"$gte": from_date, "$lt": to_date}, "ClientID":person["_id"]}):
            print(x)
            answer.append(x)
    else:
        answer = []
        col = db["Orders"]
        for x in col.find({"ClientID":person["_id"]}):
            print(x)
            answer.append(x)
    return answer
def read_msg(person, stringdatestart, stringdateend, status):
    answer = []
    col = db["ChatMessages"]
    for x in db["Chat"].find({"ClientID":person["_id"]}):
        chatid = x["_id"]
    if (status == 1):
        for x in col.find({"Chat._id":chatid , "Status":0}):
            print(x)
            answer.append(x)
            col.update( { "Status" : 0} , { "$set": { "Status" : 1} })
    elif (stringdatestart != "") & (stringdateend != ""):
        date1 = stringdatestart.split('-')
        date2 = stringdateend.split('-')
        from_date = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]), int(date1[3]), int(date1[4]))
        to_date = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]), int(date2[3]), int(date2[4]))
        for x in col.find({"Time": {"$gte": from_date, "$lt": to_date}, "Chat._id":chatid}):
            answer.append(x)
    else:
        for x in col.find({"Chat._id":chatid}):
            print(x)
            answer.append(x)
    return answer
def get_max_id(collection):
    col = db[collection]
    maxid = 0
    for x in col.find().sort("_id"):
        maxid = x["_id"]
    return maxid
def find_by_id(id, collection):
    col = db[collection]
    obj = {}
    for x in col.find():
        if x["_id"] == id:
            obj = x
    return obj
def add_animal(person, animal):
    newanimal={}
    newanimal["_id"] = (get_max_id("Animals")) + 1
    newanimal["Name"] = animal["Name"]
    newanimal["AnimalTypes"] = find_by_id(animal["TypeID"], "AnimalTypes")
    newanimal["Sex"] = animal["Sex"]
    newanimal["Comment"] = animal["Comment"]
    newanimal["Birthday"] = animal["Birthday"]
    newanimal["ClientID"] = person["_id"]
    newanimal["DelTime"] = None
    print(save_all("Animals", newanimal))
    return "Животное успешно добавлено."
def add_person(person):
    newperson = {}
    newperson["_id"] = (get_max_id("Persons")) + 1
    newperson["Token"] = None
    newperson["DateOfIssueToken"] = None
    newperson["State"] = 1
    newperson["Login"] = person["Login"]
    newperson["Password"] = person["Password"]
    newperson["Name"] = person["Name"]
    newperson["Phone"] = person["Phone"]
    newperson["Email"] = person["Email"]
    newperson["Birthday"] = person["Birthday"]
    newperson["Address"] = person["Address"]
    print(save_all("Persons", newperson))
    newchat = {}
    newchat["_id"] = (get_max_id("Chat")) + 1
    newchat["DelTime"] = None
    newchat["ClientID"] = newperson["_id"]
    print(save_all("Chat", newchat))
    return "Пользователь успешно зарегестрирован."
def add_order(person, order):
    neworder = {}
    neworder["_id"] = (get_max_id("Orders")) + 1
    neworder["Status"] = "В обработке"
    datest = order["DateStart"].split('-')
    dateend = order["DateEnd"].split('-')
    neworder["DateStart"] = datetime.datetime(int(datest[0]), int(datest[1]), int(datest[2]))
    neworder["DateEnd"] = datetime.datetime(int(dateend[0]), int(dateend[1]), int(dateend[2]))
    neworder["ClientID"] = person["_id"]
    neworder["AnimalID"] = order["AnimalID"]
    neworder["DeliveryToTheHotel"] = order["DeliveryToTheHotel"]
    neworder["FromDeliveryAddress"] = order["FromDeliveryAddress"]
    neworder["FromDeliveryTime"] = order["FromDeliveryTime"]
    neworder["DeliveryFromHotel"] = order["DeliveryFromHotel"]
    neworder["ToDeliveryAddress"] = order["ToDeliveryAddress"]
    neworder["ToDeliveryTime"] = order["ToDeliveryTime"]
    neworder["Comment"] = order["Comment"]
    neworder["DelTime"] = None
    neworder["Price"] = 5000
    db["Orders"].save(neworder)
    return "Заказ успешно добавлен."
def add_review(person, review):
    newreview = {}
    newreview["_id"] = (get_max_id("Reviews")) + 1
    newreview["AnimalTypes"] = find_by_id(review["AnimalTypeID"], "AnimalTypes")
    newreview["Body"] = review["Body"]
    newreview["AddTime"] = datetime.datetime.now()
    newreview["DelTime"] = None
    newreview["ClientID"] = person["_id"]
    print(save_all("Reviews", newreview))
    return "Отзыв успешно добавлен."
def add_message(person, message):
    newmessage = {}
    col = db["Chat"]
    for x in col.find({"ClientID":person["_id"]}):
        chat = x
    newmessage["_id"] = (get_max_id("ChatMessages")) + 1
    newmessage["Chat"] = chat
    newmessage["PersonID"] = person["_id"]
    newmessage["Time"] = datetime.datetime.now()
    newmessage["Text"] = message['Text']
    newmessage["FilePath"] = message['FilePath']
    newmessage["DelTime"] = None
    newmessage["Status"] = 0
    print(save_all("ChatMessages", newmessage))
    return "Сообщение успешно отправлено."
def save_all(collection, content):
    col = db[collection]
    col.insert_one(content)
    return content
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

class FileMutex:
    def __init__(self):
        self.mutexname = "chillforanimals_filemutex"
        self.mutex = win32event.CreateMutex(None, 1, self.mutexname)
        self.lasterror = win32api.GetLastError()
    def release(self):
        return win32event.ReleaseMutex(self.mutex)

mutex = FileMutex()
mutex.release()

def add_operation_in_journal(opeartion,clientAddress):
    import time
    mutex = FileMutex()
    date=datetime.datetime.now()
    row = str(opeartion) + "===" + str(clientAddress) + "===" + str(date) + '\n'
    while True:
        win32event.WaitForSingleObject(mutex.mutex, win32event.INFINITE )
        print(str(clientAddress) + " " + " зашёл")
        f = open('journal.txt', 'a')
        f.write(row)
        f.close()
        mutex.release()
        return
class singleinstance:#Ограничивает приложение одним экземпляром
    def __init__(self):
        self.mutexname = "testmutex_{b5123b4b-e59c-4ec7-a912-51be8ebd5819}" #GUID сгенерирован онлайн генератором
        self.mutex = win32event.CreateMutex(None, False, self.mutexname)
        self.lasterror = win32api.GetLastError()#извлекает значение кода последней ошибки вызывающего потока
    def aleradyrunning(self):
        return (self.lasterror == ERROR_ALREADY_EXISTS)
    def __del__(self):
        if self.mutex:
            win32api.CloseHandle(self.mutex) #закрывает дескриптор мьютекса

from sys import exit
myapp = singleinstance()
if myapp.aleradyrunning():
    print("Другой экземпляр этой программы уже запущен.")
    exit(0)
start_server() # Запускаем функцию старта сервера.
