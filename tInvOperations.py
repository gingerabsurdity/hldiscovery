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


def replace(trace, cyc, cyc_without_A_elements):
    indexes = []
    for i in range(len(trace)):  # ищем цикл в трассе
        if trace[i:i + len(cyc)] == cyc:
            indexes.append((i, i + len(cyc)))
    trace_after_replace = trace
    del trace_after_replace[indexes[0]:indexes[1]]  # надеюсь тут не напутала с индексами, удаляем сус из трассы
    trace_after_replace.insert(indexes[0],
                               cyc_without_A_elements)  # вставляем на место cycа сус без элементов компоненты связности
    return trace_after_replace


def clear(cyc, A) -> list:
    return cyc.difference_update(A)


class ShorterStartTaskEndKeeper(object):
    def __init__(self, log):
        self.log = log
        self.visited_traces = set()
        self.no_nested_cyc = True
        # HashMap<Integer, Vector<String>> tinvariants = new HashMap< Integer, Vector<String>>();
        self.t_invariants = {} #dict[index_of_t_inv: [t_inv_elements]]
        self.visited_cycs = {}
        self.relations = {}

    def fill_t_inv(self):
        dfg = dfg_discovery.apply(self.log)  # строим Directly follows graph для всего лога, чтобы найти отношения

        self.relations = {k: v for k, v in
                            causal_algorithm.apply(dfg, variant=CAUSAL_ALPHA).items() if
                            v > 0}.keys()

        for trace in self.log:  # в оригинале был прогресс от лога отдельной переменной, а лог глобальной, в процедуре
            # запускалось от текущего прогресса и он инкрементился, то есть переходил к следующей трассе
            if trace:  # if (!trace.isEmpty()) {
                if trace not in self.visited_traces: #класть в посещенные трассы только массив и сравнивать только его, не всю трассу с именем
                    self.visited_traces.add(trace)  # чтобы не обрабатывать одинаковые трассы
                    # print("Trace number: " + trace.index)
                    flag = True
                    while flag:
                        # Find the elementary cycle in trace if there are some
                        ecyc = self.e_cyc(trace)
                        if self.no_nested_cyc:  # if(noNestedCyc){
                            ecyc = sorted(ecyc, key=lambda x: x['concept:name'])
                            self.add_invariant(ecyc)
                            flag = False  # вместо очистки трассы из лога 70 строка в джаве
                        else:
                            if tuple(ecyc) not in self.visited_cycs:  # if( !visitedeCycs.containsKey(ecyc) ){
                                dfg = dfg_discovery.apply(self.log)   #строим Directly follows graph для всего лога, чтобы найти отношения

                                causal_relations = {k: v for k, v in
                                                    causal_algorithm.apply(dfg, variant=CAUSAL_ALPHA).items() if
                                                    v > 0}.keys() #dfg -> causal relations (dict)
                                #dfg = dfg_discovery.apply(ecyc)

                                causality_graph = variants.alpha.apply(dfg)
                                strongly_connected_components_of_eCyc = nx.strongly_connected_components(
                                    causality_graph)  # page 4 of tapia thesis, line 80 in prom TinvOperations
                                # создаем клон ecyc (зочем?)
                                for nodes_of_component in strongly_connected_components_of_eCyc:  # line 85
                                    if len(nodes_of_component) > 1:  # 87 |V_i|>1
                                        self.t_invariants.add(tuple(i) for i in
                                                              nodes_of_component)  # line 99 Y(lambda)<-Y(lambda)\union V_i (так как множество инвариантов - set, то повторов не будет)
                                        # 89 //Update trace with replace and clear operation
                                        ecyc_without_t_inv_nodes = clear(set(ecyc), set(nodes_of_component))
                                        trace = replace(trace, ecyc, ecyc_without_t_inv_nodes)
                                        # 91-92 for(String del : temp){
                                    #        ecycClone.remove(del);}
                                    # 95-96?
                                    ecyc = self.e_cyc(trace)
                                    self.visited_cycs[tuple(ecyc)] = nodes_of_component
                                else:
                                    for aux in self.visited_cycs:  # line 114
                                        ecyc_without_t_inv_nodes = clear(set(ecyc), set(aux))
                                        trace = replace(trace, ecyc, ecyc_without_t_inv_nodes)

                                    # if (self.visited_cycs.get(ecyc).size() == 0):
                                    #    trace = removeAllXevent(trace, ecyc.get(0));

                                    # line 114

                        flag = flag and (len(ecyc) > 0)  # until trace not empty and cyc_e != empty set

    # Find the first elementary cyc in the trace
    def e_cyc(self, trace):
        analyzed_events = list()
        ecyc = list()
        for i in range(len(trace)):
            event = trace[i]
            if len(analyzed_events) > 0:
                if event in analyzed_events:
                    x = analyzed_events.index(event)
                    while x < len(analyzed_events):
                        ecyc.append(analyzed_events[x])
                        x += 1
                    self.no_nested_cyc = False
                    return ecyc
            analyzed_events.append((event))
        return analyzed_events

    def add_invariant(self, invariant_to_add): #invariant_to_add should be sorted beforehand
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

    def build_digraph_from_petri_net(net):
        """
        Builds a directed graph from a Petri net
            (for the purpose to add invisibles between inclusive gateways)
        Parameters
        -------------
        net
            Petri net
        Returns
        -------------
        digraph
            Digraph
        """
        import networkx as nx
        graph = nx.DiGraph()
        for place in net.places:
            graph.add_node(place.name)
        for trans in net.transitions:
            in_places = [x.source for x in list(trans.in_arcs)]
            out_places = [x.target for x in list(trans.out_arcs)]
            for pl1 in in_places:
                for pl2 in out_places:
                    graph.add_edge(pl1.name, pl2.name)
        return graph

    def build_causality_graph(self, cyc):
        import networkx as nx
        graph = nx.DiGraph()
        for place in cyc:
            graph.add_node(place) #если в сус лежат не просто имена то здесь надо достать имя
        #for in self.relations.
