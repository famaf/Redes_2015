# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import os
import socket
from constants import *
import server
import select


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory, address):
        # Inicialización de conexión
        self.sock = socket
        self.dir = directory
        self.address = address
        self.buff_in = ''
        self.buff_out = ''
        self.connection_active = True
        self.remain_frag_slice = False
        self.size_request = 0
        self.file_open = False

    def es_nombre_valido(self, name_file):
        """
        Devuelve True si el nombre ingresado contiene caracteres validos
        o False en caso contrario.
        """
        nombre = set(name_file) - VALID_CHARS
        return nombre == set([])

    def err_msg(self, type_error):
        """
        Imprime el mensaje de error correspondiente.
        """
        self.buff_out += str(type_error)
        self.buff_out += SPACE + error_messages[type_error] + EOL

    def get_file_listing(self):
        """
        Lista los archivos de un directorio.
        """
        lista = os.listdir(self.dir)
        self.buff_out += str(CODE_OK) + SPACE + error_messages[CODE_OK] + EOL
        for x in lista:
            self.buff_out += x
            self.buff_out += EOL
        self.buff_out += EOL

    def get_metadata(self, name_file):
        """
        Devuelve el tamaño del archivo dado (en bytes).
        """
        is_valid_name = self.es_nombre_valido(name_file)
        file_exist = os.path.isfile(os.path.join(self.dir, name_file))

        if not is_valid_name:  # si el nombre de archivo es valido
            self.err_msg(INVALID_ARGUMENTS)

        elif not file_exist:
            self.err_msg(FILE_NOT_FOUND)

        # Error interno del servidor
        else:
            data = os.path.getsize(os.path.join(self.dir, name_file))
            self.buff_out += str(CODE_OK) + SPACE + error_messages[CODE_OK]
            self.buff_out += EOL + str(data) + EOL

    def get_slice_in_pieces(self):
        """
        Llena el buffer de salida con los datos del archivo especificado.
        """
        last_part = min(self.size_request, SIZE_READ)
        bytes_read = self.file_open.read(last_part)

        self.buff_out += str(len(bytes_read))
        self.buff_out += SPACE + bytes_read + EOL

        self.size_request -= len(bytes_read)

        self.remain_frag_slice = self.size_request != 0
        if not self.remain_frag_slice:
            self.buff_out += str(CODE_OK) + SPACE + EOL
            self.file_open.close()

    def get_slice(self, avl_file, offset, size):
        """
        Leer y muestra los datos del archivo ingresado desde el OFFSET hasta
        OFFSET + SIZE.
        """
        is_valid_name = self.es_nombre_valido(avl_file)
        file_exist = os.path.isfile(os.path.join(self.dir, avl_file))

        if not is_valid_name:
            self.err_msg(INVALID_ARGUMENTS)

        elif not file_exist:
            self.err_msg(FILE_NOT_FOUND)

        else:
            try:
                start_read = int(offset)
                self.size_request = int(size)
            except ValueError:
                self.err_msg(INVALID_ARGUMENTS)

            else:
                lenght_file = os.path.getsize(os.path.join(self.dir, avl_file))
                offset_plus = start_read > lenght_file
                size_plus = (start_read + self.size_request) > lenght_file
                if offset_plus or size_plus:
                    self.err_msg(BAD_OFFSET)
                else:
                    try:
                        self.file_open = open(os.path.join(self.dir, avl_file),
                                              'r')
                    except IOError:
                        print("El archivo no se pudo abrir.")
                        raise INTERNAL_ERROR

                    self.file_open.seek(start_read)
                    self.buff_out += str(CODE_OK) + SPACE
                    self.buff_out += error_messages[CODE_OK] + EOL

                    self.remain_frag_slice = True
                    self.get_slice_in_pieces()

    def quit(self):
        """
        Cierra la conexion al cliente.
        """
        self.buff_out += str(CODE_OK) + " Listo!" + EOL
        self.connection_active = False

    def analizar(self, command):
        """
        Analiza si el pedido esta bien escrito y si contiene la cantidad
        de argumentos necesarios para cada método.
        """
        args = command.split(SPACE)

        if args[0] == 'get_file_listing':
            if len(args) == 1:
                self.get_file_listing()
            else:
                self.err_msg(INVALID_ARGUMENTS)

        elif args[0] == 'get_metadata':
            if len(args) != 2 or args[1] == '':
                self.err_msg(INVALID_ARGUMENTS)
            else:
                self.get_metadata(args[1])

        elif args[0] == 'get_slice':
            if len(args) == 4:
                self.get_slice(args[1], args[2], args[3])
            else:
                self.err_msg(INVALID_ARGUMENTS)
        elif args[0] == 'quit':
            if len(args) == 1:
                self.quit()
            else:
                self.err_msg(INVALID_ARGUMENTS)
        else:
            self.err_msg(INVALID_COMMAND)

    def receive(self):
        """
        Obtiene el comando que ingresa el usuario.
        """
        rec = self.sock.recv(SIZE_READ)
        if len(rec) == 0:
            self.sock.close()
        self.buff_in += rec

    def handle_input(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        self.receive()
        # Separa el primer "pedido" del resto
        if EOL in self.buff_in:
            request, self.buff_in = self.buff_in.split(EOL, 1)
        # Se fija que no exista error tipo 100
            if NEW_LINE in request:
                self.err_msg(BAD_EOL)
         # Analiza el primer "pedido" recibido
            else:
                self.analizar(request)

    def handle_output(self):
        """
        Envia datos para ser recibidos por el cliente.
        """
        cant_bytes = self.sock.send(self.buff_out)
        if cant_bytes == 0:
            self.sock.close()
        self.buff_out = self.buff_out[cant_bytes:]
        if self.remain_frag_slice:
            self.get_slice_in_pieces()

    def sock_closed(self):
        """
        Cierra el socket del cliente.
        """
        if not (self.connection_active or self.buff_out):
            self.sock.close()
            return True
        else:
            return False

    def events(self):
        """
        Devuelve los eventos (POLLIN, POLLOUT) que le
        interesan a la conexion.
        """
        if self.connection_active:
            if self.buff_out:
                event = select.POLLOUT
            else:
                event = select.POLLIN
        else:
            event = select.POLLOUT

        return event
