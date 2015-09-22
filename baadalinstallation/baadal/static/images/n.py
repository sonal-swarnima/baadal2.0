import pydot 
 

graph = pydot.Dot(graph_type='graph',rankdir='LR',label="HOST NETWORKING GRAPH")
labels=[[1,2,3,4],
	[1,2,4,5],
        [1,2,3,4],
	[1,2,4,5]]
host_name=["host1","host2","host3","host4"]
total_host=len(host_name)
for i in xrange(total_host):
    for j in xrange(i+1,total_host):
        if i!=j:
             graph.add_edge(pydot.Edge(host_name[i],host_name[j] ,label=labels[i][j]))
graph.write_png('/home/www-data/web2py/applications/baadal/static/images/network_graph.png') 
