import os
import numpy as np
import pm4py.algo.analysis.woflan.graphs.utility as wolflan
from pm4py.objects.petri_net.importer import importer as petri_importer
import sympy
from pm4py.objects.petri_net.utils.incidence_matrix import IncidenceMatrix

net, i_m, f_m = petri_importer.apply(os.path.join(os.path.join(os.path.dirname(__file__), "highlevelnet.pnml")))
matrix = wolflan.compute_incidence_matrix(net)
print(matrix)
b = np.zeros(len(matrix))
print(b)

incidence_matrix = IncidenceMatrix(net)

# exp from book https://www7.in.tum.de/~esparza/fcbook-middle.pdf
t_inv = sympy.Matrix(incidence_matrix.a_matrix).nullspace()
t_inv = np.array(t_inv).astype(np.float64)
invariants_names = []
for inv in t_inv:
    if(np.all(inv >= 0)):
        invariant_names = []
        t_index = 0
        for t in inv:
            if(t == 1):
                invariant_names.append(list(incidence_matrix.transitions.keys())[list(incidence_matrix.transitions.values()).index(t_index)].label)
            t_index += 1
        invariants_names.append(invariant_names)


print(t_inv)
print(invariants_names)