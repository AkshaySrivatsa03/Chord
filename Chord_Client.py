import socket
import os
import hashlib

host = socket.gethostname()
IP = socket.gethostbyname(host)
port = 13000

# Gives the user a menu of options to decide future action
def menu():

    print("The following options are available - ")
    print("join : to join the chord ring, if not already joined")
    print("leave: to leave the chord ring, if already joined")
    print("insert : to insert a file")
    print("search : to search for a file")
    print("view : to view the details of the current server : ")
    print("kill : to kill the server")

    inp = input("Please select one of the above options : ")

    return inp

# The main method of the client
def Main():

    global host
    global port
    again = True

    while again:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port ))
        inp = menu()

        if inp == "search":
            data1 = sock.recv(2048)
            reply = data1.decode('utf-8')
            if reply == "go":
                sock.send(str.encode("search"))
                fileName = input("Please enter the name of the file you wish to look up")
                sock.send(str.encode(str(fileName)))
                data2 = sock.recv(2048)
                reply2 = data2.decode('utf-8')
                if reply2 == "no":
                    print("File was not found")

            again = False

        elif inp == "insert":
            sock.send(str.encode("insert"))
            data1 = sock.recv(2048)
            reply = data1.decode('utf-8')
            if reply == "go":
                fileName = input("Please enter the name of the file you wish to insert : ")
                sock.send(str.encode(fileName))
                data2 = sock.recv(2048)
                reply2 = data2.decode('utf-8')
                if reply2 == "fresh":
                    print("File has been inserted")
                else:
                    print("File already exists")
            again = False

        elif inp == "join" :
            sock.send(str.encode("join"))
            data = sock.recv(2048)
            reply = data.decode('utf-8')
            if reply == "success":
                print("Succesfully joined the ring")
            else:
                print("Was already a part of a ring")
            again = False

        elif inp == "leave":
            sock.send(str.encode("leave"))
            print("Successfully left the ring")
            again = False

        elif inp == "view":
            sock.send(str.encode("view"))
            again = False

        else:
            print("Invalid keyword entered. Pleaase try again")
            again = True
            sock.close()

    sock.close()

    return None

Main()