# !/usr/bin/env python3

import socket
import sys
import threading
import time
import os
import random
import json

host="127.0.0.1"
port=65432
numConn=3
buffer_size = 1024

global Board,level,HBoard
Board = []
HBoard = []
#######################################################

def CreateBoard(level):
    global Board

    #4x4
    if level == '1':
        for i in range(0, 2):
            for j in range(0, 8):
                Board.append(j)
        print("Principiante")
    elif level == '2':
        #6x6
        for i in range(0, 2):
            for j in range(0, 18):
                Board.append(j)
        print("Avanzado")
    else:
        print("Error")
    #random.shuffle(Board)
    return  Board

def CreateHiddenBoard(level):
    # 4x4
    if level == '1':
        for i in range(0, 2):
            for j in range(0, 8):
                HBoard.append('-')
        #print("Principiante")
    elif level == '2':
        # 6x6
        for i in range(0, 2):
            for j in range(0, 18):
                HBoard.append('-')
        #print("Avanzado")
    else:
        print("Error")

    return HBoard

def PrintBoard(level,board):
    #os.system("clear")
    if level == '1':
        for i in range(1,17):
            print(board[i-1],end="")
            print("\t",end="")
            if i%4 == 0:
                print()
    elif level == '2':
        for i in range(1,37):
            print(board[i-1],end="")
            print("\t",end="")
            if i%6 == 0:
                print()
    else:
        print("Error al imprimir")

def GenRandIndex(level):
    if level == '1':
        return random.randrange(17)
    else:
        return random.randrange(37)

########################################################

def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr,listaconexiones])
            thread_read.start()
            gestion_conexiones(listaConexiones)
    except Exception as e:
        print(e)

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)

def SendToAll(Data,listaConexiones):
    print("Enviar a todos")
    for conn in listaConexiones:
        conn.sendall(b"$")
        data = conn.recv(buffer_size)
        conn.sendall(Data.encode())
        data = conn.recv(buffer_size)
    
def recibir_datos(Client_conn, Client_addr, listaConexiones):
    global Board,level,HBoard
    PlayerPoints = 0
    try:
        cur_thread = threading.current_thread()
        print("Recibiendo datos del cliente {} en el {}".format(Client_addr, cur_thread.name))
        
        print("Conectado a", Client_addr)        
        if Board :
            data = Client_conn.recv(buffer_size)
            #print ("Recibido,", data,"   de ", Client_addr)
            print("El tablero ha sido creado por otro usuario")
            #ETC: Error, tablero creado
            Client_conn.sendall(b"ETC") 
            print(level)
            data = Client_conn.recv(buffer_size)
            Client_conn.sendall(level.encode())
            data = Client_conn.recv(buffer_size)
            Client_conn.sendall((json.dumps(HBoard)).encode())
            PrintBoard(level,Board)
        else:
            data = Client_conn.recv(buffer_size)
            #print ("Recibido,", data,"   de ", Client_addr)
            level = data.decode()
            Board = CreateBoard(level)
            HBoard = CreateHiddenBoard(level)
            PrintBoard(level,Board)
            Client_conn.sendall(b" ")
        
        while True:
            #print("Esperando a recibir datos... ")
            data = Client_conn.recv(buffer_size)
            if not data:
                break
            Coords = data.decode()
            print(Coords)
            x1 = int((Coords.split(";")[0]).split(",")[0])
            y1 = int((Coords.split(";")[0]).split(",")[1])
            x2 = int((Coords.split(";")[1]).split(",")[0])
            y2 = int((Coords.split(";")[1]).split(",")[1])
            
            if level == '1':
                indice1 = (y1*4+x1)
                indice2 = (y2*4+x2)
            else:
                indice1 = (y1*6+x1)
                indice2 = (y2*6+x2)
                
            Cards = "x"
            if Board[indice1] != 'x':
                if Board[indice2] != 'x':
                    if int(Board[indice1]==Board[indice2]):
                        Cards = str(Board[indice1])+","+str(Board[indice2])+","+str(indice1)+","+str(indice2)
                        HBoard[indice1]=Board[indice1]
                        HBoard[indice2]=Board[indice2]
                        Board[indice1]="x"
                        Board[indice2]="x"
                        print(HBoard)
                    else:
                        Cards = str(Board[indice1])+","+str(Board[indice2])+","+str(indice1)+","+str(indice2)
                        
            if indice1 == indice2:
                Client_conn.sendall(b"SAMECARD")
            else:
                #Verificar carta volteada
                #print("Entro aqui")
                Client_conn.sendall(Cards.encode())
                data = Client_conn.recv(buffer_size)
                Client_conn.sendall((json.dumps(HBoard)).encode())
                data = Client_conn.recv(buffer_size)
                #print("Enviando respuesta a", Client_addr)
        
        #while True:
        #    data = conn.recv(1024)
        #    response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        #    if not data:
        #        print("Fin")
        #        break
        #    conn.sendall(response)
    except Exception as e:
        print(e)
    finally:
        Client_conn.close()



listaConexiones = []
#host, port, numConn = sys.argv[1:4]

#if len(sys.argv) != 4:
#    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
#    sys.exit(1)

serveraddr = (host, int(port))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)
