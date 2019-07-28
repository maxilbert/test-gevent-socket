from node import Node
from random import Random


def test():
    N = 4
    host = "localhost"
    port_base = int(Random().random() * 40000 + 10000)
    addresses = [(host, port_base + i) for i in range(N)]

    nodes = [Node(port=each[1], nodes_list=addresses) for each in addresses]

    for node in nodes:
        node.start()

    for node in nodes:
        node.connect_nodes()

    for j in range(100):
        msg = ("msg %d" % j)
        nodes[j % 4].broadcast(msg)
    print("all messages sent")


if __name__ == "__main__":
    test()
