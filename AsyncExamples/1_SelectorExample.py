#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import selectors


selector = selectors.DefaultSelector()


def startServer():
    # Создаем неблокирующий сокет
    acceptSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptSocket.setblocking(False)  # acceptSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    acceptSocket.bind(("localhost", 9999))
    acceptSocket.listen()

    # Добавляем этот неблокирующий сокет в селектор на ожидание нового подключения
    selector.register(acceptSocket, selectors.EVENT_READ, (accepted, None))


def accepted(acceptSocket: socket.socket, _):
    # раз наступило данное событие, значит мы можем создать уже рабочий клиент-сервер сокет
    sock, addr = acceptSocket.accept()
    print("New connection from ", addr)

    # Регистрируемся на события доступности чтения данных из сокета
    selector.register(sock, selectors.EVENT_READ, (dataReadAvailable, None))


def dataReadAvailable(sock: socket.socket, _):
    # Данные поступили, значит можем начинать их читать
    newData = sock.recv(4096)
    # Если данные есть, значит сокет не отвалился
    if newData:
        # Теперь модифицируем наш селектор на возможность отправки данных
        selector.modify(sock, selectors.EVENT_WRITE, (dataWriteAvailable, newData))
    else:
        # Иначе разрегистрируемся и закрываем сокет
        selector.unregister(sock)
        sock.close()


def dataWriteAvailable(sock: socket.socket, data):
    # Заново регистрируемся на чтение
    selector.modify(sock, selectors.EVENT_READ, (dataReadAvailable, None))
    # Отправляем данные
    sock.sendall(data)


def main():
    # Запускаем сервер
    startServer()
    print("Server started")

    # EventLoop работа
    while True:
        # Получаем список ивентов
        events: selectors.SelectSelector = selector.select()
        # Перебираем события, которые произошли
        for key, eventsMask in events:
            # Переменные в key: fileobj, fd, events (ивенты, которые могли бы быть), data
            # eventsMask - битовая маска событий которые готовы на данном дескрипторе
            file = key.fileobj
            callback, data = key.data
            callback(file, data)

    selector.close()


if __name__ == '__main__':
    main()
