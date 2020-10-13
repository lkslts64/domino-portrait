# Takes an domino description file and produces a domino image, or
# outputs the domino sets.


import matplotlib
import matplotlib.pyplot as plt

from matplotlib import collections as mc
from matplotlib.patches import Rectangle
from matplotlib.patches import Circle
import re
import argparse

def create_tile(xy, width, height, tile):
    x, y = xy
    n, m = tile
    rectangles = []
    circles = []
    side = min(width, height)
    horz = True if width > height else False
    offset = 0.25 * side
    radius = 0.05 * side
    rectangles.append(Rectangle((x, y), width, -height))
    for p in (n, m):
        if p % 2 == 1:
            circles.append(Circle((x+side/2, y-side/2), radius=radius))
        if p > 1:
            if horz:
                circles.append(Circle((x+offset, y-offset), radius=radius))
                circles.append(Circle((x+side-offset, y-side+offset), 
                    radius=radius))
            else:
                circles.append(Circle((x+side-offset, y-offset), radius=radius))
                circles.append(Circle((x+offset, y-side+offset),
                                      radius=radius))
        if p > 3:
            if horz:
                circles.append(Circle((x+side-offset, y-offset), radius=radius))
                circles.append(Circle((x+offset, y-side+offset), radius=radius))
            else:
                circles.append(
                    Circle((x+offset, y-offset), radius=radius))
                circles.append(
                    Circle((x+side-offset, y-side+offset), radius=radius))
        if p > 5:
            circles.append(Circle((x+side/2, y-offset), radius=radius))
            circles.append(Circle((x+side/2, y-side+offset), radius=radius))
        if p > 7:
            circles.append(Circle((x+offset, y-side/2), radius=radius))
            circles.append(Circle((x+side-offset, y-side/2), radius=radius))
        if width > height:
            x += side
        else:
            y -= side 
    return rectangles, circles

def demo_dominoes(horz, output_file):

    fig, ax = plt.subplots()
    margin = 0.2
    if horz:
        width, height = 2, 1
        y_top = (10 + 2) * height
        ax.set_xlim(-2 * margin, 10 * (width + 2 * margin))
        ax.set_ylim(-margin, 10 * (height + margin) + 2 * margin)
    else:
        width, height = 1, 2
        y_top = (10 + 1) * height
        ax.set_xlim(-2 * margin, 10 * (width + 2 * margin))
        ax.set_ylim(-margin, 10 * (height + margin) + 2 * margin)
    side = min(width, height)
    for i in range(0, 10):
        if horz:
            x = i * (width + 2 * margin)
            y = y_top - i * (height + margin)
        else:
            x = i * (width + 2 * margin)
            y = y_top - i * (height + margin)
        for j in range(i, 10):
            rectangles, circles = create_tile((x, y), width, height, (i, j))
            cc = mc.PatchCollection(circles, 
                facecolors=('white',), edgecolors='white')
            rc = mc.PatchCollection(rectangles, 
                facecolors='black', edgecolors='gray')
            ax.add_collection(rc)
            ax.add_collection(cc)
            y -= (height + margin)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.savefig(output_file, bbox_inches='tight', pad_inches=0)
    plt.show()


def draw_portrait(input_file, output_file):

    fig, ax = plt.subplots()

    line_expr = re.compile(r"""
        ^\(\((?P<r1>\d+),\s(?P<c1>\d+)\) # start of slot (r1, c1)
        ,\s 
        \((?P<r2>\d+),\s(?P<c2>\d+)\)\) # end of slot (r2, c2)
        \s:\s
        \((?P<n>\d),\s(?P<m>\d)\).*$ # tile (n, m)
        """, re.VERBOSE)
    for line in input_file:
        line_match = line_expr.match(line)
        if not line_match:
            continue
        r1 = int(line_match.group('r1'))
        c1 = int(line_match.group('c1'))
        r2 = int(line_match.group('r2'))
        c2 = int(line_match.group('c2'))
        n = int(line_match.group('n'))
        m = int(line_match.group('m'))
        if r1 == r2:
            width = 2
            height = 1
        else:
            width = 1
            height = 2
        if r2 < r1:
            y = 30 - r2
            n, m = m, n
        else:
            y = 30 - r1
        if c2 < c1:
            x = c2
            n, m = m, n
        else:
            x = c1
        rectangles, circles = create_tile((x, y), width, height, (n, m))
        cc = mc.PatchCollection(circles,
                                facecolors='white', 
                                edgecolors='white')
        rc = mc.PatchCollection(rectangles,
                                facecolors='black',
                                edgecolors='gray')
        ax.add_collection(rc)
        ax.add_collection(cc)
    
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 30)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.savefig(output_file, bbox_inches='tight', pad_inches=0)
    plt.show()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-z", "--horz_test",
                       action="store_true",
                       help="output domino set horizontally")
    group.add_argument("-v", "--vert_test",
                       action="store_true",
                       help="output domino set vertically")
    parser.add_argument("input_file", nargs="?",
                        type=argparse.FileType('r'),                        
                        help="input file (domino description)")
    parser.add_argument("output_file",
                        help="output file drawing")
    args = parser.parse_args()

    if args.horz_test:
        demo_dominoes(horz=True, output_file=args.output_file)
    elif args.vert_test:
        demo_dominoes(horz=False, output_file=args.output_file)
    else:
        draw_portrait(args.input_file, args.output_file)
