import numpy as np

EDGE_WEIGHT_TYPES = {
    "EXPLICIT",
    "EUC_2D",
    "EUC_3D",
    "MAX_2D",
    "MAN_2D",
    "GEO",
    "GEOM",
    "ATT",
    "CEIL_2D",
    "DSJRAND",
}


def write_tsp_file(fp, xs, ys, norm, name, edges_matrix=None):
    """ Write data to a TSPLIB file.
    """
    use_edge_weight_matrix = False
    if len(xs) != len(ys):
        raise ValueError(
            "x and y coordinate vector must have the "
            "same length ({} != {})".format(len(xs), len(ys))
        )
    if norm not in EDGE_WEIGHT_TYPES:
        raise ValueError(
            "Norm {!r} must be one of {}"
            .format(norm, ', '.join(EDGE_WEIGHT_TYPES))
        )

    if edges_matrix is not None:
        norm = "EXPLICIT"
        nnodes = edges_matrix.shape[0]
        assert nnodes == edges_matrix.shape[1] == len(xs), (
            "shape of edges_matrix must match the number of nodes")
        use_edge_weight_matrix = True

    fp.write("NAME: {}\n".format(name))
    fp.write("TYPE: TSP\n")
    fp.write("DIMENSION: {}\n".format(len(xs)))
    fp.write("EDGE_WEIGHT_TYPE: {}\n".format(norm))
    if use_edge_weight_matrix:
        fp.write("EDGE_WEIGHT_FORMAT: FULL_MATRIX\n")
    fp.write("NODE_COORD_SECTION\n")
    for n, (x, y) in enumerate(zip(xs, ys), start=1):
        fp.write("{} {} {}\n".format(n, x, y))
    if use_edge_weight_matrix:
        fp.write("EDGE_WEIGHT_SECTION")
        minv = edges_matrix.min()
        for n, mat_index_i in enumerate(range(n), start=1):
            for m, mat_index_j in enumerate(range(n), start=1):
                weight = int(edges_matrix[mat_index_i, mat_index_j] / minv)
                fp.write("{} {} {}\n".format(n, m, weight))
        fp.write("-1")
    fp.write("EOF\n")


def read_tsp_tour(fname):
    has_tour = False
    tour = []
    with open(fname) as fp:
        for line in fp:
            if line.startswith("TOUR_SECTION"):
                has_tour = True
            elif line.startswith("EOF"):
                break
            else:
                if has_tour:
                    tour.extend(int(node) for node in line.split())
    if not tour:
        raise RuntimeError("File {} has no valid TOUR_SECTION".format(fname))
    if tour[-1] == -1:
        tour.pop()
    return np.array(tour)
