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


def replace(trace, cyc, cyc_without_A_elements):
    indexes = []
    for i in range(len(trace)):  # ищем цикл в трассе
        if trace[i:i + len(cyc)] == cyc:
            indexes.extend([i, i + len(cyc)])
    trace_after_replace = trace
    if len(indexes) > 1:
        del trace_after_replace[indexes[0]:indexes[1]]  # удаляем сус из трассы
        trace_after_replace[indexes[0]:indexes[0]] = list(cyc_without_A_elements)
    return trace_after_replace


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
        dfg = dfg_discovery.apply(self.log)  # строим Directly follows graph для всего лога, чтобы найти отношения

        self.causal_relations = {k: v for k, v in
                                 causal_algorithm.apply(dfg, variant=CAUSAL_HEURISTIC).items() if
                                 v > 0}.keys()
        self.parallel_relations = {(f, t) for (f, t) in dfg if (t, f) in dfg}

        for trace in self.log:  # в оригинале был прогресс от лога отдельной переменной, а лог глобальной, в процедуре
            # запускалось от текущего прогресса и он инкрементился, то есть переходил к следующей трассе
            trace_to_events_names_list = [event['concept:name'] for event in trace]
            if trace:
                if tuple(
                        trace_to_events_names_list) not in self.visited_traces:  # класть в посещенные трассы только массив и сравнивать только его, не всю трассу с именем
                    self.visited_traces.add(
                        tuple(trace_to_events_names_list))  # чтобы не обрабатывать одинаковые трассы
                    flag = True
                    while flag:
                        # Find the elementary cycle in trace if there are some
                        ecyc = self.e_cyc(trace_to_events_names_list)
                        if ecyc is not None:
                            if self.no_nested_cyc:
                                ecyc = sorted(ecyc)
                                self.t_invariants.add(ecyc)
                                flag = False
                            else:
                                if tuple(ecyc) not in self.visited_cycs:
                                    causality_graph = self.build_causality_graph(ecyc)
                                    strongly_connected_components_of_eCyc = nx.strongly_connected_components(
                                        causality_graph)  # page 4 of tapia thesis, line 80 in prom TinvOperations
                                    for nodes_of_component in strongly_connected_components_of_eCyc:  # line 85
                                        if len(nodes_of_component) > 1:  # 87 |V_i|>1
                                            if tuple(nodes_of_component) not in self.t_invariants:
                                                self.t_invariants.add(tuple(nodes_of_component))
                                            A.update(nodes_of_component)
                                    ecyc_without_t_inv_nodes = clear(set(ecyc), A)
                                    trace_to_events_names_list = replace(trace_to_events_names_list, ecyc,
                                                                         ecyc_without_t_inv_nodes)
                                    self.visited_cycs[tuple(
                                        ecyc)] = nodes_of_component  # мб только если в компоненте больше 1 элемента
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
                    while x < len(analyzed_events):
                        ecyc.append(analyzed_events[x])
                        x += 1
                    self.no_nested_cyc = False
                    return ecyc
            analyzed_events.append((event))
        return None

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
