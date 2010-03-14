"""A thorough test of polling REQ/REP sockets."""

import time
import zmq

addr = 'tcp://127.0.0.1:5555'
ctx = zmq.Context(1,1,zmq.POLL)
s1 = ctx.socket(zmq.REP)
s2 = ctx.socket(zmq.REQ)

s1.bind(addr)
s2.connect(addr)

# Sleep to allow sockets to connect.
time.sleep(1.0)

poller = zmq.Poller()
poller.register(s1, zmq.POLLIN|zmq.POLLOUT)
poller.register(s2, zmq.POLLIN|zmq.POLLOUT)

# Now make sure that both are send ready.
socks = dict(poller.poll())
assert socks[s1] == 0
assert socks[s2] == zmq.POLLOUT

# Make sure that s2 goes immediately into state 0 after send.
s2.send('msg1')
socks = dict(poller.poll())
assert socks[s2] == 0

# Make sure that s1 goes into POLLIN state after a time.sleep().
time.sleep(0.5)
socks = dict(poller.poll())
assert socks[s1] == zmq.POLLIN

# Make sure that s1 goes into POLLOUT after recv.
s1.recv()
socks = dict(poller.poll())
assert socks[s1] == zmq.POLLOUT

# Make sure s1 goes into state 0 after send.
s1.send('msg2')
socks = dict(poller.poll())
assert socks[s1] == 0

# Wait and then see that s2 is in POLLIN.
time.sleep(0.5)
socks = dict(poller.poll())
assert socks[s2] == zmq.POLLIN

# Make sure that s2 is in POLLOUT after recv.
s2.recv()
socks = dict(poller.poll())
assert socks[s2] == zmq.POLLOUT

# Wait for everything to finish.
time.sleep(1.0)
