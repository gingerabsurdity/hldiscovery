import os
import pm4py

from tInvOperations import ShorterStartTaskEndKeeper


def main():
    file_path = os.path.join(os.path.dirname(__file__), 'from_paper.xes')
    log = pm4py.read.read_xes(file_path)
    t_inv = ShorterStartTaskEndKeeper(log)
    t_inv.fill_t_inv()
    print("end")


if __name__ == '__main__':
    main()
