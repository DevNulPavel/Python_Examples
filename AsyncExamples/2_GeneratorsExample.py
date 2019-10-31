#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import select
import socket

tasks = []
toRead = {}
toWrite = {}

READ = 0
WRITE = 1

def server():
    # Создаем блокирующий сокет
    acceptSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    acceptSocket.bind(("localhost", 9999))
    acceptSocket.listen()

    # Создаем бесконечный цикл
    while True:
        # Дожидаемся, когда нам станет доступен новый прием соединения
        yield (READ, acceptSocket)
        # Принимаем соединение
        sock, addr = acceptSocket.accept()
        print("New connection from ", addr)

        # Ставим в обработку генератор обработки сокета
        tasks.append(clientCode(sock))


def clientCode(sock: socket.socket):
    # Бесконечный цикл обработки сокета
    while True:
        # Ждем доступности на чтение
        yield (READ, sock)
        data = sock.recv(4096)

        if data:
            # Ждем доступность на запись
            yield (WRITE, sock)
            sock.sendall(data)
        else:
            break

    # TODO: Надо ли удалять из списков, вроде бы нет?
    sock.close()


def main():
    # Создаем первый генератор сервера
    tasks.append(server())

    # Выполняем данный цикл, пока хоть где-то есть задания
    while any([tasks, toRead, toWrite]):
        # Пока нет никаких задач
        while not tasks:
            # Выбираем что мы можем читать или писать
            readyToRead, readyToWrite, _ = select.select(toRead.keys(), toWrite.keys(), [])

            # Перебираем все сокеты, готовые на запись
            for sock in readyToRead:
                # Добавляем генераторы, которые отвечают за работу данного сокета,
                # извлекая их из словаря, где ключ - это сокет
                generator = toRead.pop(sock)
                tasks.append(generator)

            for sock in readyToWrite:
                # Добавляем генераторы, которые отвечают за работу данного сокета,
                # извлекая их из словаря, где ключ - это сокет
                generator = toWrite.pop(sock)
                tasks.append(generator)

        try:
            # Извлекаем задачу
            task = tasks.pop(0)
            # Выполняем задачу
            type, sock = next(task)
            # В зависимости от того, что теперь должна ждать задача - возможности записи или чтения
            # добавляем в нужный список
            if type == READ:
                toRead[sock] = task
            if type == WRITE:
                toWrite[sock] = task
        except StopIteration:
            print("Complete with client")


if __name__ == '__main__':
    main()