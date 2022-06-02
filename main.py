import os
import pm4py
from copy import deepcopy
from pm4py.objects.log.obj import EventLog, Trace, Event

from TInvRecogniser import TInvRecogniser
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

import os
from datetime import datetime

from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pm4py.objects.petri_net.exporter as pn_exporter
import sys


import LowLevelLogPreprocessingMethods as preprocessing


def main():

        arr = os.listdir(os.path.dirname(__file__) + "/tests/50")
        arr.sort()
        ln = 0

        hl_net, hl_i_m, hl_f_m = petri_importer.apply(os.path.join(os.path.join(os.path.dirname(__file__), "highlevelnet.pnml")))
        fitnesses = []
        for path in arr:

            file_path = os.path.join(os.path.join(os.path.dirname(__file__), "tests/50"), path)
            print("start: log number " + str(ln))
            print(file_path)

            log = pm4py.read.read_xes(file_path)

            start_time = datetime.now()


            #print("mining time for initial log:")
            #print(datetime.now() - start_time)

            t_inv = TInvRecogniser(log)
            t_inv.fill_t_inv() #1.1

            fixed_invariants = t_inv.t_invariants
            for inv in t_inv.t_invariants:
                if 't4' in inv and 't11' in inv:
                    new_inv = list(inv)
                    new_inv.remove('t4')
                    new_inv.append('t10')
                    if(inv in fixed_invariants):
                        fixed_invariants.remove(inv)
                        fixed_invariants.add(tuple(new_inv))
                if 't6' in inv and 't10' in inv:
                    new_inv = list(inv)
                    new_inv.remove('t10')
                    new_inv.append('t4')
                    new_inv.append('t5')
                    if (inv in fixed_invariants):
                        fixed_invariants.remove(inv)
                        fixed_invariants.add(tuple(new_inv))

            #1.2 find in log all possible cycle bodies to get a set of tuples
            # каждому циклу поставить в соответствие индекс
            possible_cycles_bodies, log_without_cycles_bodies = preprocessing.change_cycles_bodies_to_special_sym(log, fixed_invariants, 'cycle')

            #mapping
            file_path = os.path.join(os.path.dirname(__file__), 'mapping.json')
            mapping = preprocessing.hierarchical_events_mapping(file_path)

            #transform log into hl, cycles remain as same symbols

            abstract_traces = []
            for trace in log_without_cycles_bodies:
                abstract_traces.extend(preprocessing.detailed_events_to_abstract(trace, mapping))

            abstract_cycle_bodies = {}
            for cycle_body in possible_cycles_bodies.keys():
                abstract_cycle_bodies[cycle_body] = preprocessing.detailed_events_to_abstract(possible_cycles_bodies.get(cycle_body), mapping)

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
                               for event_hl in set(body):
                                   if new_trace.__contains__(event_hl):
                                       if new_trace.index(event_hl) < j:
                                           body.remove(event_hl)
                                       else:
                                           new_trace.remove(event_hl)
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

            final_log = EventLog()
            for trace in abstract_traces_with_hl_cycles_bodies:
                t = Trace()
                for event in trace:
                    e = Event()
                    e["concept:name"] = event
                    t.append(e)
                final_log.append(t)
            final_log_file_name = 'final_log' + str(ln) + '.xes'
            file_path_out = os.path.join(os.path.dirname(__file__), final_log_file_name)
            xes_exporter.apply(final_log, file_path_out)

            net, initial_marking, final_marking = inductive_miner.apply(final_log)
            net_file_name = 'final_net_ind' + str(ln) + '.pnml'
            net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
            ln += 1
            pn_exporter.exporter.apply(net, initial_marking, net_path_out)

            replayed_traces = token_replay.apply(final_log, hl_net, hl_i_m, hl_f_m)

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
            fitnesses.append(fitness)
            #print("for " + str(len(final_log)) + " traces total")
            #print("end: log number" + str(ln-1))

        sum = 0
        for fit in fitnesses:
            print(fit)
            sum +=fit
        print("total average: " + str(sum/len(fitnesses)))


if __name__ == '__main__':
    main()
