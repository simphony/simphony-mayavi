from collections import defaultdict

from tvtk.api import tvtk

from simphony.cuds.mesh import Face, Cell, Edge


CELL2VTKCELL = {
    4: tvtk.Tetra().cell_type,
    8: tvtk.Hexahedron().cell_type,
    6: tvtk.Wedge().cell_type,
    5: tvtk.Pyramid().cell_type,
    10: tvtk.PentagonalPrism().cell_type,
    12: tvtk.HexagonalPrism().cell_type}

_polygon_type = tvtk.Polygon().cell_type
_polyline_type = tvtk.PolyLine().cell_type

FACE2VTKCELL = defaultdict(
    lambda: _polygon_type,
    {3: tvtk.Triangle().cell_type, 4: tvtk.Quad().cell_type})

EDGE2VTKCELL = defaultdict(
    lambda: _polyline_type, {2: tvtk.Line().cell_type})

VTKCELLTYPES = [
    tvtk.Tetra().cell_type,
    tvtk.Hexahedron().cell_type,
    tvtk.Wedge().cell_type,
    tvtk.Pyramid().cell_type,
    tvtk.PentagonalPrism().cell_type,
    tvtk.HexagonalPrism().cell_type]

VTKEDGETYPES = [
    tvtk.Line().cell_type,
    tvtk.PolyLine().cell_type]

VTKFACETYPES = [
    tvtk.Triangle().cell_type,
    tvtk.Quad().cell_type,
    tvtk.Polygon().cell_type]

ELEMENT2VTKCELLTYPES = {
    Edge: VTKEDGETYPES,
    Face: VTKFACETYPES,
    Cell: VTKCELLTYPES}

VTKCELLTYPE2ELEMENT = {
    cell_type: Cell for cell_type in VTKCELLTYPES}
VTKCELLTYPE2ELEMENT.update({
    cell_type: Face for cell_type in VTKFACETYPES})
VTKCELLTYPE2ELEMENT.update({
    cell_type: Edge for cell_type in VTKEDGETYPES})
