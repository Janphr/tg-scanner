import networkx as nx
import pylab
import matplotlib.pyplot as plt

from matplotlib.pyplot import pause
from matplotlib import pyplot
pylab.ion()

import warnings
warnings.filterwarnings("ignore")

g = nx.Graph()

g = nx.MultiDiGraph()

g.add

g.add_nodes_from(range(1, 7))

pos = nx.circular_layout(g)

# def node():
#
#     for epoch in range(1,9):
#         print('------ iteration %d ---------' % epoch)
#         for nod1 in range(1,7):
#             g.add_node(nod1)
#             #for nod2 in range(1,7):   # this is how I originally create the graph
#                 #g.add_edge(nod1,nod2) # ''
#
#         if epoch > 1:
#             g.add_edge(1,2)
#             g.add_edge(2,3)
#             g.add_edge(5,4)
#             g.add_edge(4,6)
#             print(g.nodes())
#             print(g.edges())
#
#         if epoch > 5:
#             g.remove_node(5)
#             g.remove_edge(1,2)
#             g.remove_edge(4,6)
#
#         nx.draw(g, pos=nx.circular_layout(g), with_labels=True)
#         #pylab.draw()
#         pause(1)
#         pylab.show()
# #        plt.show()

def node():
    for epoch in range(1, 9):
        edges = []
        if 1 < epoch <= 5:
            edges = [(1, 2), (2, 3), (5, 4), (4, 6)]
        elif epoch > 5:
            if 5 in g.nodes:
                g.remove_node(5)
            edges = [(2, 3)]

        plt.clf()
        plt.title('Iteration {}'.format(epoch))
        nx.draw(g, pos=pos, edgelist=edges, with_labels=True)
        plt.pause(1)
        plt.show()

def main():

    print('--------- Simulation ---------')
    node()
    return 0

if __name__ == '__main__':
    main()