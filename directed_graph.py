# -*- coding:utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import random

# Crea grafica
G = nx.DiGraph()

# Vertices
G.add_nodes_from(range(1,7))

# Aristas
aristas = [(1,5), (2,1), (2,3), (2,5),
           (3,4), (4,5), (6,4)]
G.add_edges_from(aristas)

pos=nx.spring_layout(G)
nx.draw_networkx_labels(G, pos, 
                        labels=dict([(i,i) for i in range(1,7)]))

# Dibuja la gráfica
nx.draw(G,pos)

# Muestra en pantalla lo dibujado
plt.show()
