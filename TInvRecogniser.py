import os
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pandas
import pm4py
import datetime as dt
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.algo.discovery.causal import variants
import networkx as nx
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.causal import algorithm as causal_algorithm
from pm4py.algo.discovery.causal.algorithm import CAUSAL_ALPHA
from pm4py.algo.discovery.causal.algorithm import CAUSAL_HEURISTIC

# simplifies the trace by removing detected cycles for further analysis
def replace(trace, cyc, cyc_without_A_elements):
    indexes = []
    for i in range(len(trace)):  # looking for a cycle in the trace
        if trace[i:i + len(cyc)] == cyc:
            indexes.extend([i, i + len(cyc)])
    trace_after_replace = trace
    if len(indexes) > 1:
        del trace_after_replace[indexes[0]:indexes[1]]  # remove the cycle from the trace

        trace_after_replace[indexes[0]:indexes[0]] = list(cyc_without_A_elements)
    return trace_after_replace

# identifies parts of a cycle that aren't already covered by known invariants
def clear(cyc, A) -> list:
    if len(cyc.difference(A)) > 0:
        return cyc.difference(A)
    else:
        return []


class TInvRecogniser(object):
    def __init__(self, log):
        self.log = log
        self.visited_traces = set()
        self.no_nested_cyc = True
        self.t_invariants = set()
        self.visited_cycs = {}
        self.causal_relations = {}
        self.parallel_relations = {}

    def fill_t_inv(self):
        """
            Computes t invariants of a given log.

            Returns
            -----------
            set of t-invariants (tuples)
                {()}
            """
        A = set()
        dfg = dfg_discovery.apply(self.log) # build Directly follows graph for the entire log to find relationships
        self.causal_relations = set({k: v for k, v in
                                 causal_algorithm.apply(dfg, variant=CAUSAL_ALPHA).items() if
                                 v > 0}.keys())
        self.parallel_relations = {(f, t) for (f, t) in dfg if (t, f) in dfg}

        for trace in self.log: # in the original there was progress from the log of a separate variable, and the log was global, in the procedure
            # started from the current progress and it incremented, that is, it moved to the next track
            trace_to_events_names_list = [event['concept:name'] for event in trace]
            if trace:
                if tuple(
                        trace_to_events_names_list) not in self.visited_traces:  # put only an array into the visited traces and compare only it, not the entire trace with the name
                    self.visited_traces.add(
                        tuple(trace_to_events_names_list)) # to avoid processing identical traces
                    flag = True
                    while flag:
                        # Find the elementary cycle in trace if there are some
                        ecyc = self.e_cyc(trace_to_events_names_list)
                        if ecyc is not None:
                            if self.no_nested_cyc:
                                ecyc.sort() #TODO: check if this is really sorted here and if so, then add sorted in other places too
                                self.t_invariants.add(ecyc)
                                flag = False
                            else:
                                if tuple(ecyc) not in self.visited_cycs:
                                    causality_graph = self.build_causality_graph(ecyc)
                                    strongly_connected_components_of_eCyc = nx.strongly_connected_components(
                                        causality_graph)  # page 4 of tapia thesis, line 80 in prom TinvOperations
                                    #nodes_of_component: list
                                    for nodes_of_component in strongly_connected_components_of_eCyc:  # line 85
                                        if len(nodes_of_component) > 1:  # 87 |V_i|>1
                                            sorted_nodes_of_comp = sorted(nodes_of_component)
                                            if tuple(nodes_of_component) not in self.t_invariants: #TODO: add a check that one is not included in the other and, if it is, then add only the set that is greater
                                                result = False
                                                inv_to_remove = []
                                                for inv in self.t_invariants:
                                                    #result = all(elem in inv for elem in nodes_of_component) or all(elem in nodes_of_component for elem in inv)
                                                    if (set(nodes_of_component).issubset(set(inv))):
                                                        result = True
                                                        break
                                                    if (set(inv).issubset(set(nodes_of_component))):
                                                        inv_to_remove = inv
                                                        break

                                                if len(inv_to_remove)>0:
                                                    self.t_invariants.remove(inv_to_remove)
                                                if not result:
                                                    self.t_invariants.add(tuple(sorted_nodes_of_comp))
                                            A.update(nodes_of_component)
                                    ecyc_without_t_inv_nodes = clear(set(ecyc), A)
                                    trace_to_events_names_list = replace(trace_to_events_names_list, ecyc,
                                                                         ecyc_without_t_inv_nodes)
                                    self.visited_cycs[tuple(
                                        ecyc)] = nodes_of_component  # mb only if the component has more than 1 element
                                    ecyc = self.e_cyc(trace_to_events_names_list)
                                else:
                                    for aux in self.visited_cycs.get(tuple(ecyc)):
                                        A.add(aux)
                                        ecyc_without_t_inv_nodes = clear(set(ecyc), A)
                                        trace_to_events_names_list = replace(trace_to_events_names_list, ecyc,
                                                                             ecyc_without_t_inv_nodes)
                                    ecyc = self.e_cyc(trace_to_events_names_list)
                                    if ecyc is None or self.visited_cycs.get(tuple(ecyc)) is None:
                                        flag = False
                                        # line 114

                        flag = flag and (ecyc is not None) and (
                                    len(ecyc) > 0)  # until trace not empty and cyc_e != empty set

    # Find the first elementary cyc in the trace
    def e_cyc(self, trace):
        analyzed_events = list()
        ecyc = list()
        for i in range(len(trace)):
            event = trace[i]  # ['concept:name']
            if len(analyzed_events) > 0:
                if event in analyzed_events:
                    x = analyzed_events.index(event)
                    #ecyc_len = x + trace[x+1:len(trace)].index(event)
                    while x < len(analyzed_events):
                        ecyc.append(analyzed_events[x])
                        x += 1
                    self.no_nested_cyc = False
                    return ecyc
            analyzed_events.append((event))
        return None
    # adds new T-invariants to the set of discovered invariants
    def add_invariant(self, invariant_to_add):  # invariant_to_add should be sorted beforehand
        add = True
        t_inv_to_remove = list()
        if invariant_to_add not in self.t_invariants.values():
            for existing_invariant in self.t_invariants.keys():
                if len(self.t_invariants[existing_invariant]) > len(invariant_to_add):
                    existing_invariant_set = set(self.t_invariants[existing_invariant])
                    invariant_to_add_set = set(invariant_to_add)
                    if invariant_to_add_set in existing_invariant_set:
                        t_inv_to_remove.append(existing_invariant)
                    elif existing_invariant_set in invariant_to_add_set:
                        add = False
            for i in t_inv_to_remove:
                self.t_invariants.pop(i)
            if add:
                self.t_invariants[len(self.t_invariants)] = invariant_to_add

    def build_causality_graph(self, cyc):
        import networkx as nx
        graph = nx.DiGraph()
        for transition in cyc:
            graph.add_node(transition)
        for relation in self.causal_relations:
            if relation not in self.parallel_relations:
                if relation[0] in graph.nodes and relation[1] in graph.nodes:
                    graph.add_edge(relation[0], relation[1])
        return graph
