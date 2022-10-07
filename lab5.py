"""
Networks and Network Security
Lab 5 - Distributed Sensor Network
NAME(s): Daan van den Hoek, Lara Topalovic-Henn
STUDENT ID(s): 14030527, 13824570
GROUP NAME: Lab4 sux

DESCRIPTION:

"""
import sys
import struct
import socket
import math
from random import randint, gauss
import sensor
from tkinter import TclError
from threading import Thread
from gui import MainWindow


# Get random position in NxN grid.
def random_position(n):
    x = randint(0, n)
    y = randint(0, n)
    return (x, y)

# hier ergens pythagoras doen
# Misschien math.hypot()
def pythagoras(x, y) :
    return math.sqrt(x ** 2 + y ** 2)


class SensorClient(Thread):
    def __init__(self, mcast_addr, sensor_pos, sensor_strength, sensor_value,
                 grid_size, ping_period, window):
        """
        mcast_addr: udp multicast (ip, port) tuple.
        sensor_pos: (x,y) sensor position tuple.
        sensor_strength: initial strength of the sensor ping (radius).
        sensor_value: initial temperature measurement of the sensor.
        grid_size: length of the  of the grid (which is always square).
        ping_period: time in seconds between multicast pings.

        Additional parameters to this method should always have a default
        value!
        """
        super().__init__()

        # Save any parameters which should be accessible later:
        # TODO It's probably a good idea to either save the parameters
        # to this method here, or create a seperate class to hold them.


        # sensor strength is the radius!!
        self.window = window
        self.strength = sensor_strength

        # Listen for this socket becoming readable in your select call
        # to allow the main thread to wake the client from being blocked on
        # select. You should ignore the data being written to it.
        self.wake_socket = self.window.wake_thread

        # Create the multicast listener socket.
        self.mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                   socket.IPPROTO_UDP)
        # Sets the socket address as reusable so you can run multiple instances
        # of the program on the same machine at the same time.
        self.mcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Subscribe the socket to multicast messages from the given address.
        mreq = struct.pack('4sl', socket.inet_aton(mcast_addr[0]),
                        socket.INADDR_ANY)
        self.mcast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        if sys.platform == 'win32':  # windows special case
            mcast.bind(('localhost', mcast_addr[1]))
        else:  # should work for everything else
            self.mcast.bind(mcast_addr)

        # Create the peer-to-peer socket.
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                            socket.IPPROTO_UDP)
        # Set the socket multicast TTL so it can send multicast messages.
        self.peer.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        # Bind the socket to a random port.
        if sys.platform == 'win32':  # windows special case
            peer.bind(('localhost', socket.INADDR_ANY))
        else:  # should work for everything else
            self.peer.bind(('', socket.INADDR_ANY))

        self.window.writeln('my address is %s:%s' % self.peer.getsockname())
        self.window.writeln(f'my position is (%s, %s)' % sensor_pos)

        self.sensor = sensor.Sensor(mcast_addr, sensor_pos, sensor_strength, sensor_value,
                 grid_size, ping_period, self.peer, self.mcast, window)

        # TODO Implement additional code that should be run only once when starting
        # the client here:

    def run(self):
        """
        Implement the auto ping and listening for incoming messages here.
        """
        try:
            while not self.window.quit_event.is_set():
                # Implement code that should run continuously here:

                # clear list of neighbors

                # check multicast ping message
                pass
        except TclError:
            pass

    def text_entered(self, line):
        """
        Handle new input line here.
        Do not change the name of this method!
        This method is called each time a command is entered in
        the GUI.
        """
        # Implement code that should be run when a line is entered here:
        pass

# Program entry point.
# You may add additional commandline arguments, but your program
# should be able to run without specifying them
if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--group', help='multicast group', default='224.1.1.1',
                   type=str)
    p.add_argument('--port', help='multicast port', default=50000, type=int)
    p.add_argument('--pos', help='x,y sensor position', type=str)
    p.add_argument('--strength', help='sensor strength', default=50,
                   type=int)
    p.add_argument('--value', help='sensor measurement value (unused this year)', type=float)
    p.add_argument('--grid', help='size of grid', default=100, type=int)
    p.add_argument('--period', help='period between autopings (0=off)',
                   default=10, type=int)
    args = p.parse_args(sys.argv[1:])
    if args.pos:
        pos = tuple(int(n) for n in args.pos.split(',')[:2])
    else:
        pos = random_position(args.grid)
    value = args.value if args.value is not None else gauss(20, 2)
    mcast_addr = (args.group, args.port)

    w = MainWindow()
    sensor_client = SensorClient(mcast_addr, pos, args.strength, value, args.grid, args.period, w)
    w.set_client(sensor_client)
    sensor_client.start()
    w.start()