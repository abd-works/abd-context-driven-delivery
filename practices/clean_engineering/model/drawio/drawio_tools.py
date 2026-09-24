"""
DrawIO class diagram toolkit — core XML read/write functions.

All CLI commands use these shared functions to manipulate DrawIO files.
"""
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
CELL_WIDTH = 260
CELL_MIN_HEIGHT = 80
LINE_HEIGHT = 16
SECTION_PAD = 8
CLASS_STYLE = 'verticalAlign=top;align=left;overflow=fill;fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;'
CLASS_STYLE_IMPORT = 'verticalAlign=top;align=left;overflow=fill;fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;dashed=1;dashPattern=8 4;strokeColor=#999999;fontColor=#666666;'
EDGE_ORTHOGONAL = 'edgeStyle=orthogonalEdgeStyle;rounded=1;'
EDGE_STYLES = {'inheritance': 'endArrow=block;endSize=16;endFill=0;html=1;', 'inheritance-orthogonal': f'{EDGE_ORTHOGONAL}endArrow=block;endSize=16;endFill=0;html=1;', 'composition': f'{EDGE_ORTHOGONAL}endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;', 'aggregation': f'{EDGE_ORTHOGONAL}endArrow=none;html=1;startArrow=diamondThin;startFill=0;startSize=14;', 'association': f'{EDGE_ORTHOGONAL}endArrow=open;endSize=12;html=1;', 'association-straight': 'endArrow=open;endSize=12;html=1;', 'composition-straight': 'endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;', 'aggregation-straight': 'endArrow=none;html=1;startArrow=diamondThin;startFill=0;startSize=14;', 'dependency': 'endArrow=open;endSize=12;dashed=1;html=1;', 'dependency-orthogonal': f'{EDGE_ORTHOGONAL}endArrow=open;endSize=12;dashed=1;html=1;'}
SHORT_ROUTE_MAX_WAYPOINTS = 2
SHORT_ROUTE_MAX_BOX_GAP = 320
_LEAF_ROW_Y_TOLERANCE = 30
_LEAF_ROW_MIN_SIZE = 4
if __name__ == '__main__':
    import sys
    from practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner
    scanner = DrawioScanner()
    if len(sys.argv) < 2:
        print('Commands: audit')
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd != 'audit':
        print(f'Unknown command: {cmd}')
        sys.exit(1)
    args = sys.argv[2:]
    if len(args) < 1:
        print('Usage: python drawio_tools.py audit <file> [--page <name>]')
        sys.exit(1)
    path = args[0]
    page = None
    if '--page' in args:
        idx = args.index('--page')
        if idx + 1 < len(args):
            page = args[idx + 1]
    print(scanner._audit_diagram_report(path, page))
    results = scanner._audit_diagram(path, page)
    any_fail = any((not info['pass'] for info in results.values()))
    sys.exit(1 if any_fail else 0)

