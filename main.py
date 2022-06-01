import os
import pm4py
from copy import deepcopy
from pm4py.objects.log.obj import EventLog, Trace, Event

from TInvRecogniser import TInvRecogniser
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

import os
import time
from pm4py.algo.conformance.alignments.petri_net import algorithm as ali
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.visualization.petri_net import visualizer as pt_visualizer


import LowLevelLogPreprocessingMethods as preprocessing


def main():
    # pnml_path = os.path.join(os.path.dirname(__file__), "example.pnml")
    # net, marking, fmarking = petri_importer.apply(pnml_path)
    # gviz = pt_visualizer.apply(net)
    # pt_visualizer.view(gviz)

    file_path = os.path.join(os.path.dirname(__file__), 'сеть поболбше.1.2251028129059564290.xes')
    log = pm4py.read.read_xes(file_path)
    t_inv = TInvRecogniser(log)
    t_inv.fill_t_inv() #1.1
    print(t_inv.t_invariants)

    fixed_invariants = t_inv.t_invariants



    #1.2 find in log all possible cycle bodies to get a set of tuples
    # каждому циклу поставить в соответствие индекс
    possible_cycles_bodies, log_without_cycles_bodies = preprocessing.change_cycles_bodies_to_special_sym(log, fixed_invariants, 'cycle')
    print(log_without_cycles_bodies)
    #в каждой трассе заменить каждое полное тело цикла на "cycleN" где N - индекс цикла

    #mapping
    file_path = os.path.join(os.path.dirname(__file__), 'mapping.json')
    mapping = preprocessing.hierarchical_events_mapping(file_path)

    #transform log into hl, cycles remain as same symbols

    abstract_traces = []
    for trace in log_without_cycles_bodies:
        # trace_to_events_names_list = [event['concept:name'] for event in trace]
        abstract_traces.extend(preprocessing.detailed_events_to_abstract(trace, mapping))
    print(abstract_traces)
    print(type(abstract_traces[1][1]))

    abstract_cycle_bodies = {}
    for cycle_body in possible_cycles_bodies.keys():
        abstract_cycle_bodies[cycle_body] = preprocessing.detailed_events_to_abstract(possible_cycles_bodies.get(cycle_body), mapping)

    abstract_traces_with_hl_cycles_bodies = []
    # для каждой трассы в abstract_traces заменяем все циклы на их высокоуровневое представление
    for trace in abstract_traces:
        has_cycle = False
        new_trace = list.copy(trace)
        for i in possible_cycles_bodies.keys():
            j = 0
            while j < len(new_trace):
                event = new_trace[j]
                if event == 'cycle' + str(i):
                   has_cycle = True
                   for body in abstract_cycle_bodies[i]:
                       abstract_trace_with_hl_cycle_body = list(new_trace[0:j]) + body + list(new_trace[j + 1:len(new_trace)])
                       abstract_traces_with_hl_cycles_bodies.append(abstract_trace_with_hl_cycle_body)
                       new_trace = list.copy(abstract_trace_with_hl_cycle_body)
                j += 1
        if not has_cycle:
            abstract_traces_with_hl_cycles_bodies.append(new_trace)
        #заменяем в трассе ивент на его сайкл бади преобразованное в абстрактный вид
    trace_index_for_deleting = 0
    while trace_index_for_deleting < len(abstract_traces_with_hl_cycles_bodies):
        delete = False
        for event in abstract_traces_with_hl_cycles_bodies[trace_index_for_deleting]:
            if event.__contains__('cycle'):
                delete = True
        if delete:
            del abstract_traces_with_hl_cycles_bodies[trace_index_for_deleting]
        else:
            trace_index_for_deleting += 1
    print(abstract_traces_with_hl_cycles_bodies)
    #print(type(abstract_traces[1][1]))

    final_log = EventLog()
    for trace in abstract_traces_with_hl_cycles_bodies:
        t = Trace()
        for event in trace:
            e = Event()
            e["concept:name"] = event
            t.append(e)
        final_log.append(t)

    file_path_out = os.path.join(os.path.dirname(__file__), 'final_log.xes')
    xes_exporter.apply(final_log, file_path_out)


if __name__ == '__main__':
    main()
