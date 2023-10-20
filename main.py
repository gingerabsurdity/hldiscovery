import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
from TInvRecogniser import TInvRecogniser
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pm4py.objects.petri_net.exporter as pn_exporter
import os
import numpy as np
from pm4py.objects.petri_net.utils.incidence_matrix import IncidenceMatrix
from pm4py.objects.petri_net.importer import importer as petri_importer
import sympy
import copy
import csv
from pm4py.objects.conversion.log import converter as log_converter

import LowLevelLogPreprocessingMethods as preprocessing

import sys


def main():
        orig_stdout = sys.stdout
        f = open('out.txt', 'w')
        sys.stdout = f
        csvf = open(os.path.dirname(__file__) + '/tests/final.csv', 'w')
        writer = csv.writer(csvf)
        arr = os.listdir(os.path.dirname(__file__) + "/tests/evg_logs")
        #arr.sort()

        ln = 0

        #arr2 = arr[1:]
        arr2 = []
        arr2.append(arr[1])
        fitnesses = []
        for path in arr2:

            row = []

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
            t_inv.fill_t_inv() #1.1

            fixed_invariants = t_inv.t_invariants
            fixed_invariants = sorted(fixed_invariants)

            #1.2 find in log all possible cycle bodies to get a set of tuples
            # каждому циклу поставить в соответствие индекс
            possible_cycles_bodies, log_without_cycles_bodies = preprocessing.change_cycles_bodies_to_special_sym(log, fixed_invariants, 'cycle')

            print("possible cycles bodies:")
            print(possible_cycles_bodies)
            print("log without cycles bodies:")
            print(log_without_cycles_bodies)

            #mapping
            file_path = os.path.join(os.path.dirname(__file__), 'tests//evg_logs//activities.txt')
            mapping = preprocessing.mapping_from_txt_with_separators(file_path, "::")

            print(mapping)

            #transform log into hl, cycles remain as same symbols

            abstract_traces = []
            for trace in log_without_cycles_bodies:
                abstract_traces.extend(preprocessing.detailed_events_to_abstract(trace, mapping))

            abstract_cycle_bodies = {}
            for cycle_body in possible_cycles_bodies.keys():
                abstract_cycle_bodies[cycle_body] = preprocessing.detailed_events_to_abstract(possible_cycles_bodies.get(cycle_body), mapping)
            print("abstract possible invariants:")
            print(abstract_cycle_bodies.values())
            abstract_traces_with_hl_cycles_bodies = []
            trace_index = 0
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
                               #?for event_hl in set(body):
                               #?    if new_trace.__contains__(event_hl):
                               #?        if new_trace.index(event_hl) < j:
                               #?            body.remove(event_hl)
                               #?        else:
                               #?            new_trace.remove(event_hl)
                               abstract_trace_with_hl_cycle_body = list(new_trace[0:j]) + body + list(new_trace[j + 1:len(new_trace)])
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
            #print(abstract_traces_with_hl_cycles_bodies)
            #print(type(abstract_traces[1][1]))
            print(abstract_traces_with_hl_cycles_bodies)

            final_log = EventLog()
            for trace in abstract_traces_with_hl_cycles_bodies:
                t = Trace()
                for event in trace:
                    e = Event()
                    e["concept:name"] = event
                    t.append(e)
                final_log.append(t)
            final_log_file_name = '2912BPIC17_final_log.xes'
            file_path_out = os.path.join(os.path.dirname(__file__), final_log_file_name)
            xes_exporter.apply(final_log, file_path_out)

            net, hlinitial_marking, hlfinal_marking = inductive_miner.apply(final_log)
            net_file_name = '2912BPIC17_final_net_ind' + str(ln) + '.pnml'
            net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
            ln += 1
            pn_exporter.exporter.apply(net, hlinitial_marking, net_path_out)
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

            #print("invariants from net:")
            #print(invariants_names)

            final_detailed_log = EventLog()
            for trace in initial_log:
                new_detailed_trace = Trace()
                trace_events_bool = dict()
                i = 0
                for event in trace:
                    if event["concept:name"] in trace_events_bool:
                        trace_events_bool[event["concept:name"]]['positions'].append(i)
                    else:
                        event_ordbool = dict()
                        event_ordbool['event'] = event
                        event_ordbool['positions'] = [i]
                        event_ordbool['processed'] = False
                        trace_events_bool[event["concept:name"]] = event_ordbool
                    i+=1


                for event in trace:
                    # идем по детальной трассе, для каждого события находим соответствующее ему абстрактное
                    # и забираем из детального все которые ему принадлежат
                    # если их еще не было в рамках этого абстрактного события, то записываем в лог
                    # значит надо хранить какие события мы в рамках этого события обработали в одном массиве, и не забывать убирать их из лога
                    # чтобы потом обрабатываеть только еще не обработанные
                    # на построенном логе сделать прогон реплая на низкоуровневой модели



                    detailed_event = event
                    abstract_event = None
                    keys = [key for key in mapping.keys() if detailed_event["concept:name"] in mapping[key]]
                    if len(keys) > 0:
                        abstract_event = keys[0]
                    if abstract_event is not None:
                        #здесь выписываем все события которые есть в логе и в mapping[abstract_event]
                        #удаляя их из исходного лога или помечая как взятые в отдельном массиве, например

                        for corresponding_detailed_event in mapping[abstract_event]:
                            if corresponding_detailed_event in trace_events_bool and trace_events_bool[corresponding_detailed_event]['positions']:
                                trace_events_bool[corresponding_detailed_event]['positions'].pop(0)
                                e = Event()
                                e["concept:name"] = corresponding_detailed_event
                                new_detailed_trace.append(e)
                    else:
                        new_detailed_trace.append(detailed_event)

                final_detailed_log.append(new_detailed_trace)

            detailed_net, initial_marking, final_marking = inductive_miner.apply(initial_log)
            row.append(len(detailed_net.transitions))
            row.append(len(detailed_net.places))
            replayed_traces = token_replay.apply(final_log, net, hlinitial_marking, hlfinal_marking)

            net_file_name = '2912BPIC17_final_low-level_net_ind' + str(ln) + '.pnml'
            net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
            ln += 1
            #pn_exporter.exporter.apply(detailed_net, initial_marking, net_path_out)

            final_log_file_name = '2912BPIC17_final_low_level_log' + str(ln) + '.xes'
            file_path_out = os.path.join(os.path.dirname(__file__), final_log_file_name)
            xes_exporter.apply(final_detailed_log, file_path_out)

            r = 0
            p = 0
            m = 0
            c = 0
            trace_num = 0

            for trace_result in replayed_traces:
                r += trace_result.get('remaining_tokens')
                p += trace_result.get('produced_tokens')
                m += trace_result.get('missing_tokens')
                c += trace_result.get('consumed_tokens')
                # if(len(trace_result["transitions_with_problems"])>0):
                #     print("problem with transitions: ")
                #     for x in trace_result["transitions_with_problems"]:
                #         print(x.label + ", ")
                trace_num += 1
            fitness = 0.5 * (1 - r / p) + 0.5 * (1 - m / c)
            #print("fitness of final log with initial model: ")
            print(fitness)
            row.append(len(final_log))
            row.append(fitness)
            fitnesses.append(fitness)

            precision = pm4py.algo.evaluation.precision.variants.align_etconformance.apply(final_log, net,hlinitial_marking, hlfinal_marking)
            row.append(precision)
            print(precision)
            writer.writerow(row)

        sum = 0
        for fit in fitnesses:
            print(fit)
            sum +=fit
        print("total average: " + str(sum/len(fitnesses)))

        sys.stdout = orig_stdout
        f.close()
        csvf.close()


if __name__ == '__main__':
    main()
