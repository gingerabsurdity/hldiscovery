import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
from TInvRecogniser import TInvRecogniser
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristic_miner
import pm4py.objects.petri_net.exporter as pn_exporter
import os
import numpy as np
from pm4py.objects.petri_net.utils.incidence_matrix import IncidenceMatrix
from pm4py.objects.petri_net.importer import importer as petri_importer
import sympy
import copy

from pm4py.objects.conversion.log import converter as log_converter
import pnml_to_gml_converter

import LowLevelLogPreprocessingMethods as preprocessing
import subnets

import sys


def main():
    f = open('out.txt', 'w')
    sys.stdout = f
    # csvf = open(os.path.dirname(__file__) + '/tests/final.csv', 'w')
    # writer = csv.writer(csvf)
    # arr = os.listdir(os.path.dirname(__file__) + "/tests/evg_logs")
    relevant_path = os.path.dirname(__file__) + "/tests/evg_logs"

    included_extensions = ['xes']
    file_names = [fn for fn in os.listdir(relevant_path)
                  if any(fn.endswith(ext) for ext in included_extensions)]
    ln = 0

    for path in file_names:
        row = []
        print(__file__)
        file_path = os.path.join(os.path.dirname(__file__) + "\\tests\\evg_logs", path)
        print("start: log number " + str(ln))
        print(file_path)
        row.append(file_path)

        initial_log = pm4py.read.read_xes(file_path)
        log = copy.deepcopy(initial_log)
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

        for trace in log:
            trace_to_events_names_list = [event['concept:name'] for event in trace]
            print(trace_to_events_names_list)

        t_inv = TInvRecogniser(log)
        t_inv.fill_t_inv()

        fixed_invariants = t_inv.t_invariants
        fixed_invariants = sorted(fixed_invariants)

        # 1.2 find in log all possible cycle bodies to get a set of tuples
        # каждому циклу поставить в соответствие индекс
        possible_cycles_bodies, log_without_cycles_bodies = preprocessing.change_cycles_bodies_to_special_sym(log,
                                                                                                              fixed_invariants,
                                                                                                              'cycle')

        print("possible cycles bodies:")
        print(possible_cycles_bodies)
        print("log without cycles bodies:")
        print(log_without_cycles_bodies)

        # mapping
        print(__file__)
        file_path = os.path.join(os.path.dirname(__file__), 'tests//evg_logs//activities.txt')
        print(file_path)
        mapping = preprocessing.mapping_from_log(log, "hierarchy_level")
        # mapping = preprocessing.mapping_from_log(log, " ")

        print(mapping)

        # file_path = os.path.join(os.path.dirname(__file__), 'tests//evg_logs//activities_instances.txt')
        # dict_for_events = subnets.read_activities_info(file_path)

        # формирование массива подсетей
        dict_event_to_log = subnets.generate_nets_by_mapping(log, mapping, "activity")

        # вывод подсетей
        subnets.subnets_writers(dict_event_to_log)

        abstract_traces = []
        trace_number = 0
        for trace in log_without_cycles_bodies:
            abstract_traces.extend(preprocessing.detailed_events_to_abstract(trace, mapping, "activity"))
            trace_number += 1

        abstract_cycle_bodies = {}
        for cycle_body in possible_cycles_bodies.keys():
            abstract_cycle_bodies[cycle_body] = preprocessing.detailed_events_to_abstract(
                possible_cycles_bodies.get(cycle_body), mapping)
        print("abstract possible invariants:")
        print(abstract_cycle_bodies.values())
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
                            # ?for event_hl in set(body):
                            # ?    if new_trace.__contains__(event_hl):
                            # ?        if new_trace.index(event_hl) < j:
                            # ?            body.remove(event_hl)
                            # ?        else:
                            # ?            new_trace.remove(event_hl)
                            abstract_trace_with_hl_cycle_body = list(new_trace[0:j]) + body + list(
                                new_trace[j + 1:len(new_trace)])
                            abstract_traces_with_hl_cycles_bodies.append(abstract_trace_with_hl_cycle_body)
                            # generated = False
                            # for event_hl in set(body):
                            #     if abstract_trace_with_hl_cycle_body.count(event_hl) > 1:
                            #         generated = True
                            #           # and len(abstract_traces[trace_index])>len(set(abstract_traces[trace_index])):
                            #         traces_with_event = preprocessing.generate_traces_by_duplicated_events(
                            #             abstract_trace_with_hl_cycle_body, event_hl)
                            #         set_traces_with_event = set()
                            #         for draft_trace in traces_with_event:
                            #             draft_trace = preprocessing.remove_stuttering(draft_trace)
                            #             set_traces_with_event.add(tuple(draft_trace))
                            #         abstract_trace_with_hl_cycle_body_list = [list(x) for x in set_traces_with_event][0]
                            #         abstract_traces_with_hl_cycles_bodies.append(abstract_trace_with_hl_cycle_body_list)
                            #
                            #             #trace_index += len(set_traces_with_event)
                            # if not generated:
                            #     abstract_traces_with_hl_cycles_bodies.append(abstract_trace_with_hl_cycle_body)

                            new_trace = list.copy(abstract_trace_with_hl_cycle_body)
                    j += 1
            if not has_cycle:
                abstract_traces_with_hl_cycles_bodies.append(new_trace)
            # заменяем в трассе ивент на его сайкл бади преобразованное в абстрактный вид
        trace_index_for_deleting = 0
        while trace_index_for_deleting < len(abstract_traces_with_hl_cycles_bodies):
            delete = False
            for event in abstract_traces_with_hl_cycles_bodies[trace_index_for_deleting]:
                if str(event).__contains__('cycle'):
                    delete = True
            if delete:
                del abstract_traces_with_hl_cycles_bodies[trace_index_for_deleting]
            else:
                trace_index_for_deleting += 1

        print(abstract_traces_with_hl_cycles_bodies)

        final_log = EventLog()
        for trace in abstract_traces_with_hl_cycles_bodies:
            t = Trace()
            for event in trace:
                e = Event()
                e["concept:name"] = event
                t.append(e)
            final_log.append(t)
        final_log_file_name = 'final_log.xes'
        file_path_out = os.path.join(os.path.dirname(__file__), final_log_file_name)
        xes_exporter.apply(final_log, file_path_out)

        # process_tree = heuristic_miner.apply(final_log)
        # net, initial_marking, final_marking = pm4py.convert_to_petri_net(process_tree)
        net, initial_marking, final_marking = heuristic_miner.apply(final_log)
        net_file_name = 'contest_final_net_heu' + str(ln) + '.pnml'
        net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
        ln += 1
        pn_exporter.exporter.apply(net, initial_marking, net_path_out)
        row.append(len(net.transitions))
        row.append(len(net.places))

        incidence_matrix = IncidenceMatrix(net)

        # exp from book https://www7.in.tum.de/~esparza/fcbook-middle.pdf
        t_inv = sympy.Matrix(incidence_matrix.a_matrix).nullspace()
        t_inv = np.array(t_inv).astype(np.float64)

        invariants_names = []
        for inv in t_inv:
            if np.all(inv >= 0):
                invariant_names = []
                t_index = 0
                for t in inv:
                    if t == 1:
                        invariant_names.append(list(incidence_matrix.transitions.keys())[
                                                   list(incidence_matrix.transitions.values()).index(
                                                       t_index)].label)
                    t_index += 1
                invariants_names.append(invariant_names)


if __name__ == '__main__':
    main()
