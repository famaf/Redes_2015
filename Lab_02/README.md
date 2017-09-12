LABORATORIO 2: Asyncserver
==========================

>El objetivo de este laboratorio es adaptar el servidor hecho en el laboratorio
>anterior para que en vez de solo atender a un solo cliente, pueda atender
>a varios a la vez de forma concurrente.
>Vale aclarar que tomamos como base el codigo, del laboratorio 1. Por lo cual
>lo que hicimos fue adaptar todo el código.


server.py
---------
>Aquí lo que hicimos fue tomar como base el código dado por la cátedra, sobre el
>mecanismo poll y modificarlo (o adaptarlo) para que el funcionamiento sea
>correcto. Con esto nos referimos a que el servidor, dado una lista de clientes,
>debe atender de manera concurrente.
>Cada cliente se identifica por un file descriptor y un evento, el cual el
>servidor debe atender.
>Si el evento es *POLLIN*, quiere decir que el servidor va a recibir un comando
>por parte del cliente. Si el evento es POLLOUT, quiere decir que el servidor
>debe responder a un pedido del cliente que fue atendido por el servidor en un
>evento *POLLIN*.


connection.py
-------------
>Lo que hicimos en esta parte del proyecto fue dividir el trabajo del handler en
>dos partes (*handle_input* y *handle_output*) que se encargan de la recepción
>de pedidos y las respuestas a los mismos, respectivamente.
>Estos métodos son llamados en el servidor, ya que es este quien se encarga de
>atender pedidos y responderlos según que evento se haya registrado.
>Además, tuvimos que implementar algunos métodos para adaptar el funcionamiento,
>los cuales los nombraremos a continuación:

###get_slice_in_pieces
>Este método contiene el algoritmo del método *get_slice*, el cual fue
>implementado con la idea de que con un nuevo flag llamado *rec_slice*,
>se verifique si hay partes faltantes por enviar.

###keep_processing_get_slice
>Llama al método *get_slice_in_pieces*, siempre y cuando el flag *rec_slice*,
>le indique que quedan partes pendientes para enviar.

###slice_is_not_finished
>Es llamado desde el servidor y se utiliza para verificar el flag *rec_slice*
>de *Connection*

###sock_closed
>Cuando un cliente quiere hacer un *quit*, este método permite que el mismo
>se desconecte, por ende, desregistre de la lista de clientes; esto solo cuando
>*connection* este inactivo y el *buff_out* vacío.

###events
>Este método le permite dar a conocer al servidor que eventos están habilitados
>en un momento dado para algún cliente, ya sea *POLLIN* o *POLLOUT*.

###buff_wo_EOL
>Verifica si existe un EOL en el *buff_in* del *connection* del cliente.

###receive
>Recive los datos enviados por el cliente.

Dificultades encontradas y resoluciones
---------------------------------------
>Uno de los problemas que tuvimos fue con la concurrencia entre los clientes,
>lo cual fue solucionado en el archivo *server.py* con la implementación nueva
>del servidor para atender múltiples clientes, registando a cada cliente, y
>recorriendo la lista de eventos, para saber como actuar en cada caso.
>Para poder realizar esto, fue necesario la implementación del método *events*,
>explicado anteriormente.
>Una de las grandes dificultades fue entender como se debía comportar el
>servidor cuando tenia que enviar un *get_slice* de un archivo muy grande, y
>luego de haberlo hecho, adaptar el servidor para solucionar este problema.
>Debiamos hacer métodos que pudieran saber si se habia enviado todo lo pedido,
>y además que puedan enviar la respuesta por partes para no saturar los recursos
>disponibles.
>Por otro lado, debimos separar la recepción de datos del *handle_input* ya que
>nos traia problemas si recibiamos el comando por partes, por lo que se llama
>al método *receive* siempre que no exista un comando completo en *buff_in*.
