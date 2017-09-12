LABORATORIO 5: Proxy HTTP
=========================

>El siguiente esquema muestra la interaccion entre el proxy, cliente y servidor.

>cliente ---------------------> proxy -----------------> servidor
>              pedido                      pedido'
>        <----------------------       <-----------------
>            respuesta                   respuesta

> El objetivo de este laboratorio es poder implementar un proxy reverso HHTP,
>que pueda usarse como load balancer para multiples dominios.
>El proxy debe funcionar solo para los ip en el domain de tal forma que se
>conecte a las diferentes ip's para distribuir pedidos. Se usa elección al azar
>para que se conecte de manera balanceada a todas las ip's.
> La conexion de proxy y server siempre es *forward* desde que se crea hasta que
>muere, mientras que la conexión de cliente-proxy puede cambiar.
> Se utilizó la estructura de la cátedra para la implementación del servidor
>proxy sobre la cual no se realizó algún cambio significante o idea de
>implementacion distinta, sino que solo implementamos los metodos que se
>requerian.


proxy.py
--------

>Aquí se representa a un servidor proxy como una clase con diferentes atributos.
>Crea un socket como conexión entrante, y mantiene una lista de todas las 
>conexiones con las que el socket del proxy establece las conexiones. De esta
>manera, sirve a los hosts que se especifican.
>La tarea del proxy es manejar los datos de cada una de las conexiones hasta
>que cada una se cierre. El manejo de los datos implica que cada conexion esta
>representada con un file descriptor y su evento correspondiente, donde se debe
>encargar de procesar las conexiones, aceptar nuevas y eliminar otras que lo
>requieran. Cuando se genera una conexión, el proxy debe establecer una conexión
>saliente al hostname que se especifica.

>Los metodos implementados para generar el objeto proxy son los siguientes:

### connect
> Aquí lo que hicimos fue establecer una conexión con el *hostname* dado, el
>cual podia ser dado como *host:puerto* o solamente *host*, lo que hacemos es
>analizar si los *:* se encuentran en el *hostname* en ese caso establecemos
>la conexión con el host y ese puerto, si los *:* no están en *hostname*,
>asumimos el puerto como el 80, y el host como el hostname.

### remove_finished
> Aquí lo que hacemos es recorrer la lista de objectos Connection, analizando
>uno por uno, fijándonos si la connexián está lista para ser removida
>(su atributo *remove* tiene que estar seteado en *true*) y si no tiene nada
>en su buffer de salida. Llegados a cumplirse estos requisitos, eliminamos
>y cerramos dicha conexión.

### accept_new
> Aceptamos una nueva connexión y setearla como bloqueante, también le seteamos
>la tarea a *RequestHandlerTask* y la agregamos a la lista de conexiones.

### handle_events
> Se recorre la lista de eventos, fijándonos si el *fileno* de dicha lista se
>corresponde con el del *socket_master*, en ese caso aceptamos una nueva
>conexión, si no se corresponde, obtenemos la conexión que se corresponde con
>dicho *fileno* y chequeamos si es *POLLIN* o *POLLOUT*, en el primer caso
>recibimos los datos del socket y en el segundo caso, enviamos los datos que
>tengamos.

### connection_with_fd
> Aquí lo que hacemos es recorrer la lista de conexiones fijándonos
>cual se corresponde con el *file descriptor* pasado como argumento,
>cuando lo encuentro devuelvo la conexion correspondiente.

### polling_set
> Lo que se hace es crear un objeto *polleable* y registrarlo en principio
>como *POLLIN*, para luego recorrer la lista de conexiones fijandonos en el
>modo de la conexión, y registrar al objeto como corresponda, *POLLIN* en caso
>de que halla que recibir datos o *POLLOUT* en caso de que haya que enviar
>datos, si no es ninguno de estos casos, seteamos la conexion para que se
>removida.

### run
> Aquí lo que hacemos es una conjunción de todos los métodos antes mencionados.
>Se procesan las conexiones que tienen trabajo por hacer, se crea  un objeto
>*polleable*, se obtienen sus eventos, se manejan dichos eventos, y se eliminan
>aquellas conexiones que lo requieran.


connection.py
-------------

>Se define una conexión como una clase que es instanciada como un objeto
>cada vez que se crea una nueva. Esta clase es una abstracción de una conexión,
>en la cual se manejan los datos que hay en las colas de entrada y salida (las 
>colas son instanciadas en este modulo como objetos).
>Ademas se definen dos clases mas; *Forward*, la cual coloca los datos que
>contiene una conexion vieja en la cola de entrada, a la cola de salida de una
>conexión nueva, es decir, se escriben los datos en la conexion target.
>Y la clase *RequestHandlerTask* que se encarga de tomar el pedido del cliente y
>direccionarlo hacia el servidor.

>A cada conexion se le debe asignar una *task* para que sepa que tarea debe
>realizar. Esta *task*, procesa datos de entrada y escribe en el buffer de
>salida.

### Clase Connection

#### fileno
>retorna el *file descriptor* asociado al socket de cada conexion.

#### direction
> Aquí lo que hacemos es chequear si en la cola de salida de la conexion hay
>algun dato, si nos encontramos en este caso devolvemos *DIR_WRITE*, es decir,
>que hay datos para enviar, sino devolvemos *DIR_READ*, para esperar a que
>lleguen datos, y en el caso en que la conexión esté en un estado final o a
>punto o ya no tenga datos, se retorna *None*.

#### send
> Aquií mandamos todo lo que tengamos en el buffer de salida.

#### recv
> Aquí recibimos datos en la cola de entrada.

#### close
>Se encarga de cerrar el socket de la conexion y de avisarle al proxy que borre
>la misma de su lista de conexiones.

#### send error
>Utilizada para mandar mensajes de error durante la tarea asignada a la
>conexion.

### Clase Forward

> Inicializa sus datos y tiene un solo método.

#### apply

>Se encarga de retransmitir todos los datos que ingresan, hacia la conexión
>destino.

### Clase RequestHandlerTask

> Inicializa sus datos y tiene un solo método.

#### apply

>Como se dijo antes, toma pedido del cliente y direccionarlo hacia el servidor.
>Lee los datos de entrada de una conexión para obtener los datos de hacia donde
>se realiza el pedido.
>Al mismo tiempo se fija que sean correctos, y cuando obtiene el host de destino
>(mediante la búsqueda en las cabeceras de los datos de entradas), se encarga de
>balancear las cargas entre las diferentes direcciones del host solicitado.
>En este momento es necesaria una nueva conexión entre el proxy y el host
>solicitado, siendo necesario también, pasar los datos que llegaron al proxy,
>pero como se quiere que no haya conexiones persistentes se modifica el campo
>*Connection* a close.
>Esa es la única diferencia con respecto a los datos originales.
>Finalmente esa conexión de ahi en adelante se dedicará a transmitir los datos,
>es decir cumple la tarea de *Fordward*.