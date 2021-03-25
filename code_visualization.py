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
             print("1. Adding %s to %s" %(i,key))
             if isinstance(node[key][i], Mapping):
                 for e in node[key][i]:
                     G.add_edge(i,e)
                     print("2. Adding %s to %s" %(e,i))
                     if isinstance(node[key][i][e], Mapping):
                         for f in node[key][i][e]:
                             G.add_edge(e,f)
                             print("3. Adding %s to %s" %(f,e))
                             if isinstance(node[key][i][e][f], Mapping):
                                for a in node[key][i][e][f]:
                                   G.add_edge(f,a)
                                   print("4. Adding %s to %s" %(a,f))
                                   if isinstance(node[key][i][e][f][a], Mapping):
                                       for b in node[key][i][e][f][a]:
                                           G.add_edge(a,b)
                                           print("5. Adding %s to %s" %(b,a))
                                           if isinstance(node[key][i][e][f][a][b], Mapping):
                                               for c in node[key][i][e][f][a][b]:
                                                   G.add_edge(b,c)
                                                   print("6. Adding %s to %s" %(c,b))
                                                   if isinstance(node[key][i][e][f][a][b][c], Mapping):
                                                       for d in node[key][i][e][f][a][b][c]:
                                                           G.add_edge(c, d)
                                                           print("7a. Adding %s to %s" %(d,c))
                                                           G.add_edge(d, node[key][i][e][f][a][b][c][d])
                                                           print("7. Adding %s to %s" %(node[key][i][e][f][a][b][c][d],d))
                                                   else:
                                                       G.add_edge(c, node[key][i][e][f][a][b][c])
                                                       print("8. Adding %s to %s" %(node[key][i][e][f][a][b][c],c))
                                           else:
                                               G.add_edge(a, node[key][i][e][f][a][b])
                                               print("9. Adding %s to %s" %(node[key][i][e][f][a][b],a))
                                   elif isinstance(node[key][i][e][f][a], list):
                                       for b in node[key][i][e][f][a]:
                                           if isinstance(b, list):
                                               for c in b:
                                                   G.add_edge(a,c)
                                                   print("10. Adding %s to %s" %(c,a))
                                           else:
                                               G.add_edge(a,b)
                                               print("11. Adding %s to %s" %(b,a))
                                   else:
                                       G.add_edge(a,node[key][i][e][f][a])
                                       print("12. Adding %s to %s" %(node[key][i][e][f][a],a))
                             else:
                                 G.add_edge(f,node[key][i][e][f])
                                 print("13. Adding %s to %s" %(node[key][i][e][f],f))
                     elif isinstance(node[key][i][e], list):
                         for f in node[key][i][e]:
                             if isinstance(f, list):
                                 for g in f:
                                     G.add_edge(e,g)
                                     print("14. Adding %s to %s" %(g,e))
                             else:
                                 G.add_edge(e,f)
                                 print("15. Adding %s to %s" %(f,e))
                     else:
                         if e!="long_description":
                            G.add_edge(e,node[key][i][e])
                            print("16. Adding %s to %s" %(node[key][i][e],e))
             else:
                 G.add_edge(i,node[key][i][:10])
                 print("17. Adding %s to %s" %(node[key][i],i))

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
        elif node == "file" or node in js["file"].keys():
             color_map.append('lavender')
             node_size.append(100)
        elif node == "dependencies" or node in js["dependencies"].keys():
             color_map.append('orange')
             node_size.append(100)
        elif node == "classes" or node in js["classes"].keys():
             color_map.append('yellowgreen')
             node_size.append(100)
        elif node == "functions" or node in js["functions"].keys():
             color_map.append('turquoise')
             node_size.append(100)
        elif node == "controlflow":
             color_map.append('lightcoral')
             node_size.append(100)
        elif node == "doc":
            color_map.append('orchid')
            node_size.append(100)
        elif node == "args":
            color_map.append('whitesmoke')
            node_size.append(100)
        elif node == "returns":
            color_map.append('whitesmoke')
            node_size.append(100)
        elif node == "min_max_lineno":
            color_map.append('khaki')
            node_size.append(100)
        elif node == "min_lineno":
            color_map.append('khaki')
            node_size.append(100)
        elif node == "max_lineno":
            color_map.append('khaki')
            node_size.append(100)
        elif node == "extension":
            color_map.append('bisque')
            node_size.append(100)
        elif node == "fileNameBase":
            color_map.append('bisque')
            node_size.append(100)
        elif node == "path":
            color_map.append('bisque')
            node_size.append(100)
        elif node == "cfg":
            color_map.append('lightcoral')
            node_size.append(100)
        elif node == "png":
            color_map.append('lightcoral')
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
            color_map.append('silver')
            node_size.append(100)
    
    plt.figure(figsize=(20,10))
    #comment this line if you want to have the name of the nodes
    nx.draw(G,with_labels=True, node_color=color_map)
    #comment this line if you do not want to have the name of the nodes 
    #nx.draw(G,with_labels=False, node_color=color_map)
    plt.savefig("visual_code.png")
    
