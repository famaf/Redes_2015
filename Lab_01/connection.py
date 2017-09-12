# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import os
import socket
from constants import *
import server


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        # Inicialización de conexión
        self.sock = socket
        self.dir = directory
        self.buff_in = ''
        self.buff_out = ''
        self.connection_active = True

    def es_nombre_valido(self, name_file):
        """
        Devuelve True si el nombre ingresado contiene caracteres validos
        o False en caso contrario.
        """
        nombre = set(name_file) - VALID_CHARS
        return nombre == set([])

    def send_buffer(self):
        """
        Envia datos para ser recibidos por el cliente.
        """
        while self.buff_out:
            cant_bytes = self.sock.send(self.buff_out)
            assert cant_bytes > 0
            self.buff_out = self.buff_out[cant_bytes:]

    def unknown_command(self):
        """
        Mensaje de comando inválido.
        """
        self.buff_out += str(INVALID_COMMAND)
        self.buff_out += space + error_messages[INVALID_COMMAND] + EOL
        self.send_buffer()

    def wrong_arg_q(self):
        """
        Mensaje de argumentos inválidos.
        """
        self.buff_out += str(INVALID_ARGUMENTS)
        self.buff_out += space + error_messages[INVALID_ARGUMENTS] + EOL
        self.send_buffer()

    def file_not_found(self):
        """
        Mensaje de archivo inexistente.
        """
        self.buff_out += str(FILE_NOT_FOUND)
        self.buff_out += space + error_messages[FILE_NOT_FOUND] + EOL
        self.send_buffer()

    def bad_offset(self):
        """
        Mensaje de posicion inexistente en un archivo.
        """
        self.buff_out += str(BAD_OFFSET)
        self.buff_out += space + error_messages[BAD_OFFSET] + EOL
        self.send_buffer()

    def bad_eol(self):
        """
        Mensaje de que se encontro un caracter r\n fuera de un terminador
        de pedido EOL.
        """
        self.buff_out += str(BAD_EOL)
        self.buff_out += space + error_messages[BAD_EOL] + EOL
        self.send_buffer()

    def get_file_listing(self):
        """
        Lista los archivos de un directorio.
        """
        try:
            lista = os.listdir(self.dir)
        except:
            print('INTERNAL SERVER ERROR')
            raise INTERNAL_ERROR
        else:
            self.buff_out += "0 OK" + EOL
            for x in lista:
                self.buff_out += x
                self.buff_out += EOL
            self.buff_out += EOL
            self.send_buffer()

    def get_metadata(self, name_file):
        """
        Devuelve el tamaño del archivo dado (en bytes).
        """
        is_valid_name = self.es_nombre_valido(name_file)
        file_exist = os.path.isfile(os.path.join(self.dir, name_file))

        if not is_valid_name:  # si el nombre de archivo es valido
            self.wrong_arg_q()

        elif not file_exist:
            self.file_not_found()

        # Error interno del servidor
        else:
            try:
                data = os.path.getsize(os.path.join(self.dir, name_file))
            except:
                print('INTERNAL SERVER ERROR')
                raise INTERNAL_ERROR
            else:
                self.buff_out += "0 OK" + EOL + str(data) + EOL
                self.send_buffer()

    def get_slice(self, avl_file, offset, size):
        """
        Leer y muestra los datos del archivo ingresado desde el OFFSET hasta
        OFFSET + SIZE.
        """
        file_exist = os.path.isfile(os.path.join(self.dir, avl_file))

        if not file_exist:
            self.file_not_found()
        else:
            try:
                offset2 = int(offset)
                size2 = int(size)
            except ValueError:
                self.wrong_arg_q()

            else:
                size_file = size2
                start_read = offset2
                len_file = os.path.getsize(os.path.join(self.dir, avl_file))
                offset_plus = start_read > len_file
                size_plus = (start_read + size_file) > len_file
                if offset_plus or size_plus:
                    self.bad_offset()
                else:
                    try:
                        file_open = open(os.path.join(self.dir, avl_file), 'r')
                    except IOError:
                        print("el archivo no se pudo abrir")
                        raise INTERNAL_ERROR

                    file_open.seek(start_read)
                    self.buff_out += "0 OK" + EOL

                    remain = size_file

                    while remain > 0:
                        last_part = min(remain, SIZE_READ)
                        bytes_read = file_open.read(last_part)

                        self.buff_out += str(len(bytes_read))
                        self.buff_out += space + bytes_read + EOL

                        remain -= len(bytes_read)
                        self.send_buffer()

                    self.buff_out += "0 " + EOL
                    self.send_buffer()

    def quit(self):
        """
        Cierra la conexion al cliente.
        """
        self.buff_out += str(CODE_OK) + " Listo!" + EOL
        self.send_buffer()
        self.sock.close()
        self.connection_active = False

    def analizar(self, command):
        """
        Analiza si el pedido esta bien escrito y si contiene la cantidad
        de argumentos necesarios para cada método.
        """
        c_tmp = command.split(space)

        if c_tmp[0] == 'get_file_listing':
            if len(c_tmp) == 1:
                self.get_file_listing()
            else:
                self.wrong_arg_q()

        elif c_tmp[0] == 'get_metadata':
            if len(c_tmp) != 2 or c_tmp[1] == '':
                self.wrong_arg_q()
            else:
                self.get_metadata(c_tmp[1])

        elif c_tmp[0] == 'get_slice':
            if len(c_tmp) == 4:
                self.get_slice(c_tmp[1], c_tmp[2], c_tmp[3])
            else:
                self.wrong_arg_q()
        elif c_tmp[0] == 'quit':
            if len(c_tmp) == 1:
                self.quit()
            else:
                self.wrong_arg_q()
        else:
            self.unknown_command()

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """

        # Maneja recepciones y envíos hasta desconexión

        while self.connection_active:
            # Recibe datos hasta recibir un EOL
            while EOL not in self.buff_in:
                rec = self.sock.recv(SIZE_READ)
                self.buff_in += rec
            # Separa el primer "pedido" del resto
            request, self.buff_in = self.buff_in.split(EOL, 1)
            # Se fija que no exista error tipo 100
            if new_line in request:
                self.bad_eol()
            # Analiza el primer "pedido" recibido
            else:
                self.analizar(request)
        # Cerramos el socket en desconexión
        self.sock.close()
