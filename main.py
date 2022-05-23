import os
import pm4py

from TInvRecogniser import TInvRecogniser
import LowLevelLogPreprocessingMethods as preprocessing


def main():
    file_path = os.path.join(os.path.dirname(__file__), 'from_paper.xes')
    log = pm4py.read.read_xes(file_path)
   # t_inv = TInvRecogniser(log)
   # t_inv.fill_t_inv()
   # print(t_inv.t_invariants)

    #mapping
    file_path = os.path.join(os.path.dirname(__file__), 'mapping.json')
    mapping = preprocessing.hierarchical_events_mapping(file_path)


if __name__ == '__main__':
    main()
