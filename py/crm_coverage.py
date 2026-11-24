"""Which BREC classes have a CIDOC CRM family class (crm, crmdig, crminf) among their ancestors, and through which chain.

Shared by the check step, the coverage figure and the coverage and crosswalk pages. The CRM family classes themselves are not in the
ontology file (it imports CIDOC CRM), so a chain ends at the first class of the family; what lies above it is CRM's own hierarchy.
"""
from rdflib import OWL, RDF, RDFS, URIRef

BREC = "https://w3id.org/brec/ontology#"
FAMILY = ("http://www.cidoc-crm.org/cidoc-crm/", "http://www.cidoc-crm.org/extensions/crmdig/", "http://www.ics.forth.gr/isl/CRMinf/")

# Classes that intentionally have no CRM-family ancestor, with the reason. Empty since 2026-11-17: every class is anchored.
NO_ANCHOR_OK: dict = {}


def own_classes(g):
    return sorted((c for c in g.subjects(RDF.type, OWL.Class) if str(c).startswith(BREC)), key=str)


def is_family(u):
    return str(u).startswith(FAMILY)


def chains(g, cls):
    """All chains from cls up to the first CRM-family class on each path (lists of URIs, own classes in between)."""
    out = []

    def walk(c, path):
        for p in sorted(g.objects(c, RDFS.subClassOf), key=str):
            if not isinstance(p, URIRef):
                continue
            if is_family(p):
                out.append(path + [p])
            elif str(p).startswith(BREC) and p not in path:
                walk(p, path + [p])

    walk(cls, [cls])
    return out


def anchors(g, cls):
    return sorted({c[-1] for c in chains(g, cls)}, key=str)


def uncovered(g):
    return [c for c in own_classes(g) if not anchors(g, c)]
