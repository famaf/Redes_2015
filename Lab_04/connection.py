# encoding: utf-8
# $Rev: 512 $

"""
Módulo que provee manejo de conexiones genéricas
"""
import random
from urlparse import urlparse
from socket import error as socket_error
import logging

from queue import Queue, ProtocolError
from queue import BAD_REQUEST, SEPARATOR, TWO_POINT, SPACE, EMPTY, SLASH

import config

# Estados posibles de la conexion
DIR_READ = +1  # Hay que esperar que lleguen más datos
DIR_WRITE = -1  # Hay datos para enviar

class Connection(object):
    """
    Abstracción de conexión. Maneja colas de entrada y salida de datos,
    y una funcion de estado (task). Maneja tambien el avance de la maquina de
    estados.
    """

    def __init__(self, fd, address=''):
        """
        Crea una conexión asociada al descriptor fd
        """
        self.socket = fd
        self.task = None  # El estado de la maquina de estados
        self.input = Queue()
        self.output = Queue()
        self.remove = False  # Esto se seta a true para pedir
                             # al proxy que desconecte
        self.address = address

    def fileno(self):
        """
        Número de descriptor del socket asociado.
        Este metodo tiene que existir y llamarse así para poder pasar
        instancias de esta clase a select.poll()
        """
        return self.socket.fileno()

    def direction(self):
        """
        Modo de la conexión, devuelve uno de las constantes DIR_*; también
        puede devolver None si el estado es el final y no hay datos para
        enviar.
        """
        # COMPLETAR
        if len(self.output.data) != 0:
            return DIR_WRITE
        elif self.task is not None:
            return DIR_READ
        else:
            return None

    def recv(self):
        """
        Lee datos del socket y los pone en la cola de entrada.
        También maneja lo que pasa cuando el remoto se desconecta.
        Aqui va la unica llamada a recv() sobre sockets.
        """
        # COMPLETAR
        data = self.socket.recv(4096)
        if len(data) > 0:
            self.input.put(data)
        else:
            self.remove = True

    def send(self):
        """
        Manda lo que se pueda de la cola de salida
        """
        # COMPLETAR
        if len(self.output.data) != 0:
            cant_bytes = self.socket.send(self.output.data)
            self.output.remove(cant_bytes)

    def close(self):
        """
        Cierra el socket. OJO que tambien hay que avisarle al proxy que nos
        borre.
        """
        self.socket.close()
        self.socket = None
        self.remove = True
        self.output.clear()

    def send_error(self, code, message):
        """
        Funcion auxiliar para mandar un mensaje de error
        """
        logging.warning("Generating error response %s [%s]",
                        code, self.address)
        self.output.put("HTTP/1.1 %d %s\r\n" % (code, message))
        self.output.put("Content-Type: text/html\r\n")
        self.output.put("\r\n")
        self.output.put("<body><h1>%d ERROR: %s</h1></body>\r\n" %
                        (code, message))
        self.remove = True


class Forward(object):
    """
    Estado: todo lo que venga, lo retransmito a la conexión target
    """

    def __init__(self, target):
        self.target = target

    def apply(self, connection):
        # COMPLETAR
        # Considerar que hacer si el otro cierra
        # la conexion (la cola de entrada va a estar vacia)
        # Esto puede devolver
        #  - self, cuando hay que seguir retransmitiendo
        #  - None cuando no hay que hacer mas nada con esta conexion
        # en el futuro
        if len(connection.input.data) != 0:
            self.target.output.put(connection.input.data)
            connection.input.clear()
            return self
        else:
            return None


class RequestHandlerTask(object):

    def __init__(self, proxy):
        self.proxy = proxy
        ### Agregar cosas si hace falta para llevar estado interno.
        # Puede que les convenga llevar
        self.host = None
        self.url = None
        self.method = None
        self.protocol = None
        self.number = 0

    def apply(self, connection):
        # COMPLETAR
        # Parsear lo que se vaya podiendo de self.input (utilizar los metodos
        # de Queue). Esto puede devolver
        # - None en caso de error, por ejemplo:
        #    * hubo un error de parseo
        #    * la url no empieza con http://
        #      (es decir, no manejamos este protocolo) (error 400 al cliente)
        #    * Falta un encabezado Host y la URL del pedido tampoco tiene host
        #      (error 400 al cliente)
        #    * Nos pidieron hacer proxy para algo que no esta en la
        #      configuracion (error 403 al cliente)
        # - Una instancia de Forward a una nueva conexion si se puede proxyar
        #    En este caso también hay que crear la conexion y
        #    avisarle al Proxy()

        if (self.method, self.url, self.protocol is None, None, None):
            self.method, self.url, self.protocol = connection.input.read_request_line()

        if (self.method, self.url, self.protocol is not None, None, None):
            if connection.input.parse_headers():
                parse_url = urlparse(self.url)
                hostname = parse_url[1]
                path = parse_url[2]
                for i in range(len(connection.input.headers)):
                    if(connection.input.headers[i][0] == 'Host'):
                        original_host = connection.input.headers[i][1][1:]
                        self.host = connection.input.headers[i][1][1:]
                    elif(connection.input.headers[i][0] == 'Connection'):
                        connection.input.headers[i][1] = ' close'
                if self.protocol is 'HTTP/1.0' and hostname is EMPTY:
                    connection.send_error(400, "Falta Host")
                if self.protocol is 'HTTP/1.0' and hostname:
                    self.host = hostname

                if self.host not in config.HOSTS:
                    connection.send_error(403, "Prohibido")
                else:
                    ran_num = random.randrange(0, len(config.HOSTS[self.host]))
                    ip = config.HOSTS[self.host][ran_num]
                    new_connection = self.proxy.connect(ip)
                    if path:
                        new_req = SPACE.join([self.method, path, self.protocol])
                    else:
                        new_req = SPACE.join([self.method, SLASH, self.protocol])
                    new_req += SEPARATOR
                    if self.protocol is 'HTTP/1.0':
                        new_req += 'Host'
                        new_req += TWO_POINT
                        new_req += self.host
                        new_req += SEPARATOR
                    new_connection.output.put(new_req)

                    new_req = EMPTY
                    for header in connection.input.headers:
                        new_req += header[0]
                        new_req += TWO_POINT
                        new_req += header[1]
                        new_req += SEPARATOR

                    new_connection.output.put(new_req)
                    new_connection.output.put(SEPARATOR)

                    new_connection.task = Forward(connection)
                    return new_connection.task
            else:
                return self
        else:
            return self
