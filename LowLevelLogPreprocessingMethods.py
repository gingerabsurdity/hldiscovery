import json


def hierarchical_events_mapping(json_file_name):
    mapping = {}
    with open(json_file_name) as json_file:
        mapping = json.load(json_file)
    return mapping


def detailed_events_to_abstract(trace, mapping):
    abstract_trace = []
    for detailed_event in trace:
        detailed_event_string = ''
        if not isinstance(detailed_event, str):
            detailed_event_string = detailed_event["concept:name"]
        else:
            detailed_event_string = detailed_event
        keys = [key for key in mapping.keys() if detailed_event_string in mapping[key]]
        if len(keys) > 0:
            abstract_event = keys[0]
        else:
            abstract_trace.append(detailed_event_string)
        abstract_trace.append(abstract_event)  # create abstract trace with duplicates
    i = 0
    abstract_trace = remove_stuttering(abstract_trace)
    abstract_traces = [abstract_trace]
    for event in set(abstract_trace):
        if abstract_trace.count(event) > 1:
            trace_index = 0
            #for trace in abstract_traces:

            while trace_index < len(abstract_traces): # and len(abstract_traces[trace_index])>len(set(abstract_traces[trace_index])):
                traces_with_event = generate_traces_by_duplicated_events(abstract_traces[trace_index], event)
                set_traces_with_event = set()
                for draft_trace in traces_with_event:
                    draft_trace = remove_stuttering(draft_trace)
                    set_traces_with_event.add(tuple(draft_trace))
                abstract_traces.remove(abstract_traces[trace_index])
                abstract_traces[trace_index:trace_index] = [list(x) for x in set_traces_with_event]
                trace_index += len(set_traces_with_event)

    trace_index_for_deleting = 0
    abstract_traces_set = set()
    while trace_index_for_deleting < len(abstract_traces):
        if len(set(abstract_traces[trace_index_for_deleting])) != len(abstract_traces[trace_index_for_deleting]):
            del abstract_traces[trace_index_for_deleting]
        else:
            abstract_traces_set.add(tuple(abstract_traces[trace_index_for_deleting]))
            trace_index_for_deleting += 1
    abstract_traces_set_to_lists = []
    for a_trace in abstract_traces_set:
        abstract_traces_set_to_lists.append(list(a_trace))
    return abstract_traces_set_to_lists

# def cycle_body_to_abstract(cycle, mapping):
#     abstract_trace = []
#     for detailed_event in trace:
#         keys = [key for key in mapping.keys() if detailed_event in mapping[key]]
#         if len(keys) > 0:
#             abstract_event = keys[0]
#         else:
#             abstract_trace.append(detailed_event)
#         abstract_trace.append(abstract_event)  # create abstract trace with duplicates
#     i = 0
#     abstract_trace = remove_stuttering(abstract_trace)
#     abstract_traces = [abstract_trace]
#     for event in set(abstract_trace):
#         if abstract_trace.count(event) > 1:
#             for trace in abstract_traces:
#                 traces_with_event = generate_traces_by_duplicated_events(trace, event)
#                 for draft_trace in traces_with_event:
#                     draft_trace = remove_stuttering(draft_trace)
#                 abstract_traces.remove(trace)
#                 abstract_traces.extend(traces_with_event)
#     return abstract_traces


def remove_stuttering(trace):
    i = 0
    while i < len(trace) - 1:
        if trace[i] == trace[i + 1]:
            del trace[i + 1]  # remove stuttering
        else:
            i += 1
    return trace


def generate_traces_by_duplicated_events(trace, event):
    traces = []
    indexes = []
    k = 0
    for i in range(len(trace)):
        if trace[i] == event:
            indexes.append(k)
        k += 1

    for index in indexes:
        changed_trace = list.copy(trace)
        j = 0
        i = 0
        while i < len(changed_trace):
            if changed_trace[i] == event:
                if j != indexes.index(index) and event != "e0":
                    del changed_trace[i]
                    i -= 1
                j += 1
            i += 1
        traces.append(changed_trace)
    if len(traces) == 0:
        traces.append(trace)
    return traces

def find_set_of_cycles_bodies(log, t_invariants):
    cycles_bodies = set()
    cycles_bodies_dict = {}
    for trace in log:
        for cycle in t_invariants:
            presented_elements = set()
            cycle_body = []
            for event in trace:
                if event["concept:name"] in cycle:
                    if event["concept:name"] not in presented_elements:
                        presented_elements.add(event["concept:name"])
                        cycle_body.append(event["concept:name"])
            if set(cycle) == presented_elements:
                cycles_bodies.add(tuple(cycle_body))
    i = 0
    for cycle_body in cycles_bodies:
        cycles_bodies_dict[i] = cycle_body
        i += 1
    print("possible cycle bodies:")
    print(cycles_bodies_dict)
    return cycles_bodies_dict


def change_cycles_bodies_to_special_sym(log, t_invariants, symbol): #EventLog, set(tuple), str
    possible_cycles_bodies = find_set_of_cycles_bodies(log, t_invariants) #dict{index: body}
    for trace in log:
        for cycle_body in possible_cycles_bodies:
            i = 0
            for event in trace:
                if i < len(possible_cycles_bodies[cycle_body]) and event["concept:name"] == possible_cycles_bodies[cycle_body][i]:
                    i += 1
            if i == len(possible_cycles_bodies[cycle_body]):
                j = 0

                for event_current in trace:
                    if j < len(possible_cycles_bodies[cycle_body]) and event_current["concept:name"] == possible_cycles_bodies[cycle_body][j]:
                        j += 1
                        event_current["concept:name"] = symbol + str(cycle_body)
    return possible_cycles_bodies, log