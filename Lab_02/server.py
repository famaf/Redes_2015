#!/usr/bin/env python
# encoding: utf-8
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import optparse
import socket
import select
from connection import *
from constants import *


class AsyncServer(object):
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
        self.sock_serv.setblocking(0)
        self.directory = directory
        self.addr = addr
        self.poll = select.poll()

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        try:
            clients = {}
            self.poll.register(self.sock_serv.fileno(), select.POLLIN)
            while True:
                events = self.poll.poll()
                for fileno, event in events:
                    if fileno == self.sock_serv.fileno():
                        sock_clnt, addr = self.sock_serv.accept()
                        sock_clnt.setblocking(0)
                        self.poll.register(sock_clnt.fileno(), select.POLLIN)
                        connec = Connection(sock_clnt, self.directory,
                                            self.addr)
                        clients[sock_clnt.fileno()] = connec
                    else:
                        if event & select.POLLIN:
                            clients[fileno].handle_input()
                        elif event & select.POLLOUT:
                            clients[fileno].handle_output()
                        if clients[fileno].sock_closed():
                            self.poll.unregister(fileno)
                        else:
                            con = clients[fileno]
                            new_events = con.events()
                            self.poll.modify(fileno, new_events)

        except:
            self.poll.unregister(self.sock_serv.fileno())
            self.sock_serv.close()
            self.poll.close()


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

  server = AsyncServer(options.address, port, options.datadir)
  server.serve()

if __name__ == '__main__':
  main()