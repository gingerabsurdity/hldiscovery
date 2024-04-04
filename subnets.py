import os
import pm4py
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pm4py.objects.petri_net.exporter as pn_exporter
import pnml_to_gml_converter
from pm4py.algo.discovery.heuristics import algorithm as heuristic_miner


def list_of_string_to_event_log(list_of_strings):
    final_log = EventLog()
    for trace in list_of_strings:
        t = Trace()
        for event in trace:
            e = Event()
            e["concept:name"] = event
            t.append(e)
        final_log.append(t)
    return final_log


def generate_nets_by_mapping(log, mapping, activity_tag=""):
    logs_mapping = dict()
    for event in mapping.keys():
        logs_mapping[event] = []
        for trace in log:
            trace_for_event = []
            for detailed_event in trace:
                if not isinstance(detailed_event, str):
                    detailed_event_string = detailed_event["concept:name"]
                else:
                    detailed_event_string = detailed_event
                if detailed_event_string in mapping[event]:
                    if activity_tag != "":
                        if detailed_event[activity_tag] == event:
                            trace_for_event.append(detailed_event_string)
                    else:
                        trace_for_event.append(detailed_event_string)
            if len(trace_for_event) > 0:
                logs_mapping[event].append(trace_for_event)
    return logs_mapping


def generate_nets_by_mapping_and_activities_dict(log, mapping, dict_for_events):
    logs_mapping = dict()
    for event in mapping.keys():
        logs_mapping[event] = []
        trace_number = 0
        for trace in log:
            trace_for_event = []
            detailed_event_number = 0
            for detailed_event in trace:
                if not isinstance(detailed_event, str):
                    detailed_event_string = detailed_event["concept:name"]
                else:
                    detailed_event_string = detailed_event
                if detailed_event_string in mapping[event]:
                    if event in dict_for_events.keys() and trace_number in dict_for_events.get(event):
                        if int(dict_for_events.get(event).get(trace_number).get(
                                'start_event')) <= detailed_event_number < int(
                                dict_for_events.get(event).get(trace_number).get('events_number')):
                            trace_for_event.append(detailed_event_string)
                detailed_event_number += 1
            if len(trace_for_event) > 0:
                logs_mapping[event].append(trace_for_event)
            trace_number += 1
    return logs_mapping


def subnets_writers(dict_event_to_log):
    for event in dict_event_to_log.keys():
        log_for_event = list_of_string_to_event_log(dict_event_to_log[event])
        final_log_file_name = str(event) + '_final_log.xes'
        file_path_out = os.path.join(os.path.dirname(__file__), final_log_file_name)
        xes_exporter.apply(log_for_event, file_path_out)
        process_tree = inductive_miner.apply(log_for_event)
        #net, initial_marking, final_marking = heuristic_miner.apply(log_for_event)
        net, initial_marking, final_marking = pm4py.convert_to_petri_net(process_tree)
        net_file_name = str(event) + '_contest_net_heu.pnml'
        net_path_out = os.path.join(os.path.dirname(__file__), net_file_name)
        pn_exporter.exporter.apply(net, initial_marking, net_path_out)
        pnml_to_gml_converter.generate_gml(net)


def read_activities_info(file_name):
    file1 = open(file_name, 'r')
    lines = file1.readlines()

    count = 0
    dict_for_traces = {}
    dict_for_events = {}
    # Strips the newline character
    for line in lines:

        if line.find('Trace') != -1:
            trace_number = count

            count += 1
        else:
            if line.strip():
                no_brackets = line.strip()[1:-1]
                if dict_for_traces.get(trace_number):
                    dict_for_traces[trace_number].append(no_brackets.split(", "))
                else:
                    dict_for_traces[trace_number] = [no_brackets.split(", ")]

    for trace in dict_for_traces:

        for activity in dict_for_traces.get(trace):
            if dict_for_events.get(activity[0]):
                dict_for_events[activity[0]][trace] = {'start_event': activity[1],
                                                       'events_number': activity[2]}
            else:
                dict_for_events[activity[0]] = {trace:
                                                    {'start_event': activity[1],
                                                     'events_number': activity[2]}}

    return dict_for_events
