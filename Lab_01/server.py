#!/usr/bin/env python
# encoding: utf-8
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $


import optparse
import socket
from connection import *
from constants import *


class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print("Serving %s on %s:%s." % (directory, addr, port))
        # Creamos el socket del servidor
        self.sock_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Configuración del socket
        self.sock_serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Asignamos el socket del servidor a DEFAUL_ADDR y DEFAULT_PORT
        self.sock_serv.bind((addr, port))
        # Socket a la espera o "escuchando" para conectarse con 1 cliente
        self.sock_serv.listen(1)

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """

        while True:
            # Acepta la conexión
            sock_clnt, addr = self.sock_serv.accept()
            # Crea la conexión con el cliente
            connec = Connection(sock_clnt, DEFAULT_DIR)
            # Atiende y maneja la conexión hasta que el cliente se desconecte
            connec.handle()


def main():
    """Parsea los argumentos y lanza el server"""
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port",
                      help=u"Número de puerto TCP donde escuchar",
                      default=DEFAULT_PORT)
    parser.add_option("-a", "--address",
                      help=u"Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option("-d", "--datadir",
                      help=u"Directorio compartido", default=DEFAULT_DIR)
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()

if __name__ == '__main__':
    main()
