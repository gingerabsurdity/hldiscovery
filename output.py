from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.visualization.petri_net import visualizer as pn_visualizer

# Import the Petri net from PNML
net, initial_marking, final_marking = pnml_importer.apply("output.pnml")

# Visualize and save as image
gviz = pn_visualizer.apply(net, initial_marking, final_marking)
pn_visualizer.save(gviz, "petri_net_visualization.png")
print("Petri net visualization saved as petri_net_visualization.png")
