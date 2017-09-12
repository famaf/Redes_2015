LABORATORIO 1: HFTP
===================

>Para crear los comandos a los cuales el cliente tendrá acceso, definimos
>los métodos GFL (get_file_listing), GM (get_metadata), GS (get_slice) y quit,
>para no hacerlo en el método handle , lo que hicimos fue modularizarlas como
>otros métodos de la clase Connection, con lo cual quedará mucho más legible a
>la hora de encontrar un error, cada uno de los comandos
>(los llamaremos así, para no decir métodos y confundir, pero en realidad son
>métodos de la clase Connection).
>En cada uno de los comandos, están definidos los parámetros que ellos tomarán y
>las excepciones que llevarán a cabo, por algún error
>(intencional o "sin querer") del cliente.

server.py
---------
>Aquí se crea el socket del servidor y lo configura de tal forma que se conecte
>al puerto 19500 y se mantenga en interacción con los pedidos de un solo cliente
>a la vez(por ser secuencial).
>Además, se encarga de aceptar la conexión, creando así el socket del cliente,
>y generando la conexión que será manejada por el método *handle* en
>*connection.py.*
>Estos sockets permiten la interacción en la conexión entre ambos, enviando y
>respondiendo los pedidos, hasta la desconexión del cliente.

connection.py
-------------

### Recepción de pedidos y envío de respuestas

>Ante todo, connection se encarga de manejar la conexión entre el cliente
>y el servidor.
>En ella se definen los diferentes comandos que utilizará el cliente para
>interactuar con el servidor, de tal forma que el mismo no se corrompa por algún
>tipo de error del cliente en cuanto a la ejecución de algunos de los comandos;
>es decir que si se le pasa un comando que no esta bien redactado, el servidor
>sea capaz de reconocer un error y permitir nuevamente, sin cortar la conexión
>entre ambos, que el cliente pueda seguir interactuando con el servidor,
>a menos de que ocurra uno de los errores del tipo 1xx (con el cual el servidor
>deberá cerrarse de manera instantánea).
>El manejo de los pedidos y respuestas es realizado por el método *handle*.
>Es necesario que los pedidos del cliente se respondan de a uno a la vez, por lo
>que se decidió implementar un buffer de entrada (buffer_in) que se encarga de
>recibir todos los pedidos, separar el primero, analizarlo y responderlo, luego
>repitiendo el procedimiento con los pedidos siguientes.
>Debíamos ver que estos pedidos fueran realizados de manera correcta, lo cual
>conlleva a la definición del método *analizar*, que como su nombre indica,
>analiza si el pedido es un comando valido con su cantidad exacta de argumentos.
>Luego se llama al método correspondiente, y allí analiza si los argumentos son
>correctos. En caso contrario, responde con el mensaje de error.
>Luego de que el método tiene la respuesta al pedido, a traves de un buffer de
>salida *buff_out* que almacena la respuesta completa, las envía al cliente
>mediante *buffer_send* que envía los datos hasta que el buffer de salida este
>vacío.


### GFL

>Este comando es el encargado de listar los archivos disponibles en el servidor
>de forma dinámica, es decir, que si se borran o modifican los archivos mientras
>el server este activo, estos estarán actualizados.
>Este comando no toma ningún argumento, es decir, que cuando se le pasa un
>argumento o más, el servidor está preparado (por la implementación que nosotros
>hicimos) a responder de manera correcta (dando un mensaje de error) de acuerdo
>al protocolo por el cual nos estamos rigiendo.


### GM

>Este comando toma como argumento un archivo y se encarga de devolver la
>cantidad de bytes del mismo (que es el tamaño del archivo), siempre y cuando
>este exista, además de devolver *0 OK* (como mensaje de corroboración de que el
>archivo existe) antes de dar la cantidad de bytes; este comando al igual que el
>GFL está regido por el protocolo correspondiente, siendo el caso en el que si
>el cliente ingrese mal los parámetros, el servidor sepa contestar de la manera
>adecuada con los mensajes de error correspondientes, es decir, esta preparado
>para manejar errores del cliente en cuanto a las diversas formas de ejecutar
>este comando.


### GS

>Este comando recibe 3 argumentos (ARCHIVO, OFFSET, SIZE), y de lo que se
>encarga es de leer y mostrar por pantalla los datos que hay desde el OFFSET
>hasta OFFSET+SIZE que se le ha ingresado, siempre y cuando se tengan en cuenta
>las condiciones que esto conlleva, las cuales están explicadas en el enunciado
>del laboratorio, pero en la implementación se encuentran contempladas dichas
>problemáticas descriptas.
>Se toman en cuenta las diferentes formas en las que el cliente puede ingresar
>el comando con sus respectivos argumentos, por lo que cada una de esas
>posibilidades se controlan con la implementación.

### quit

>Lo único de lo que se encarga este comando es de cerrarle la conexión al
>cliente, reiterando nuevamente que las problemáticas que pudieran surgir en el
>uso de este comando, se han tenido en cuenta en la implementación.
>Un punto a tener en cuenta es que este comando al ejecutarse, además de listar
>en consola del cliente un mensaje OK listo!, saca de ejecución al cliente pero
>el servidor sigue en pie para seguir recibiendo pedidos.


Decisiones de diseño
--------------------

>En un principio pensamos en realizar todo el trabajo del manejo de recepción de
>pedidos y envíos hasta desconexión dentro del método *handle*, lo cual generaba
>un código muy largo y menos comprensible para nosotros mismos, por lo que
>decidimos comenzar a modularizar este método, y que el mismo llame a los nuevos
>implementados para realizar su tarea.
>De esta manera, al ir implementando cada uno de los comandos del cliente, nos
>dimos cuenta que íbamos a necesitar asimismo más métodos, por lo que seguimos
>modularizando el código de tal forma que logre una legibilidad mayor y sea mas
>comprensible su lectura.
>Por otro lado, así como decidimos implementar el buffer de entrada de pedidos,
>implementamos un buffer de salida, cuyos datos son enviados al cliente,
>por el método *send_buffer*.
>Con respecto a los mensajes de error, se decidió agregar métodos a la clase
>*Connection*, como por ejemplo *unknown_command*, *file_not_found*, etc, de tal
>manera que cada uno responda con el error correspondiente.
>Además decidimos definir un atributo *connection_active*, que indica si el
>servidor debe seguir recibiendo y analizando pedidos.

Dificultades encontradas y resoluciones
---------------------------------------

>Principalmente la mayor dificultad de este proyecto fue comenzar a
>familiarizarse con un nuevo lenguaje de programación como lo es python, aunque
>de alguna forma es comprensible a la hora de entender todos los métodos que se
>pueden utilizar de sus paquetes ya definidos, la sintaxis con la que se debe
>escribir, el uso de las variables, etc.
>Luego de comenzar a comprender un poco mas el lenguaje, el hecho de empezar a
>escribir código e implementar métodos, nos ayudaron a comprender de gran manera
>muchas cosas propias del lenguaje, ya que a medida que íbamos realizando el
>trabajo, pensábamos en métodos que podíamos necesitar para realizar alguna
>tarea y averiguábamos en tutoriales de python.
>Por eso, la mejor forma que tuvimos de resolver los problemas que se nos fueron
>presentando fue el hecho investigar sobre cosas que nos hacían falta.
>Ademas de la dificultad de comenzar a aprender python, estuvo también la
>dificultad del laboratorio, el entender como interactúan el cliente y el
>servidor por medio de una conexión, la toma de pedidos del servidor por parte
>del cliente y su respuesta adecuada, como también, además de que el servidor
>realice varias tareas como corresponde, debía ser robusto ante clientes que no
>ejecutaban bien los comandos, lo cual aumentó en cierto grado la dificultad de
>este proyecto, pero a medida que íbamos implementando, fuimos entendiendo
>mayormente en profundidad el funcionamiento del servidor.