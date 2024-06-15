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
        # find the max dimensions, so we can know the bounding box, getting the height,
        # width, length (because these are the step size)...
        return Point(self.mesh.min_[0], self.mesh.min_[1], self.mesh.min_[2]), \
            Point(self.mesh.max_[0], self.mesh.max_[1], self.mesh.max_[2])

    def fits(self, bounds, szx, szy, szz, rot=True):
        # rot is a boolean indicating whether the fits check is 
        # for the original model (False) or its rotated version (True).
        def rotate(pt, angle_rad):
            return Point(pt.x*math.cos(angle_rad) - pt.y*math.sin(angle_rad),
                         pt.y*math.cos(angle_rad) + pt.x*math.sin(angle_rad),
                         pt.z)

        # find the longest diagonal
        bmin = bounds[0]
        bmax = bounds[1]

        px = bmax.x - bmin.x + 1
        py = bmax.y - bmin.y + 1
        pz = bmax.z - bmin.z + 1

        # check if part fits without rotation
        if px <= szx and py <= szy and pz <= szz:
            return True
        
        # stop here if it doesn't allow rotation
        if not rot:
            return False

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
