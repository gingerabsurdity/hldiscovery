import json


def hierarchical_events_mapping(json_file_name):
    mapping = {}
    with open(json_file_name) as json_file:
        mapping = json.load(json_file)
        print(mapping)
    return mapping


def detailed_events_to_abstract(trace, mapping):
    abstract_trace = []
    for detailed_event in trace:
        keys = [key for key, value in mapping.items() if detailed_event in value]
        abstract_event = keys[0]
        abstract_trace.append(abstract_event)  # create abstract trace with duplicates
    i = 0
    abstract_trace = remove_stuttering(abstract_trace)
    abstract_traces = []
    abstract_traces.append(abstract_trace)
    for event in set(abstract_trace):
        for trace in abstract_traces:
            traces_with_event = generate_traces_by_duplicated_events(abstract_trace, event)
            for draft_trace in traces_with_event:
                draft_trace = remove_stuttering(draft_trace)
            abstract_traces.remove(trace)
            abstract_traces.extend(traces_with_event)
    return abstract_traces


def remove_stuttering(trace):
    i = 0
    while i < len(trace) - 2:
        if trace[i] == trace[i + 1]:
            del trace[i + 1]  # remove stuttering
        else:
            i += 1
    return trace


def generate_traces_by_duplicated_events(trace, event):
    traces = []
    indexes = []
    for i in range(len(trace)):
        if trace[i] == event:
            indexes.append(i)
    for index in indexes:
        changed_trace = trace
        new_indexes = indexes
        new_indexes.remove(index)
        for i in sorted(new_indexes, reverse=True):
            del changed_trace[i]
        traces.append(changed_trace)
    if len(traces) == 0:
        traces.append(trace)
    return traces
