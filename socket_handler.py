#!/usr/bin/env python

import struct
from socket import *
from structures import *
import threading

class SocketThread(threading.Thread):
    def __init__(self, session):
        threading.Thread.__init__(self)
        self.session = session
        self.running = True

        #open socket
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind(('', 20777))

        self.start()

    def close(self):
        self.running = False

    def run(self):
        while self.running:
            #populate a packet object
            packet = Packet()
            #todo, remove calcsize from here and do it in the pkt object
            raw_packet = self.socket.recv(struct.calcsize(packet.format))
            packet.decode_raw_packet(raw_packet)

            #add this packet object to the current session
            lap_finished = not self.session.current_lap.add_packet(packet)
            if lap_finished:
                pass

        #we've signalled for the recv thread to stop, so do cleanup
        self.socket.close()

if __name__ == '__main__':
    s = Session()
    thread = SocketThread(s);
    while True:
        pass #todo print out some stuff
