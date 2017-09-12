#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <netinet/in.h>

#include "node.h"
#include "EtherFrame.h"

#define IP_CODE 0x0800  
#define ETH_CODE 1      
#define ARP_CODE 0x0806 
#define ARPOP_REQUEST   1
#define ARPOP_REPLY     2

const MACAddress BROADCAST_ADDR = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};

struct ethernet_frame{
public:
    MACAddress addr_dest;           // ethernet address of destination 6 bytes
    MACAddress addr_origin;         // ethernet address of sender 6 bytes
    uint16_t type_protocol;         // protocol type 2 bytes
    char payload[IP_PAYLOAD_SIZE];  // buffer with 1500 bytes
}__attribute__((__packed__));


struct arp_packet{
public:
    uint16_t hrd;       // hardware address space
    uint16_t pro;       // protocol address space
    uint8_t hln;        // hardware length
    uint8_t pln;        // protocol length
    uint16_t op;        // opcode (request or reply)
    MACAddress sha;     // sender hardware address
    IPAddress spa;      // sender protocol address
    MACAddress tha;     // target hardware address
    IPAddress tpa;      // target protocol address
}__attribute__((__packed__));


int Node::ip_index(IPAddress ip){
    int i = 0;

    for(i = 0; i < arp_table.count_register; i++){
        if(memcmp(ip, arp_table.ip_array[i], sizeof(IPAddress)) == 0){
            return i;
        }
    }
    return -1;
}

void Node::add_arp_table(IPAddress new_ip, MACAddress new_mac){

    if(arp_table.count_register == 255){
        printf("tabla llena\n");
    }else{
        memcpy(arp_table.ip_array[arp_table.count_register], new_ip, sizeof(IPAddress));
        memcpy(arp_table.mac_array[arp_table.count_register], new_mac, sizeof(MACAddress));
        arp_table.count_register = arp_table.count_register + 1;
    }
}

/*
 * Implementar!
 * Intentar enviar `data` al `ip` especificado.
 * `data` es un buffer con IP_PAYLOAD_SIZE bytes.
 * Si la dirección MAC de ese IP es desconocida, debería enviarse un pedido ARP.
 * Devuelve 0 en caso de éxito y distinto de 0 si es necesario reintentar luego
 * (porque se está bucando la dirección MAC usando ARP)
 */

int Node::send_to_ip(IPAddress ip, void *data){

    struct ethernet_frame eth_frame;

    int i = ip_index(ip);

    if(i >= 0){
        /*armamos paquete IP*/
        get_my_mac_address(eth_frame.addr_origin);
        memcpy(eth_frame.addr_dest, arp_table.mac_array[i], sizeof(MACAddress));
        eth_frame.type_protocol = htons(IP_CODE);
        memcpy(eth_frame.payload, data, IP_PAYLOAD_SIZE);
        send_ethernet_packet(&eth_frame);
        return 0;
    } else{
        /*armamos marco ethernet para paquete ARP*/
        struct arp_packet packet;

        get_my_mac_address(eth_frame.addr_origin);
        memcpy(eth_frame.addr_dest, BROADCAST_ADDR, sizeof(MACAddress));
        eth_frame.type_protocol = htons(ARP_CODE);

        /*armamos paquete ARP*/
        packet.hrd = htons(ETH_CODE);
        packet.pro = htons(IP_CODE);
        packet.hln = (uint8_t) sizeof(MACAddress);
        packet.pln = (uint8_t) sizeof(IPAddress);
        packet.op = htons(ARPOP_REQUEST);
        get_my_mac_address(packet.sha);
        get_my_ip_address(packet.spa);
        memcpy(packet.tha, BROADCAST_ADDR, sizeof(MACAddress));
        memcpy(packet.tpa, ip, sizeof(IPAddress));
        memcpy(eth_frame.payload, &packet, IP_PAYLOAD_SIZE);
        send_ethernet_packet(&eth_frame);
        return 1;
    }
}

    /*
 * Implementar!
 * Manejar el recibo de un paquete.
 * Si es un paquete ARP: procesarlo.
 * Si es un paquete con datos: pasarlo a la capa de red con receive_ip_packet.
 * `packet` es un buffer de ETHERFRAME_SIZE bytes.
    Un paquete Ethernet tiene:
     - 6 bytes MAC destino
     - 6 bytes MAC origen
     - 2 bytes tipo
     - 46-1500 bytes de payload (en esta aplicación siempre son 1500)
    Tamaño total máximo: 1514 bytes
 */
void Node::receive_ethernet_packet(void *packet) {

    struct ethernet_frame *frame = (struct ethernet_frame*) packet;
    MACAddress my_mac;
    get_my_mac_address(my_mac);


    /*verificamos si el paquete es de tipo IP*/
    if(ntohs(frame->type_protocol) == IP_CODE){
        /*verifico si las dos direcciones mac son iguales para
        enviar el paquete a la capa de red*/
        if(memcmp(my_mac, frame->addr_dest, sizeof(MACAddress)) == 0){
            receive_ip_packet(frame->payload);
        }   
    /*verificamos si el paquete es ARP*/
    }else if(ntohs(frame->type_protocol) == ARP_CODE){

        struct arp_packet *pack = (struct arp_packet*) (frame->payload);
        /*verificamos campos del paquete ARP recibido*/
        if(ntohs(pack->hrd) == ETH_CODE && ntohs(pack->pro) == IP_CODE){
            bool merge_flag = false;
            int index = ip_index(pack->spa);

            if(index >= 0){
                /*actualizamos la mac del host con el ip recibido*/
                memcpy(arp_table.mac_array[index], pack->sha, sizeof(MACAddress));
                merge_flag = true;
            }
            IPAddress my_ip;
            get_my_ip_address(my_ip);
            /*verifico si el paquete llega a la direccion ip donde se queria enviar
            para agregar tanto la direccion mac y la direccion ip a la tabla*/
            if(memcmp(pack->tpa, my_ip, sizeof(IPAddress)) == 0){
                if(!merge_flag){
                    add_arp_table(pack->spa, pack->sha);
                }
            }
            /*verifico si el paquete arp recibido es de solicitud de direccion mac*/
            if(ntohs(pack->op) == ARPOP_REQUEST){
                /*creo estructuras para armar nuevo paquete a enviar*/
                    struct ethernet_frame frame;
                    struct arp_packet arp_p;

                /*creo el marco ethernet del paquete*/
                    get_my_mac_address(frame.addr_origin);
                    memcpy(frame.addr_dest, pack->sha, sizeof(MACAddress));
                    frame.type_protocol = htons(ARP_CODE);

                /*creo el nuevo paquete arp de respuesta y swapeo los campos de direcciones
                mac e ip del receptor con emisor*/
                    memcpy(arp_p.tpa, pack->spa, sizeof(IPAddress));
                    memcpy(arp_p.tha, pack->sha, sizeof(MACAddress));
                    get_my_mac_address(arp_p.sha);
                    get_my_ip_address(arp_p.spa);
                    arp_p.hrd = htons(ETH_CODE);
                    arp_p.pro = htons(IP_CODE);
                    arp_p.hln = (uint8_t) sizeof(MACAddress);
                    arp_p.pln = (uint8_t) sizeof(IPAddress);
                    arp_p.op = htons(ARPOP_REPLY);

                    /*encapsulo el paquete arp en payload*/
                    memcpy(frame.payload, &arp_p, IP_PAYLOAD_SIZE);
                    /*envio el marco ethernet*/
                    send_ethernet_packet(&frame);
            }
        }
    }
}

/*
 * Constructor de la clase. Poner inicialización aquí.
 */
Node::Node()
{
    arp_table.count_register = 0;//inicializo la cantidad de direcciones en la tabla
    timer = NULL;
    for (unsigned int i = 0; i != AMOUNT_OF_CLIENTS; ++i) {
        seen[i] = 0;
    }
}