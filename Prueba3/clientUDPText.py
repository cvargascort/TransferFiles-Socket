import socket
import sys

if len(sys.argv) == 3: 
    # Obtener "dirección IP del servidor" y también el "número de puerto" del argumento 1 y el argumento 2
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    print("Run like : python3 client.py <arg1 server ip 172.0.0.1> <arg2 server port 4444 >")
    exit(1)

# Create socket for server
s = socket. socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
print("¡Haga Ctrl + c para salir del programa!")

# Enviemos datos a través del protocolo UDP 
while True:
    send_data = input("Escriba algún texto para enviar = >");
    s.sendto(send_data. encode('utf-8'), (ip, port))
    print("\n\n 1. Cliente enviado: ", send_data, "\n\n")
    data, dirección = s.recvfrom(4096)
    print("\n\n 2. Cliente recibido:", data.decode('utf-8'), " \n\n")
# cerrar el socket
s.cerrar()