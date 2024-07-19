import json


def mapping_from_json_file(json_file_name):
    mapping = {}
    with open(json_file_name) as json_file:
        mapping = json.load(json_file)
    return mapping


def mapping_from_txt_with_separators(file_path, separator_for_events, separator_for_activity_name=""):
    f = open(file_path, "r")
    mapping = {}
    current_key_number = 0
    for x in f:
        if separator_for_activity_name and x.count(separator_for_activity_name) > 0:
            x_parts = x.strip().split(separator_for_activity_name)
            current_key = x_parts[0]
            x = x_parts[1]
        else:
            current_key = current_key_number
            current_key_number += 1

        hl_event_to_ll_event = x.strip().split(separator_for_events)

        # current_key_number = len(mapping.keys())
        if len(hl_event_to_ll_event) < 2:
            mapping[current_key] = []
            mapping[current_key].append(hl_event_to_ll_event[0])
        else:
            mapping[current_key] = hl_event_to_ll_event

    return mapping


def mapping_from_log_by_separator(initial_log, cycle_prefix="cycle", separator=""):
    mapping = dict()

    for trace in initial_log:
        for event in trace:
            concept_name = event['concept:name']
            if not (cycle_prefix  in concept_name):
                if concept_name.count(separator) > 0:
                    group = '' + concept_name.split(separator)[0] + concept_name.split(separator)[1]
                else:

                    group = concept_name
                if group not in mapping:
                    mapping[group] = set()
                mapping[group].add(event['concept:name'])
    return mapping


def mapping_from_log(initial_log, activity_tag_prefix):
    mapping = dict()

    for trace in initial_log:
        for event in trace:
            concept_name = event['concept:name']

            if event[activity_tag_prefix]:
                group = event[activity_tag_prefix]
            else:
                group = concept_name
            if group not in mapping:
                mapping[group] = set()
            mapping[group].add(event['concept:name'])
    return mapping


def add_other_events_to_mapping(log, mapping):
    # TODO
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
            abstract_trace.append(abstract_event)  # create abstract trace with duplicates
        else:
            abstract_trace.append(detailed_event_string)

    abstract_trace = remove_stuttering(abstract_trace)
    abstract_traces = [abstract_trace]
    for event in set(abstract_trace):
        if abstract_trace.count(event) > 1:
            trace_index = 0
            # for trace in abstract_traces:

            while trace_index < len(
                    abstract_traces):  # and len(abstract_traces[trace_index])>len(set(abstract_traces[trace_index])):
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


def detailed_events_to_abstract(trace, mapping, activity_tag = ""):
    abstract_trace = []
    detailed_event_number = 0
    for detailed_event in trace:
        detailed_event_string = ''
        if not isinstance(detailed_event, str):
            detailed_event_string = detailed_event["concept:name"]
        else:
            detailed_event_string = detailed_event
        keys = [key for key in mapping.keys() if detailed_event_string in mapping[key]]
        if len(keys) > 0:
            abstract_event = keys[0]
            abstract_trace.append(abstract_event)  # create abstract trace with duplicates
        else:
            abstract_trace.append(detailed_event_string)
    detailed_event_number += 1

    abstract_trace = remove_stuttering(abstract_trace)
    abstract_traces = [abstract_trace]
    for event in set(abstract_trace):
        if abstract_trace.count(event) > 1:
            trace_index = 0
            # for trace in abstract_traces:

            while trace_index < len(
                    abstract_traces):  # and len(abstract_traces[trace_index])>len(set(abstract_traces[trace_index])):
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


def remove_stuttering(trace):
    i = 0
    while i < len(trace) - 1:
        if trace[i] == trace[i + 1]:
            del trace[i + 1]  # remove stuttering
        else:
            i += 1
    return trace


def first_and_last_event_occurrence(trace, event):
    indexes = ()
    indexes['first'] = trace.index(event)
    indexes['last'] = len(trace) - 1 - trace[::-1].index(event)
    return indexes


def generate_traces_by_duplicated_events(trace, event):
    traces = []
    indexes = []

    k = 0
    for i in range(len(trace)):
        if trace[i] == event:
            indexes.append(k)
        k += 1
    first_index_of = trace.index(event)
    last_index_of = len(trace) - 1 - trace[::-1].index(event)
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
    for cycle_body in sorted(cycles_bodies):
        cycles_bodies_dict[i] = cycle_body
        i += 1
    return cycles_bodies_dict


def change_cycles_bodies_to_special_sym(log, t_invariants, symbol):  # EventLog, set(tuple), str
    possible_cycles_bodies = find_set_of_cycles_bodies(log, t_invariants)  # dict{index: body}
    for trace in log:
        for cycle_body in possible_cycles_bodies:
            i = 0
            for event in trace:
                if i < len(possible_cycles_bodies[cycle_body]) and event["concept:name"] == \
                        possible_cycles_bodies[cycle_body][i]:
                    i += 1
            if i == len(possible_cycles_bodies[cycle_body]):
                j = 0

                for event_current in trace:
                    if j < len(possible_cycles_bodies[cycle_body]) and event_current["concept:name"] == \
                            possible_cycles_bodies[cycle_body][j]:
                        j += 1
                        event_current["concept:name"] = symbol + str(cycle_body)
    return possible_cycles_bodies, log
