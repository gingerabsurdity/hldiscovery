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
        yield f"""
        node [
            id {id_of(name)}
            label "{name}"
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
    from pm4py.algo.discovery.inductive import algorithm as ind_discover
    from pm4py.read import read_xes
    from pm4py.objects.log.importer import xes

    f_from = sys.argv[1]
    f_to = sys.argv[2]
    
    print(f"Reading {f_from}...")
    log = read_xes(f_from)
    
    print(f"Running discovery")
    net, _, _ = ind_discover.apply(log)

    with open(f_to, mode="w") as f:
        for part in tqdm(generate_gml(net), desc="Writing GML"):
            f.write(part)
    
    print(f"Success! GML written to {f_to}")