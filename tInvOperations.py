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


class ShorterStartTaskEndKeeper(object):
    def __init__(self, log, relations):
        self.__log = log
        self.__relations = relations
        self.__visited_traces = set()
        self.__no_nested_cyc = True
        # HashMap<Integer, Vector<String>> tinvariants = new HashMap< Integer, Vector<String>>();
        self.t_invariants = {}
        self.visited_cycs = {}

    def fill_t_inv(self, log, relations):
        for trace in log:  # в оригинале был прогресс от лога отдельной переменной, а лог глобальной, в процедуре
            # запускалось от текущего прогресса и он инкрементился, то есть переходил к следующей трассе
            if trace:  # if (!trace.isEmpty()) {
                if trace not in self.__visited_traces:
                    self.__visited_traces.add(trace)  # чтобы не обрабатывать одинаковые трассы
                    print("Trace number: " + trace.index)
                    flag = True
                    while flag:
                        # Find the elementary cycle in trace if there are some
                        ecyc = self.e_cyc(trace)
                        if self.__no_nested_cyc: #if(noNestedCyc){
                            ecyc.sort()
                            self.add_invariant(ecyc)
                            flag = False
                        else:
                            if ecyc not in self.visited_cycs:   #if( !visitedeCycs.containsKey(ecyc) ){
                                dfg = dfg = dfg_discovery.apply(ecyc)
                                causality_graph = variants.alpha.apply(dfg)
                                scc_of_eCyc = nx.strongly_connected_components(causality_graph) #page 4 of tapia thesis


                            else:
                                #for(Vector<String> aux : visitedeCycs.get(ecyc)){
            					#trace = replaceClear(trace, aux, ecyc);
            				    #}
            				    #if(visitedeCycs.get(ecyc).size() == 0){
            				    #	trace = removeAllXevent(trace, ecyc.get(0));
            				    #}



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
                    self.__no_nested_cyc = False
                    return ecyc
            analyzed_events.append((event))
        return analyzed_events

    def add_invariant(self, invariant_to_add):
        add = True
        tinv_to_remove = list()
        if invariant_to_add not in self.t_invariants:
            for existing_invariant in self.t_invariants:
                if len(self.t_invariants[existing_invariant]) > len(invariant_to_add):
                    existing_invariant_set = set(self.t_invariants[existing_invariant])
                    invariant_to_add_set = set(invariant_to_add)
                    if invariant_to_add_set in existing_invariant_set:
                        tinv_to_remove.append(existing_invariant)
                    elif existing_invariant_set in invariant_to_add_set:
                        add = False
            for i in tinv_to_remove:
                self.t_invariants.pop(i)
                if add:
                    self.t_invariants[len(self.t_invariants) + 1] = invariant_to_add #нужен ли тут этот +1?




