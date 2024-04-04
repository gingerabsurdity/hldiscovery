import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event

# import togml
from TInvRecogniser import TInvRecogniser
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from datetime import datetime
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.inductive import algorithm as heuristic_miner
import pm4py.objects.petri_net.exporter as pn_exporter
import os
import numpy as np
from pm4py.objects.petri_net.utils.incidence_matrix import IncidenceMatrix
from pm4py.objects.petri_net.importer import importer as petri_importer
import sympy

import os

# arr2 = arr[:3]

path = "BPI Challenge 2017.xes"
# path = "BPIC15_1f.xes"
file_path = os.path.join(os.path.join(os.path.dirname(__file__), "TKDE_Benchmark"), path)
log = pm4py.read.read_xes(file_path)

process_tree = heuristic_miner.apply(log)
net, initial_marking, final_marking = pm4py.convert_to_petri_net(process_tree)

# net, initial_marking, final_marking = inductive_miner.apply(log)

# net_file_name = 'final_net_BPIC17_ind.pnml'
# net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
# pn_exporter.exporter.apply(net, initial_marking, net_path_out)

# togml.generate_gml(net)

replayed_traces = token_replay.apply(log, net, initial_marking, final_marking)
# replayed_traces = token_replay.apply(final_detailed_log, detailed_net, initial_marking, final_marking)
# replayed_traces = token_replay.apply(initial_log, detailed_net, initial_marking, final_marking)
print(str(replayed_traces))

net_file_name = 'final_net_BPIC17_ind.pnml'
net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
pn_exporter.exporter.apply(net, initial_marking, net_path_out)
