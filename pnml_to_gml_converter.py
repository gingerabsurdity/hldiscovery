#!/usr/bin/env python3

def generate_gml(net):
    """
        Generates basic representation of network in GML.
        No layout is applied: for that use yEd or similar tools.
    """
    names = {}
    counter = 0

    def id_of(name):
        nonlocal names, counter
        oid = names.setdefault(name, counter + 1)
        counter = max(oid, counter)
        return oid

    yield f"""
    Creator	"cab's stupid script"
    Version	"0"
    graph
    [
        hierarchic	1
        label	"{net.name}"
        directed	1
    """
    for place in net.places:
        name = place.name
        yield f"""
        node [
            id {id_of(name)}
            label "{name}"
            graphics [
                fill "#777777"
                type "circle"
            ]
        ]
        """
    for trans in net.transitions:
        name = trans.name
        if trans.label is None:
            label = trans.name
        else:
            label = trans.label
        yield f"""
        node [
            id {id_of(name)}
            label "{label}"
            graphics [
                fill "#cc8888"
                type "rectangle"
            ]
        ]
        """

    for arc in net.arcs:
        a = arc.source.name
        b = arc.target.name
        yield f"""
        edge [
            source {id_of(a)}
            target {id_of(b)}
        ]
        """
    yield "]"


if __name__ == '__main__':
    import sys, os
    from tqdm import tqdm
    from pm4py.objects.petri_net.importer import importer as petri_importer

    arr = os.listdir(os.path.dirname(__file__) + "\\tests\\evg_logs")
    arr.sort()

    ln = 0

    for file in arr:

        f_from = file
        f_to = file + '.gml'

        print(f"Reading {f_from}...")
        net, hl_i_m, hl_f_m = petri_importer.apply(os.path.join(os.path.join(os.path.dirname(__file__) + "\\tests\\evg_logs", f_from)))

        with open(f_to, mode="w") as f:
            for part in tqdm(generate_gml(net), desc="Writing GML"):
                f.write(part)

        print(f"Success! GML written to {f_to}")
    print(f"END!")