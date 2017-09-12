# encoding: utf-8
import socket
import select
import logging

from connection import Connection, DIR_READ, DIR_WRITE, RequestHandlerTask

from queue import TWO_POINT


class Proxy(object):
    """
    Proxy HTTP
    """

    def __init__(self, port, hosts):
        """
        Inicializar, escuchando en port, y sirviendo los hosts indicados en
        el mapa `hosts`
        """

        #  Conexión maestra (entrante)
        master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master_socket.bind(('', port))
        logging.info("Listening on %d", port)
        master_socket.listen(5)
        self.host_map = hosts
        self.connections = []
        self.master_socket = master_socket
        #  AGREGAR estado si lo necesitan

    def run(self):
        """
        Manejar datos de conexiones hasta que todas se cierren
        """
        while True:
            self.handle_ready()
            p = self.polling_set()
            # poll
            events = p.poll()
            self.handle_events(events)
            self.remove_finished()
            # COMPLETAR: Quitar conexiones que pidieron que las cierren
            #  - Tienen que tener el remove prendido
            #  - OJO: que pasa si la conexion tiene cosas
            #         todavía en cola de salida?
            #  - Acordarse de usar el metodo close() de la conexion

    def polling_set(self):
        """
        Devuelve objeto polleable, con los eventos que corresponden a cada
        una de las conexiones.
        Si alguna conexión tiene procesamiento pendiente (que no requiera
        I/O), realiza ese procesamiento antes de poner la conexión en el
        conjunto.
        """
        p = select.poll()
        p.register(self.master_socket.fileno(), select.POLLIN)

        for connec in self.connections:
            if connec.direction() == DIR_READ:
                p.register(connec.fileno(), select.POLLIN)
            elif connec.direction() == DIR_WRITE:
                p.register(connec.fileno(), select.POLLOUT)
            elif connec.direction() is None:
                connec.remove = True

        return p
        # COMPLETAR. Llamadas a register que correspondan, con los eventos
        # que correspondan

    def connection_with_fd(self, fd):
        """
        Devuelve la conexión que coincida con el descriptor: fd
        """
        for connec in self.connections:
            if connec.fileno() == fd:
                return connec
        # COMPLETAR

    def handle_ready(self):
        """
        Hace procesamiento en las conexiones que tienen trabajo por hacer.
        Es decir, las que estan leyendo y tienen datos en la cola de entrada
        """
        for c in self.connections:
            # Hacer avanzar la maquinita de estados
            if c.input.data:
                #asigno task a cualquier conection
                c.task = c.task.apply(c)

    def handle_events(self, events):
        """
        Maneja eventos en las conexiones.
        events es una lista de pares (fd, evento)
        """
        for fileno, event in events:
            if fileno == self.master_socket.fileno():
                self.accept_new()
            else:
                connection = self.connection_with_fd(fileno)
                if event & select.POLLIN:
                    connection.recv()
                elif event & select.POLLOUT:
                    connection.send()
        # COMPLETAR:
        #   - Segun los eventos que lleguen hay que:
        #       * Llamar a self.accept_new() si hay una conexion nueva
        #       * Llamar a c.send / c.recv / c.close en las
        #         conexiones que corresponda

    def accept_new(self):
        """
        Acepta una nueva conexión
        """
        socket, address = self.master_socket.accept()
        socket.setblocking(0)
        connec = Connection(socket, address)
        connec.task = RequestHandlerTask(self)
        self.append(connec)
        # COMPLETAR
        #  - Crea una nueva instancia de conexion y la agrega.
        #  - le setea la tarea a RequestHandlerTask(self)

    def remove_finished(self):
        """
        Elimina conexiones marcadas para terminar
        """
        for connection in self.connections:
            if (len(connection.output.data) == 0) and connection.remove:
                self.connections.remove(connection)
                connection.close()
        # COMPLETAR

    def connect(self, hostname):
        """
        Establece una nueva conexion saliente al hostname dado. El
        hostname puede tener la forma host:puerto ; si se omite el
        :puerto se asume puerto 80.

        Aqui esta la unica llamada a connect() del sistema. No
        preocuparse por el caso de connect() bloqueante
        """
        if TWO_POINT in hostname:
            host, port = hostname.split(TWO_POINT)
        else:
            host, port = hostname, 80
        #conexion saliente

        sock_saliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_saliente.connect((host, port))
        connec = Connection(sock_saliente)
        self.append(connec)

        return connec
        # COMPLETAR (es util tener esto acá)

    def append(self, c):
        """
        Agrega una nueva conexion a la lista de conexiones existente
        """
        self.connections.append(c)
