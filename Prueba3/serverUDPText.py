import socket
import sys

if len(sys.argv) == 3: # Obtener "dirección IP del servidor" y también el "número de puerto" del 
    #argument 1 and argument 2
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    print("Run like : python3 server.py <arg1:server ip:this system IP 172.0.0.1> <arg2:server port:4444 >")
    exit(1)

# Create a UDP socket
s = socket. socket(socket.AF_INET, socket.SOCK_DGRAM)
# Enlazar el socket al puerto
server_address = (ip, port)
s.bind(server_address)
print("¡¡Haga Ctrl+c para salir del programa!!")

while True: 
    print("######## El servidor está escuchando #######")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Servidor recibido: ", data.decode('utf-8'), " \n\n")
    send_data = input("Escriba algún texto para enviar = > ")
    s.sendto(send_data.encode('utf-8'), address)
    print("\n\n 1. Servidor enviado: ", send_data,"\n\n")