import networkx as nx
import json
import os
import matplotlib.pyplot as plt
from collections.abc import Mapping
import sys

def walk(node):
    for key, item in node.items():
        for i in item:
             G.add_edge(key,i)
             if isinstance(node[key][i], Mapping):
                 for e in node[key][i]:
                     G.add_edge(i,e)
                     if isinstance(node[key][i][e], Mapping):
                         for f in node[key][i][e]:
                             G.add_edge(e,f)
                             if isinstance(node[key][i][e][f], Mapping):
                                for a in node[key][i][e][f]:
                                   G.add_edge(f,a)
                                   if isinstance(node[key][i][e][f][a], Mapping):
                                       for b in node[key][i][e][f][a]:
                                           G.add_edge(a,b)
                                           if isinstance(node[key][i][e][f][a][b], Mapping):
                                               for c in node[key][i][e][f][a][b]:
                                                   G.add_edge(b,c)
                                                   if isinstance(node[key][i][e][f][a][b][c], Mapping):
                                                       for d in node[key][i][e][f][a][b][c]:
                                                           G.add_edge(d, node[key][i][e][f][a][b][c][d]) 
                                                   else:
                                                       G.add_edge(c, node[key][i][e][f][a][b][c]) 
                                           else:
                                               G.add_edge(a, node[key][i][e][f][a][b])
           
                                   elif isinstance(node[key][i][e][f][a], list):
                                       for b in node[key][i][e][f][a]:
                                           if isinstance(b, list):
                                               for c in b:
                                                   G.add_edge(a,c)
                                           else:
                                               G.add_edge(a,b)
                                   else:
                                       G.add_edge(a,node[key][i][e][f][a])
                             else:
                                G.add_edge(f,node[key][i][e][f])
                     elif isinstance(node[key][i][e], list):
                         for f in node[key][i][e]:
                             if isinstance(f, list):
                                 for g in f:
                                     G.add_edge(e,g)
                             else:
                                 G.add_edge(e,f)
                     else:
                         G.add_edge(e,node[key][i][e])
             else:
                 G.add_edge(i,node[key][i])

if __name__ == "__main__":
    input_path = sys.argv[1]
    my_path = os.path.dirname(__file__)
    with open(os.path.join(my_path, input_path)) as f:
        js = json.load(f)
    G=nx.Graph()
    for key in js.keys():
        G.add_edge('ROOT',key, color='r',weight=2)
    walk(js)
    color_map = []
    node_size = []
    for node in G:
        if node == "ROOT": 
             color_map.append('red')
             node_size.append(100)
        elif node in js.keys():
             if node == "file":
                 color_map.append('lavender')
                 node_size.append(100)
             elif node == "dependencies":
                 color_map.append('orange')
                 node_size.append(100)
             elif node == "classes":
                 color_map.append('lightgreen')
                 node_size.append(100)
             elif node == "functions":
                 color_map.append('yellow')
                 node_size.append(100)
             elif node == "controlflow":
                 color_map.append('gold')
                 node_size.append(100)
        elif node == "doc":
            color_map.append('pink')
            node_size.append(100)
        elif node == "args":
            color_map.append('whitesmoke')
            node_size.append(100)
        elif node == "returns":
            color_map.append('whitesmoke')
            node_size.append(100)
        elif node == "min_max_lineno":
            color_map.append('tan')
            node_size.append(100)
        elif node == "min_lineno":
            color_map.append('khaki')
            node_size.append(100)
        elif node == "max_lineno":
            color_map.append('khaki')
            node_size.append(100)
        elif node == "extension":
            color_map.append('magenta')
            node_size.append(100)
        elif node == "fileNameBase":
            color_map.append('bisque')
            node_size.append(100)
        elif node == "path":
            color_map.append('beige')
            node_size.append(100)
        elif node == "cfg":
            color_map.append('navajowhite')
            node_size.append(100)
        elif node == "png":
            color_map.append('navajowhite')
            node_size.append(100)
        elif node == "full":
            color_map.append('orchid')
            node_size.append(100)
        elif node == "short_description":
            color_map.append('orchid')
            node_size.append(100)
        elif node == "long_description":
            color_map.append('orchid')
            node_size.append(100)
        elif node == "raises":
            color_map.append('orchid')
            node_size.append(100)
        elif node == "from_module":
            color_map.append('orange')
            node_size.append(100)
        elif node == "import":
            color_map.append('orange')
            node_size.append(100)
        elif node == "alias":
            color_map.append('orange')
            node_size.append(100)
       
 
        else:
            color_map.append('skyblue')
            node_size.append(100)
    
    plt.figure(figsize=(20,10))
    #comment this line if you want to have the name of the nodes
    nx.draw(G,with_labels=True, node_color=color_map)
    #comment this line if you do not want to have the name of the nodes 
    #nx.draw(G,with_labels=False, node_color=color_map)
    plt.savefig("visual_code.png")
    
