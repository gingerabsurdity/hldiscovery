import os
import pm4py
from copy import deepcopy
from pm4py.objects.log.obj import EventLog, Trace, Event

from TInvRecogniser import TInvRecogniser
import LowLevelLogPreprocessingMethods as preprocessing


def main():
    file_path = os.path.join(os.path.dirname(__file__), 'сеть поболбше.1.2251028129059564290.xes')
    log = pm4py.read.read_xes(file_path)
    t_inv = TInvRecogniser(log)
    t_inv.fill_t_inv()
    print(t_inv.t_invariants)

    #mapping
    file_path = os.path.join(os.path.dirname(__file__), 'mapping.json')
    mapping = preprocessing.hierarchical_events_mapping(file_path)

    abstract_traces = []
    for trace in log:
        trace_to_events_names_list = [event['concept:name'] for event in trace]
        abstract_traces.extend(preprocessing.detailed_events_to_abstract(trace_to_events_names_list, mapping))
    print(abstract_traces)

def generate_large_log():
    L = EventLog()
    t0 = Event()
    t0["concept:name"] = "t0"
    t1 = Event()
    t1["concept:name"] = "t1"
    t2 = Event()
    t2["concept:name"] = "t2"
    t3 = Event()
    t3["concept:name"] = "t3"
    t4 = Event()
    t4["concept:name"] = "t4"
    t5 = Event()
    t5["concept:name"] = "t5"
    t6 = Event()
    t6["concept:name"] = "t6"
    t7 = Event()
    t7["concept:name"] = "t7"
    t8 = Event()
    t8["concept:name"] = "t8"
    t9 = Event()
    t9["concept:name"] = "t9"
    t10 = Event()
    t10["concept:name"] = "t10"
    t11 = Event()
    t11["concept:name"] = "t11"
    t12 = Event()
    t12["concept:name"] = "t12"
    t13 = Event()
    t13["concept:name"] = "t13"
    t14 = Event()
    t14["concept:name"] = "t14"
    t15 = Event()
    t15["concept:name"] = "t15"
    t16 = Event()
    t16["concept:name"] = "t16"
    t17 = Event()
    t17["concept:name"] = "t17"
    t18 = Event()
    t18["concept:name"] = "t18"
    t19 = Event()
    t19["concept:name"] = "t19"
    t20 = Event()
    t20["concept:name"] = "t20"
    t21 = Event()
    t21["concept:name"] = "t21"
    t22 = Event()
    t22["concept:name"] = "t22"
    t23 = Event()
    t23["concept:name"] = "t23"
    t24 = Event()
    t24["concept:name"] = "t24"
    t25 = Event()
    t25["concept:name"] = "t25"
    t26 = Event()
    t26["concept:name"] = "t26"
    t27 = Event()
    t27["concept:name"] = "t27"
    t = Trace() #без циклов
    t.append(t0)
    t.append(t1)
    t.append(t3)
    t.append(t13)
    t.append(t4)
    t.append(t5)
    t.append(t6)
    t.append(t14)
    t.append(t15)
    t.append(t7)
    t.append(t8)
    t.append(t9)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t25)
    t.append(t26)
    t.append(t27)
    for i in range(3):
        L.append(deepcopy(t))
    t = Trace() #без циклов
    t.append(t0)
    t.append(t2)
    t.append(t3)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t25)
    t.append(t26)
    t.append(t27)
    for i in range(4):
        L.append(deepcopy(t))
    t = Trace()  # без циклов
    t.append(t0)
    t.append(t2)
    t.append(t3)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t22)
    t.append(t23)
    t.append(t24)
    for i in range(4):
        L.append(deepcopy(t))
    t = Trace() #c циклом
    t.append(t0)
    t.append(t2)
    t.append(t3)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t19)
    t.append(t20)
    t.append(t21)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t25)
    t.append(t26)
    t.append(t27)
    for i in range(4):
        L.append(deepcopy(t))
    t = Trace()  # без циклов
    t.append(t0)
    t.append(t2)
    t.append(t3)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t19)
    t.append(t20)
    t.append(t21)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t19)
    t.append(t20)
    t.append(t21)
    t.append(t13)
    t.append(t4)
    t.append(t5)
    t.append(t6)
    t.append(t14)
    t.append(t15)
    t.append(t7)
    t.append(t8)
    t.append(t9)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t22)
    t.append(t23)
    t.append(t24)
    for i in range(4):
        L.append(deepcopy(t))
    return L

def generate_small_log():
    L = EventLog()
    t0 = Event()
    t0["concept:name"] = "t0"
    t1 = Event()
    t1["concept:name"] = "t1"
    t2 = Event()
    t2["concept:name"] = "t2"
    t3 = Event()
    t3["concept:name"] = "t3"
    t4 = Event()
    t4["concept:name"] = "t4"
    t5 = Event()
    t5["concept:name"] = "t5"
    t6 = Event()
    t6["concept:name"] = "t6"
    t7 = Event()
    t7["concept:name"] = "t7"
    t8 = Event()
    t8["concept:name"] = "t8"
    t9 = Event()
    t9["concept:name"] = "t9"
    t10 = Event()
    t10["concept:name"] = "t10"
    t11 = Event()
    t11["concept:name"] = "t11"
    t12 = Event()
    t12["concept:name"] = "t12"
    t13 = Event()
    t13["concept:name"] = "t13"
    t14 = Event()
    t14["concept:name"] = "t14"
    t15 = Event()
    t15["concept:name"] = "t15"
    t16 = Event()
    t16["concept:name"] = "t16"
    t17 = Event()
    t17["concept:name"] = "t17"
    t18 = Event()
    t18["concept:name"] = "t18"
    t19 = Event()
    t19["concept:name"] = "t19"
    t20 = Event()
    t20["concept:name"] = "t20"
    t21 = Event()
    t21["concept:name"] = "t21"
    t22 = Event()
    t22["concept:name"] = "t22"
    t23 = Event()
    t23["concept:name"] = "t23"
    t24 = Event()
    t24["concept:name"] = "t24"
    t25 = Event()
    t25["concept:name"] = "t25"
    t26 = Event()
    t26["concept:name"] = "t26"
    t27 = Event()
    t27["concept:name"] = "t27"
    t = Trace() #без циклов
    t.append(t0)
    t.append(t2)
    t.append(t3)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t25)
    t.append(t26)
    t.append(t27)
    L.append(deepcopy(t))
    t = Trace() #c циклом
    t.append(t0)
    t.append(t2)
    t.append(t3)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t19)
    t.append(t20)
    t.append(t21)
    t.append(t13)
    t.append(t10)
    t.append(t11)
    t.append(t14)
    t.append(t15)
    t.append(t12)
    t.append(t16)
    t.append(t17)
    t.append(t18)
    t.append(t25)
    t.append(t26)
    t.append(t27)
    L.append(deepcopy(t))
    return L

if __name__ == '__main__':
    main()
