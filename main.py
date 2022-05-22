import os
import pm4py

from tInvOperations import ModelStructureRecogniser


def main():
    file_path = os.path.join(os.path.dirname(__file__), 'from_paper.xes')
    log = pm4py.read.read_xes(file_path)
    t_inv = ModelStructureRecogniser(log)
    t_inv.fill_t_inv()
    print(t_inv.t_invariants)


if __name__ == '__main__':
    main()
