LABORATORIO 5: DIAGRAMA DE TRANSICIÓN DE ESTADOS DE TCP
=======================================================

>El objetivo de este laboratorio es implementar el diagrama de transición de
>estados de TCP del RFC 793. Es útil saber esto ya que nos permite obtener
>paquetes con informacion de la red. Para esto debemos generar una conexión TCP
>(este protocolo es orientado a la conexión, y debe haber un acuerdo entre
>dos partes en la red que quieran comunicarse para poder establecerla, y ademas
>es full duplex, ya que ambos extremos deben ser cerrados independientemente) en
>la que durante el tiempo de vida de la misma, los paquetes captados de la red
>dirán a que estado ir durante la conexion a través de las flags (indicadas mas
> adelante), es decir conociendo la información de los encabezados de los
>paquetes.
>Para poder capturar esta información se usan herramientas de red, como es el
>*sniffer*, que toma los paquetes de datos de la placa de red.
>En cuanto a los encabezados de los paquetes que determinan la transición de
>estados en diferentes momentos durante la conexión, tienen 6 flags (4 usados
para este laboratorio), ellos son: ACK, RST, SYN, FIN.


Transición de estados
---------------------

>Primero que todo para cambiar de estado, hay que diferenciar el caso en el que
>se realice el envio de datos con alguna o algunas flags o el caso en el que los
>datos junto con las flags sean recibidas.
>Una vez sabido esto (mediante la comparación de si la dirección *my_adress* es
>de destino u origen), la transición dependerá del estado actual en el que nos
>encontramos. Es por eso que se analizan todos los estados posibles.
>Una vez que se conoce sitúa en el estado actual, hay que saber a que estado ir,
> y para saber esto se deben leer las flags contenidas en el paquete, y se
>decide (siguiendo el diagrama) a que estado se debe pasar.


Dificultades encontradas y soluciones
-------------------------------------

>Hubo casos en los que no se seguía bien la transición de estados ya que
>se analizaba la transición tanto en el envio y recepción de ciertas flags,
>como por ejemplo la transición del estado *SYN SENT* a *ESTABLISHED*, que
>según el diagrama puede darse tanto con envio como con recepción.
>Para solucionar esto, se nos dijo darle prioridad a la recepción y no analizar
>los casos de envio.