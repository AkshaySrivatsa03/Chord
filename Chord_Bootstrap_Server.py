import socket
import threading

host = "glados.cs.rit.edu"
port = 15000
firstNode = ""
chord_exists = False

def transferToServer(conn, addr):
    global firstNode
    conn.send(str.encode(firstNode))
    conn.close()
    return None

def createChord(conn, addr):
    global firstNode
    global chord_exists

    mess1= "First"
    conn.send(str.encode(mess1))
    chord_exists = True

    mess2 = conn.recv(2048)
    firstNode = mess2.decode('utf-8')
    print("First Node is " + firstNode)

    conn.close()
    return None

def Main():
    global firstNode
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
    except socket.error as e:
        print(str(e))

    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        print("Client" + str(addr) + " has connected")
        if chord_exists == True:
            t = threading.Thread( target = transferToServer(conn, addr) )
        else:
            t = threading.Thread(target = createChord(conn, addr))

    sock.close()

Main()