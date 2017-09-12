LABORATORIO 4: ARP
====================

>El objetivo de este laboratorio es poder implementar el *Protocolo de
>Resolución de Direcciones (ARP)* de acuerdo a lo especificado por el *RFC 826*.
>Para realizar su tarea de encontrar la dirección de hardware(ethernet MAC) de
>su respectiva dirección IP, se envia un paquete *ARP request* por difusión,
> y espera que se le responda con la direccion MAC correspondiente a la IP.

node.h
------
>Aqui lo que hicimos fue declarar las funciones auxilares que creimos
>necesarias para la implementacion de las funciones *send_to_ip* y
>*receive_ethernet_packet*.
>Las funciones auxiliares son:
>*ip_index*
>*add_arp_table*.
>Además se declaró la estructura necesaria para recordar las direcciones de
>hardware correspondientes a las direcciones de red.
>Se declara aquí la tabla para que cada nodo tenga su tabla ARP propia,
>y pueda ser vista por las funciones que tienen que acceder a ella.

### arp_t
> La estructura de la tabla ARP consiste de dos arreglos (uno para las
>dirreciones IP y otro para las dirrecciones MAC), los arregos tienen un 
>tamaño fijo de 255, por lo especificado en el enunciado del laboratorio.
>Vale aclarar que ésta no es la resolución óptima, sino que sirve para
>satisfacer los requerimientos del laboratorio, lo óptimo seria que fuera
>dinámico.
>Además, la estructura contiene una variable llamada *count_register*, que
>especifica la cantidad de direcciones que se encuentran en la tabla.


arplab.cc
---------
>Aqui lo que hicimos fue declarar las estructuras:
>*ethernet_frame*: Este es el formato del marco ethernet que se manda por la
> red ethernet, especificado por el RFC826.
>*arp_packet*: Este es el paquete ARP que se manda a los host, de los cuales
> desconocemos su MAC, esto se hace por medio de difusion a los host conectados.

> Los campos de las estructuras *ethernet_frame* y *arp_packet* están definidos
>según el protocolo del RFC826.
>Vale aclarar que en la definicion de las 3 estructuras (incluyendo *arp_t*),
>siendo requisito del enunciado, se tuvo que colocar
>*__attribute__ ((__packed__))*.
>El funcionamiento de esta atribución a la estructura es que cuando un *packed*
>es usado en una estructura, esta comprime comprime el tamaño de cada uno de sus
>campos, alineando los bytes, unos seguidos de otros.


### ip_index
> Esta función esta hecha con el fin de saber si la dirreccion IP pasada como
>parámetro está en la tabla ARP, devolviendo como retorno el índice en donde se
>encuentran.
>En caso de que no esté, se retorna -1.
>Nunca puede darse el caso de que este solo la dirección IP o MAC, ya que se
>agregan ambas al mismo tiempo.

### add_arp_table
> Esta función agrega una nueva entrada a la tabla ARP (<IP, MAC>) y aumenta el
>*count_register*.

### send_to_ip
> Esta función se encarga de mandar PAQUETES a la IP pasada como parámetro,
>preguntando primero si la ip es conocida (es decir está en la tabla ARP),
>si es así, manda el PAQUETE al host que corresponde con la IP. Si la IP no se
>encuentra en la tabla, manda un paquete ARP por medio de difusión hacia los
>demás hosts, para saber cual es la MAC correspondiente a esa IP.

### receive_ethernet_packet
> Esta función se encarga de recibir los paquetes y analizarlos, descubriendo
>si es un paquete que le corresponde a ese host, o si es un paquete ARP
>preguntando si es él el que se corresponde con la IP adentro del paquete ARP.
>En caso de ser un paquete IP, lo recibe directamente. Y en caso de ser un
>paquete ARP, analiza si el paquete es un pedido para conocer la MAC o si es una
>respuesta de otro host, en el primer caso genera un paquete de respuesta
>ARP mandando (o comunicando) su MAC al host que mando el pedido, sino es ese
>caso actualiza su tabla ARP con la MAC recibida.

DECISIONES DE DISEÑO TOMADAS
----------------------------

>Principalmente, la decision que primero se tomó fue como implementar la tabla
>arp para cada nodo, ya que cada host en la red contiene un nodo con su propia
>tabla de direcciones. En un principio se pensó implementarla con un arreglo de
>pares (IP,MAC) pero finalmente decidimos hacerlo con dos arreglos donde uno
>guarda las direcciones *IP* y el otro guarda las direcciones *MAC*
>respectivamente, teniendo una variable *count_register* que lleva la cuenta de
>la cantidad de direcciones que hay en la tabla.
>Además, se definió una estructura *arp_table* global en *node.h*.
>Otra cosa que tuvimos en cuenta ya que el enunciado lo especificaba como
>consejo, fue que tratamos de implementar de manera muy parecida las funciones
>según el psedo-codigo del *RFC 826*.
>También se decidió modularizar en funciones al momento de saber si una
>dirección era conocida y al momento de actualizar la tabla ARP, implementando
>las funciones *ip_index* y *add_arp_table*.

DIFICULTADES ENCONTRADAS Y RESOLUCION DE LAS MISMAS
---------------------------------------------------

>Al momento de recibir paquetes, los datos llegaban con información diferente a
>la esperada. Esto simplemente se daba por un uso incorrecto de *htons* y
>*ntohs*.
>Una vez corregido esto, teniamos el problema de que los nodos docentes llegaban
>a 2/5 y nuestros nodos estaban en 0/5.
>El principio de la solución fue cambiar la declaración del marco ethernet
>y paquete arp, en l función *send_to_ip*, ya que los declarabamos como punteros
>a estructuras en vez de estructuras directamente.
>Realizando estos cambios, se logró que los nodos docentes llegaran a un estado
>de 5/5, pero nuestros nodos seguien en 0/5.
>Además de algunos cambios mínimos en *send_to_ip* y *receive_ethernet_packet*,
>lo que trajo grande cambios al funcionamiento del programa fue que se cambió de
>lugar la definición y declaración de la estrcutura arp_t para que cada nodo
>tenga su tabla correspondiente, y se agregó el campo *count_register* dentro de
>la estructura en vez de que sea una variable global independiente,
>También se cambió el orden de los campos de la estructura del paquete ARP.
>Luego de estas modificaciones se logro que todos los nodos de la red conocieran
>las direcciones correspondientes a cada host, obteniendo un resultado de 5/5
>en cada uno de los nodos.