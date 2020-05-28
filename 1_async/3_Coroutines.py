#! /usr/bin/env python3
# -*- coding: utf-8 -*-


class AverageStopIterator(Exception):
    pass

def subgen():
    x = "Ready to accept message"
    message = yield x
    print("Received: ", message)

def average():
    count = 0
    sum = 0
    average = None
    while True:
        try:
            x = yield average
        except StopIteration:
            print("Done")
        except AverageStopIterator:
            print("Stopped")
            break
        else:
            count += 1
            sum += x
            average = round(sum / count, 2)

    return average


def main():
    try:
        gen = subgen()
        data = gen.send(None)
        print("From generator: ", data)
        gen.send("10")
    except StopIteration:
        pass

    print("\n")
    av = average()
    print("Average: ", av.send(None))
    print("Average: ", av.send(5))
    print("Average: ", av.send(6))
    print("Average: ", av.send(10))
    av.throw(AverageStopIterator)


if __name__ == '__main__':
    main()