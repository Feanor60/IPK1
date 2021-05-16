#!/usr/bin/env python3

import getopt
import sys
import socket
import re


def check_args(nameserver_parsed, surl_parsed):
    socket.inet_aton(nameserver_parsed[0])

    if 0 <= int(nameserver_parsed[1]) <= 65535:
        pass
    else:
        print("Err invalid port number")
        sys.exit(2)

    if "fsp:" not in surl_parsed[0]:
        print("Err invalid protocol")
        sys.exit(2)

    if surl_parsed[1]:
        print("Err invalid url syntax")
        sys.exit(2)


def get_server_ip(nameserver_parsed, surl_parsed):
    UDP_IP = nameserver_parsed[0]
    UDP_PORT = int(nameserver_parsed[1])
    MESSAGE = "WHEREIS " + surl_parsed[2]
    buffer_size = 1024
    bytes_to_send = str.encode(MESSAGE)

    sock_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    sock_udp.settimeout(100)

    try:
        sock_udp.sendto(bytes_to_send, (UDP_IP, UDP_PORT))
        msg_from_server = sock_udp.recvfrom(buffer_size)
    except socket.error:
        print("Error while server ip address")
        sys.exit(2)

    return parse_NSP_respone(msg_from_server)


def parse_NSP_respone(msg_from_server):
    msg = format(msg_from_server[0])
    return_message = msg.split(" ")
    if(return_message[0]) == 'ERR':
        print(msg)
        sys.exit(2)

    return_message[1] = return_message[1][:-1]
    return return_message[1]


def get_file(surl_parsed, server_ip_port_parsed):
    TCP_IP = server_ip_port_parsed[0]
    if "No" in server_ip_port_parsed[0]:
        print("Err invalid fileserver name")
        sys.exit(2)

    TCP_PORT = int(server_ip_port_parsed[1])
    BUFFER_SIZE = 1024

    get_message = "GET " + surl_parsed[3] + " FSP/1.0\r\nHostname: " + surl_parsed[2] + "\r\nAgent: xbubel08\r\n\r\n"
    bytes_to_send = str.encode(get_message)

    try:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.connect((TCP_IP, TCP_PORT))
        sock_tcp.send(bytes_to_send)
    except socket.error:
        print("Err while connectiong to server")
        sys.exit(2)

    header = get_header(sock_tcp, BUFFER_SIZE)

    parse_header(header, sock_tcp, BUFFER_SIZE)

    f = open(surl_parsed[3], "x")
    f.close()

    f = open(surl_parsed[3], "wb")

    while True:
        data = sock_tcp.recv(BUFFER_SIZE)
        if not data:
            break

        f.write(data)

    f.close()


def get_header(sock_tcp, BUFFER_SIZE):
    data = sock_tcp.recv(BUFFER_SIZE)
    return data


def parse_header(header, sock_tcp, BUFFER_SIZE):
    header_decoded = header.decode("utf-8")
    if header_decoded.find('Not') > 0:
        header_parsed = header_decoded.split('\n')
        print(header_parsed[3])
        sys.exit(2)
    elif "Bad request" in header_decoded:
        header_parsed = header_decoded.split('\n')
        print(header_parsed[3])
        sys.exit(2)


def main():
    nameserver = None
    surl = None
    n_option = False
    f_option = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:f:")
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if o in ("-n"):
            n_option = True
            nameserver = a
        elif o in ("-f"):
            f_option = True
            surl = a
        else:
            print("Err: invalid option")
            sys.exit(2)

    if n_option is False:
        print("Err: nameserver option required")
        sys.exit(2)

    if f_option is False:
        print("Err: SURL option required")
        sys.exit(2)

    # print("nameserver is:" + nameserver + "\nSURL is:" + surl)

    nameserver_parsed = nameserver.split(":")
    surl_parsed = surl.split("/")
    check_args(nameserver_parsed, surl_parsed)

    server_ip_port = get_server_ip(nameserver_parsed, surl_parsed)

    server_ip_port_parsed = server_ip_port.split(":")

    get_file(surl_parsed, server_ip_port_parsed)


if __name__ == "__main__":
    main()
