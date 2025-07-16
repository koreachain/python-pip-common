#!/usr/bin/env python3
"""https://stackoverflow.com/a/71644530/756589 -- CC BY-SA 3.0"""


def all_paths(
    edges, *, allow_same_vertices=False, allow_same_edges=False, max_length=5
):
    neighbours = {None: []}
    for a, b in edges:
        for i in range(2):
            if a not in neighbours[None]:
                neighbours[None].append(a)
            if a not in neighbours:
                neighbours[a] = []
            if b not in neighbours[a]:
                neighbours[a].append(b)
            a, b = b, a
    visited_edges = {}
    visited_vertices = {}
    paths = set()
    path = []

    def rec(vertex):
        if len(path) >= 2:
            paths.add(tuple(path))
        if len(path) >= max_length:
            return
        for neighbour in neighbours.get(vertex, []):
            if not allow_same_vertices and visited_vertices.get(neighbour, 0) > 0:
                continue
            if not allow_same_edges and visited_edges.get((vertex, neighbour), 0) > 0:
                continue
            visited_vertices[neighbour] = visited_vertices.get(neighbour, 0) + 1
            visited_edges[(vertex, neighbour)] = (
                visited_edges.get((vertex, neighbour), 0) + 1
            )
            path.append(neighbour)
            rec(neighbour)
            path.pop()
            visited_vertices[neighbour] -= 1
            visited_edges[(vertex, neighbour)] -= 1

    rec(None)
    return sorted(paths, key=lambda e: (len(e), e))


if __name__ == "__main__":
    print("Sample paths in a directed graph:")
    elist = (
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("C", "D"),
        ("D", "B"),
        ("D", "E"),
        ("E", "F"),
    )
    for path in all_paths(elist):
        print(path)
