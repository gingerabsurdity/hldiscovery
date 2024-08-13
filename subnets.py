import os
import pm4py
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pm4py.objects.petri_net.exporter as pn_exporter
import pnml_to_gml_converter
from pm4py.algo.discovery.heuristics import algorithm as heuristic_miner
import LowLevelLogPreprocessingMethods


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

def generate_nets_by_log_info(log, mapping, activity_tag=""):
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
                else:
                    trace_for_event.append(dfs(mapping, event, detailed_event_string, {}))
            if len(trace_for_event) > 0:
                logs_mapping[event].append(trace_for_event)
    return logs_mapping


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
                else:
                    trace_for_event.append(dfs(mapping, event, detailed_event_string, {}))
            if len(trace_for_event) > 0:
                logs_mapping[event].append(trace_for_event)
    return logs_mapping

def generate_nets_by_activity_set(log, activity_set, activity_tag = "", separator="_", first_level_index = 0):
    global groups
    logs_by_activities = dict()
    for event in activity_set:
        logs_by_activities[event] = []
        for trace in log:
            trace_for_event = []
            for detailed_event in trace:
                try:
                    groups = {int(key.replace(activity_tag + separator, '')): val for key, val in detailed_event.items()
                              if key.startswith(activity_tag)}
                except ValueError as ve:
                    print(ve)

                sorted_groups = dict(sorted(groups.items()))
                if event.name in sorted_groups.values():
                    deeper_level = list(sorted_groups.values()).index(event.name) + first_level_index + 1
                    if deeper_level >= len(sorted_groups):
                        deeper_level_activity = detailed_event['concept:name']
                    else:
                        deeper_level_activity = list(sorted_groups.values())[deeper_level]
                        #deeper_level_activity = sorted_groups[deeper_level]
                    trace_for_event.append(deeper_level_activity)
            if len(trace_for_event) > 0:
                logs_by_activities[event].append(trace_for_event)
    return logs_by_activities



def generate_nets_by_detailed_events_mapping(log, mapping, mapping_for_detailed_events):
    logs_mapping = dict()
    for event in mapping.keys():
        logs_mapping[event] = []
        if event == 'Activity_2640':
            print(2640)
        for trace in log:
            trace_for_event = []
            for detailed_event in trace:

                if not isinstance(detailed_event, str):
                    detailed_event_string = detailed_event["concept:name"]
                else:
                    detailed_event_string = detailed_event
                if detailed_event_string == 'GC/RestartEEStart':
                    print('GC/RestartEEStart')
                if event in mapping_for_detailed_events[detailed_event_string].values():
                    level = list(mapping_for_detailed_events[detailed_event_string].keys())[list(reversed(list(mapping_for_detailed_events[detailed_event_string].values()))).index(event)] #list(mapping_for_detailed_events[detailed_event_string].keys())[list(reversed(list(mapping_for_detailed_events[detailed_event_string].values()))).index(event)]
                    if level == max(mapping_for_detailed_events[detailed_event_string].keys()):
                        trace_for_event.append(detailed_event_string)
                    else:
                        try:
                            trace_for_event.append(mapping_for_detailed_events[detailed_event_string][list(mapping_for_detailed_events[detailed_event_string].values()).index(event) + 1]) #depends on the first index in level mapping : level + 1 if the indexation starts from
                        except KeyError:
                            print(mapping_for_detailed_events[detailed_event_string].values())
            if len(trace_for_event) > 0:
                logs_mapping[event].append(trace_for_event)
    return logs_mapping


def dfs(G, v, desired, discovered):
    """find the next level nested event to create the abstract net
    args:
    G - dictionary for every abstract event with every nested lower-level event
    v - the desired event name

    return:
    the parent for desired event
    """
    discovered[v] = True
    for w in G[v]:
        if w == desired:
            return v
        if w not in discovered:
            dfs(G, w, desired, discovered)

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
        if(not ('cycle' in str(event))):
            log_for_event = list_of_string_to_event_log(dict_event_to_log[event])
            final_log_file_name = str(event) + '_final_log.xes'
            file_path_out = os.path.join(os.path.dirname(__file__), final_log_file_name)
            xes_exporter.apply(log_for_event, file_path_out)
            #process_tree = inductive_miner.apply(log_for_event)
            net, initial_marking, final_marking = heuristic_miner.apply(log_for_event)
            #net, initial_marking, final_marking = pm4py.convert_to_petri_net(process_tree)
            net_file_name = str(event) + 'log_sample_heu.pnml'
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
