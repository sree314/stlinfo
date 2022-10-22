import numpy
import stl
from stl import mesh
from collections import namedtuple
import math

Point = namedtuple('Point', 'x y z')

class STLFile:
    def __init__(self):
        self.filename = None

    def load_file(self, filename):
        self.filename = filename
        self.mesh = mesh.Mesh.from_file(self.filename)

    def bounds(self):
        # adapted from the example
        # find the max dimensions, so we can know the bounding box, getting the height,
        # width, length (because these are the step size)...

        minx = maxx = miny = maxy = minz = maxz = None
        for p in self.mesh.points:
            # p contains (x, y, z)
            if minx is None:
                minx = p[stl.Dimension.X]
                maxx = p[stl.Dimension.X]
                miny = p[stl.Dimension.Y]
                maxy = p[stl.Dimension.Y]
                minz = p[stl.Dimension.Z]
                maxz = p[stl.Dimension.Z]
            else:
                maxx = max(p[stl.Dimension.X], maxx)
                minx = min(p[stl.Dimension.X], minx)
                maxy = max(p[stl.Dimension.Y], maxy)
                miny = min(p[stl.Dimension.Y], miny)
                maxz = max(p[stl.Dimension.Z], maxz)
                minz = min(p[stl.Dimension.Z], minz)

        return Point(minx, miny, minz), Point(maxx, maxy, maxz)

    def fits(self, bounds, szx, szy, szz):
        def rotate(pt, angle_rad):
            return Point(pt.x*math.cos(angle_rad) - pt.y*math.sin(angle_rad),
                         pt.y*math.cos(angle_rad) + pt.x*math.sin(angle_rad),
                         pt.z)

        # find the longest diagonal
        bmin = bounds[0]
        bmax = bounds[1]

        px = bmax.x - bmin.x + 1
        py = bmax.y - bmin.y + 1
        pz = bmax.z - bmax.z + 1

        # check if part fits without rotation
        if px <= szx and py <= szy and pz <= szz:
            return True

        # don't explore rotations in Z
        if pz > szz:
            return False

        # does max width fit in the diagonal?
        mw = px if px > py else py
        mw2 = mw * mw
        bed_diag = szx * szx + szy * szy
        if mw2 > bed_diag:
            return False

        # diagonal fits. so center part on bed and rotate part along diagonal
        bl = Point(-px/2, -py/2, 0)
        tl = Point(-px/2, py/2, 0)
        tr = Point(px/2, py/2, 0)
        br = Point(px/2, -py/2, 0)

        angle = 45.0 / 180.0 * math.pi;

        # TODO: explore points on a tighter bounding box, such as the convex hull?
        for pt in (bl, tr):
            newpt = rotate(pt, angle)
            if newpt.x > szx/2 or newpt.x < -szx/2: return False
            if newpt.y > szy/2 or newpt.y < -szy/2: return False

        return True
