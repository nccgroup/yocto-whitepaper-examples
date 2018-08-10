#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT
# Author: Jon Szymaniak <jon.szymaniak.foss@gmail.com>

"""
Extract a subset of a dependency graph from a Yocto build history dot file.
"""

import argparse
import re
import sys

# Prepare command-line arguments
def handle_cmdline():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--infile',   metavar='filename', required=True,
        help='Input DOT file from buildhistory')
    parser.add_argument('-o', '--outfile',  metavar='filename', required=True,
        help='Output DOT file containing graph subset')
    parser.add_argument('-p', '--pkg',      metavar='package',  required=True,
        help='Target package name')
    parser.add_argument('-H', '--height',   metavar='height',   type=int, default='3',
        help='# of dependency levels from the target package upward to include. Default: 3')
    parser.add_argument('-D', '--depth',    metavar='depth',    type=int, default='0',
        help='# of dependency levels from the target package downward to include. Default: 0')
    return parser.parse_args()

# Update a package dependency graph to include the specified "depends_on" and
# "required_by" relationships
def update_graph(graph, pkg, dep, attr):
    pkg_node = graph.get(pkg, { 'depends_on': [], 'required_by': [] })
    pkg_node['depends_on'].append((dep, attr))
    graph[pkg] = pkg_node

    dep_node = graph.get(dep, { 'depends_on': [], 'required_by': [] })
    dep_node['required_by'].append((pkg, None))
    graph[dep] = dep_node

# Load and parse a Yocto buildhistory dot file and construct the included
# package dependency graph
def load_file(filename):
    pkg = '[a-zA-Z0-9\-\./]+'           # Match package name and version
    attr = '(\s*(?P<attr>\[.*\]))?'     # Match graphviz edge attributes
    pat = '^"(?P<pkg>' + pkg + ')"\s*->\s*"(?P<dep>' + pkg + ')"' + attr + '$'
    regexp = re.compile(pat)

    graph = {}
    with open(filename, 'r') as infile:
        for line in infile:
            m = regexp.match(line)
            if m:
                update_graph(graph, m.group('pkg'), m.group('dep'), m.group('attr'))

    return graph

# Traverse a dependency graph, up to the specified depth, and collect a set of
# all encountered packages in the `collected` parameter
def collect_packages(g, packages, depth, relationship, collected):
    if depth < 0:
        return []

    to_visit = []
    for p in packages:
        collected.add(p)
        to_visit += [node[0] for node in g[p][relationship]]

    collect_packages(g, to_visit, depth-1, relationship, collected)

# Return string data in DOT syntax that represents a target package's
# dependency relationships for the specified number of levels.
def dot_data(graph, target, levels, relationship, color):
    ret = ''
    packages = set()
    collect_packages(graph, [target], levels, relationship, packages)
    for pkg in packages:
        if pkg != target:
            ret += '  "{:s}" [color={:s}, style=filled]\n'.format(pkg, color)
        for info in [dep for dep in graph[pkg]['depends_on'] if dep[0] in packages]:
            ret += '  "{:s}" -> "{:s}" {:s}\n'.format(pkg, info[0], info[1] or '')
    return ret

if __name__ == '__main__':
    args = handle_cmdline()
    graph = load_file(args.infile)

    data  = 'digraph G {\n'
    data += '  node [shape=box]\n'
    data += '  edge [fontsize=9]\n'
    data += '  "{:s}" [color=seagreen1, style=filled]\n'.format(args.pkg)
    try:
        data += dot_data(graph, args.pkg, args.height, 'required_by', 'lightblue')
        data += dot_data(graph, args.pkg, args.depth, 'depends_on', 'lightgray')

        data += '}\n'
        with open(args.outfile, 'w') as outfile:
            outfile.write(data)

    except KeyError:
        print('No such package in graph: ' + args.pkg, file=sys.stderr)
