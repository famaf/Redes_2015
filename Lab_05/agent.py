from aimara.core import agent

time = 0

ACK_FLAG = "A"
SYN_FLAG = "S"
FIN_FLAG = "F"
RST_FLAG = "R"


# COMPLETAR: Reemplazar la traza vacia por una traza generada
# por el programa pcap2py.py, por ejemplo la traza trace_test1.py
# provista en el kickstart.
trace = [
]


def host(self, perception):
    """
      Retorna el nuevo estado de la conexion TCP en el diagrama de estado.
      Los estados posibles son:
      S = Closed | Listen | SynReceived | SynSent | Established | FinWait1 |
          FinWait2 | Closing | TimeWait | CloseWait | LastAck | Stop
    """
    global time
    global trace
    my_address = perception["my_address"]
    #  Estado actual de la conexion.
    state = perception["state"]

    #  Extrae de la traza el mensaje enviado, Stop si se termino la traza
    message = agent.types.Nothing()
    if time < len(trace):
        m = trace[time]
    else:
        return agent.types.Action(sent_message=message,
                                  new_state=agent.types.Stop())

    if trace[time]["src"] == my_address:
        message = agent.types.Segment(
            flags=agent.types.Flags(syn=m["syn"], ack=m["ack"], fin=m["fin"],
                                    rst=m["rst"]))

    flags = ""
    if m["ack"]:
        flags += ACK_FLAG
    if m["fin"]:
        flags += FIN_FLAG
    if m["rst"]:
        flags += RST_FLAG
    if m["syn"]:
        flags += SYN_FLAG

    if m["dst"] == my_address:

        # Caso mensaje recibido
        # COMPLETAR: Actualizar la maquinda de estado:
        # A partir del estado actual y los flags TCP
        # se debe dedicir el nuevo estado del diagrama de estado
        # - state.label obtiene un string con el nombre del estado
        #   por ej: state.label == "SynSent" determina si el estado es SynSent
        # - El modulo agent.types provee los diferentes estados posibles
        #   por ejemplo: state = agent.types.Established()
        # elif state.label == "Closed":
        #     state = agent.types.Closed()

        if state.label == "Closed":
            pass

        elif state.label == "Listen":
            if SYN_FLAG in flags:
                state = agent.types.SynReceived()

        elif state.label == "SynReceived":
            if RST_FLAG in flags:
                state = agent.types.Listen()
            elif ACK_FLAG in flags:
                state = agent.types.Established()

        elif state.label == "SynSent":
            if time == 0:
                state = agent.types.Closed()
            elif SYN_FLAG in flags and ACK_FLAG in flags:
                state = agent.types.Established()
            elif SYN_FLAG in flags:
                state = agent.types.SynReceived()

        elif state.label == "Established":
            if FIN_FLAG in flags:
                state = agent.types.CloseWait()

        elif state.label == "FinWait1":
            if FIN_FLAG in flags:
                state = agent.types.Closing()
            elif ACK_FLAG in flags:
                state = agent.types.FinWait2()

        elif state.label == "FinWait2":
            if FIN_FLAG in flags:
                state = agent.types.TimeWait()

        elif state.label == "Closing":
            if ACK_FLAG in flags:
                state = agent.types.TimeWait()

        elif state.label == "TimeWait":
            if time == 0:
                state = agent.types.Closed()

        elif state.label == "LastAck":
            if ACK_FLAG in flags:
                state = agent.types.Closed()

        elif state.label == "CloseWait":
            pass

    elif m["src"] == my_address:

        # Caso mensaje enviado
        # COMPLETAR: Actualizar la maquinda de estado:
        # A partir del estado actual y los flags TCP se debe dedicir el
        # nuevo estado a transitar en el diagrama de transicion de estado

        if state.label == "Closed":
            if SYN_FLAG in flags:
                state = agent.types.SynSent()

        elif state.label == "Listen":
            if SYN_FLAG in flags:
                state = agent.types.SynSent()

        elif state.label == "SynReceived":
            if FIN_FLAG in flags:
                state = agent.types.FinWait1()

        elif state.label == "SynSent":
            if time == 0:
                state = agent.types.Closed()

        elif state.label == "Established":
            if FIN_FLAG in flags:
                state = agent.types.FinWait1()

        elif state.label == "FinWait1":
            pass

        elif state.label == "FinWait2":
            pass

        elif state.label == "TimeWait":
            if time == 0:
                state = agent.types.Closed()

        elif state.label == "CloseWait":
            if FIN_FLAG in flags:
                state = agent.types.LastAck()

        elif state.label == "Closing":
            pass

        elif state.label == "LastAck":
            pass

    else:
        # Que pasa si my_address no es ninguno de los dos hosts de la conexion?
        pass
    # Actualiza time
    time += 1
    # Retorna el mensaje enviado + el nuevo estado
    return agent.types.Action(sent_message=message, new_state=state)

agent.run(host)
