import numpy as np
import math
from mathutils import Vector, Euler, Matrix

from utils import log, m_V
import bpy

euler_combat = None

def main(frame):
    global euler_combat
    """TODO: calc binormal from scrath. dot is false in this case"""
    forward = center_point(face("1"), face("4"))
    # custom points for mapping
    right = center_point(face("447"), face("366"))
    left = center_point(face("137"), face("227"))
    origin = center_point(right, left)
    print(origin)
    
    """ returns rotation matrix 
    -> origin = imaginary face
    -> tangent = towards left and right [+X]
    -> normal = origin towards front [+Y]
    -> binormal = cross product of tanget and normal [+Z] """
    # get vectors for angle math
    normal = normalize_vector(vector_from_points(origin, forward))
    tanget = normalize_vector(vector_from_points(left, right))
    binormal = normalize_vector(np.cross(normal, tanget))
    chin = normalize_vector(
        vector_from_points(
            origin, 
            np.array(face("152"))
        )
    )
    """ calculate binormal as normal from triangle.
    triangle = p1p2p3 """

    p1 = face("10")
    p2 = face("337")
    p3 = face("108")
    # vertex from points
    vertices = np.array([p1, p2, p3])
    faces = np.array([0, 1, 2])
    # tanget from array.. need any col point??
    bitanget, norm = create_normal_array(vertices, faces)
    bitanget = normalize_vector(bitanget)
    print("N:",bitanget, norm)
    # generate matrix from tanget, normal and binormal
    res_M = Matrix((
        [tanget[0], tanget[1], tanget[2], 0],
        [normal[0], normal[1], normal[2], 0],
        [chin[0], chin[1], chin[2], 0],
        #[binormal[0], binormal[1], binormal[2], 0],
        
       
        
        [0, 0, 0, 1],
    ))
    
    # decompose matrix
    loc, quart, sca = res_M.decompose()
    quart.invert()
    
    # convert to euler
    print("ne euler ok", euler_combat)
    if euler_combat is None:
        euler_combat = m_V.to_euler('XYZ')
    
    euler = m_V.to_euler('XYZ', euler_combat)
    print("\neu:", euler, "com", euler_combat)
    euler_combat = euler
    
    
    # keyframe suzanne
    suz = bpy.data.objects["Suzanne"]
    suz.location = origin
    suz.keyframe_insert(data_path="location", frame=frame)
    
    
        
    suz.rotation_euler = euler
    #suz.rotation_quaternion = rot
    suz.keyframe_insert(data_path="rotation_euler", frame=frame)
    return
    px,py=vector_intersection_point(right, front)
    
    
    
    """ ##1## get intersection point from top to front at 90° angle (right triangle)"""
    # return has to be vector angle + front vector
    """ ##2## the front vector should be changed, now get from front to right the res at 90° angle"""
    # return has to be points of origin
    
    ### requires result vector from front 
    vert = vector_from_points(get_ob_by_name("175"), get_ob_by_name("151"))
    backwards = np.array([front[0]-1, front[1], front[2]])
    horz = vector_from_points(front, backwards) ### -> horz vector needs to point to origin
    angle = angle_between(vert, horz) 
    print(math.degrees(angle))
    
    """1. nose face center"""
    nose_cube_for_normal_vector()
    
def create_normal_array(vertices, faces):
    """return array of normals per triangle"""
    norm = np.zeros( vertices.shape, dtype=vertices.dtype ) 
    # indexed view into the vertex array 
    # using the array of three indices for triangles 
    tris = vertices[faces] 
    # Calculate the normal for all the triangles, 
    # by taking the cross product of the vectors v1-v0, and v2-v0 in each triangle              
    normals = np.cross(tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0])
    return normals, norm


def vector_intersection_point(right, front):
    # dir =! parallel => intersection = origin of canonial face mesh
    print("\n", "right", right, "front", front)
    
    # intersection of 2d points
    p1 = np.array( [right[0], right[1]] )
    p2 = np.array( [right[0]-1, right[1]] )
    p3 = np.array( [front[0], front[1]] )
    p4 = np.array( [front[0], front[1]-1] )
    pxpy = seg_intersect(p1, p2, p3, p4)
    print(pxpy)
    return pxpy
    
def get_ob_by_name(name):
    return bpy.data.objects[name].location

def face(name):
    return Vector((bpy.data.objects["face_empty_"+str(name)].location))


def perp(a):
    # rotating by 180
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# https://web.archive.org/web/20111108065352/https://www.cs.mun.ca/%7Erod/2500/notes/numpy-arrays/numpy-arrays.html
def seg_intersect(a1,a2, b1,b2) :
    dist_a = a2-a1
    dist_b = b2-b1
    dist_p = a1-b1
    dist_ap = perp(dist_a)
    denom = np.dot(dist_ap, dist_b)
    num = np.dot(dist_ap, dist_p)
    return (num / denom.astype(float))*dist_b + b1

"""
# todo: requires funcs
def normal_angle(up, normal):
    Axis = normalize_vector(cross(up, normal))
    Angle = acos(dot(up, normal))
    return Angle
"""

# region quaternion
def rot_angle_to_quaternion(theta, vector):
    """ converts angle theta in radians to quaternion (w, x, y, z) """
    w = np.cos(theta / 2)
    xyz = np.sin(theta / 2) * vector
    return np.hstack((w, xyz))


def angle_between(vec_a, vec_b):
    """ Returns the angle in radians between vectors. """
    v1, v2 = normalize_vector(vec_a), normalize_vector(vec_b)
    dot = np.dot(v1, v2)
    limited_dot = np.clip(dot, -1.0, 1.0)
    return np.arccos(limited_dot)


def quaternion_from_point(point, target):
    """ Returns quaternion rotation from point towards target. """
    point = normalize_vector(point)
    axis_vector = normalize_vector(np.cross(point, target))
    angle = -angle_between(point, target)
    return rot_angle_to_quaternion(angle, axis_vector)




# region location
def center_point(p_a, p_b):
    """ return center point from two given points. """
    return (p_a + p_b) / 2


def vector_from_points(origin, dest):
    """ returns vector from two given points. """
    return dest-origin
# endregion


# region utils
def normalize_vector(vec):
    """ Returns the unit vector of the vector. """
    return vec / np.linalg.norm(vec)


def old_normalize_vector(vec):
    """ returns a normalized vector. 50% slower than above. """
    magnitude = vector_length(vec)
    return vec/magnitude


def vector_length(vec):
    """ returns the length of a given vector. """
    vec = np.sum(vec**2)
    return np.sqrt(vec)


def ignore_axis(vec, *args):
    """ null axis ['X', 'Y', 'Z'] of a given vector. """
    ignore = {
        'X': 0,
        'Y': 1,
        'Z': 2,
    }

    for arg in args:
        try:
            vec[ignore[arg]] = 0
        except KeyError:
            log.logger.error(arg, "AXIS NOT AVAILABLE")
    return vec


def target_vector(*args):
    """ Returns a vector for targeting ['X', 'Y', 'Z', '-X', '-Y', '-Z'] axis.
    Vector can target multiple axis. """
    target = {
        'X': [1, 0, 0],
        'Y': [0, 1, 0],
        'Z': [0, 0, 1],
        '-X': [-1, 0, 0],
        '-Y': [0, -1, 0],
        '-Z': [0, 0, -1],
    }

    vector = np.array([0, 0, 0])
    for arg in args:
        try:
            vector += np.array(target[arg])
        except KeyError:
            print("err")
            log.logger.error(arg, "AXIS NOT AVAILABLE")

    return vector
# endregion


if __name__ == '__main__':
    for i in range(150):
        scene = bpy.context.scene
        frame = scene.frame_current
        scene.frame_set(frame+1)
        main(frame)
        






def rotate_along_axis(verts, axis, main_point_idx, target):
    verts = np.delete(verts, axis, axis=1)

    # caluclate radius of each vert
    verts_squared = verts ** 2
    radius = np.sqrt(np.sum(verts_squared, axis=1))

    # define main point
    mp_radius = radius[main_point_idx]
    mp = verts[main_point_idx]

    # get angles relative to main point
    dot = np.dot(verts, mp)
    mag = radius * mp_radius
    angle = np.arccos(dot / mag)

    # get angles relative to target.
    dot = np.dot(verts, target)
    mag = radius * target[0]
    angles = np.arccos(dot / mag)

    # finding out if points are left or right of main point
    slope = mp[1] / mp[0]
    if mp[0] > 0:
        side = np.argwhere(verts[:, 1] >= verts[:, 0] * slope)
    else:
        side = np.argwhere(verts[:, 1] <= verts[:, 0] * slope)

    # adjusting angle offset
    for i in side:
        angle[i] = np.negative(angle[i])
    offset = np.radians(90)
    angle += offset
    angle[main_point_idx] = np.radians(90)

    # creating x,y vaules
    y = radius * np.cos(angle)
    x = radius * np.sin(angle)
    verts = np.stack((x, y), axis=1)

    # return verts and amount the object was rotated
    return verts, angles[main_point_idx]
# endregion



def quat_rot_nose():
    frame = bpy.data.scenes['Scene'].frame_current + 1
    bpy.data.scenes['Scene'].frame_set(frame)

    
    """tracking point 6 and 133"""
    verts = np.array([face(175) ,face(378)])
    target = np.array([1,0])    # """<<<< [1,0] ??"""

    # facing z
    verts_transformed, rotation_z = rotate_along_axis(verts, 2, 0, target)
    verts[:, 0] = verts_transformed[:, 0]
    verts[:, 1] = verts_transformed[:, 1]

    # facing y
    verts_transformed, rotation_y = rotate_along_axis(verts, 1, 0, target)
    verts[:, 0] = verts_transformed[:, 0]
    verts[:, 2] = verts_transformed[:, 1]

    # facing x
    verts_transformed, rotation_x = rotate_along_axis(verts, 0, 1, target)
    verts[:, 1] = verts_transformed[:, 0]
    verts[:, 2] = verts_transformed[:, 1]

    rot_left = np.array([rotation_x, rotation_y, rotation_z])
    """to avarage the rotation track 6 and 362"""
    # again to average
    verts = np.array([face(175) ,face(401)])
    target = np.array([1,0])

    # facing z
    verts_transformed, rotation_z = rotate_along_axis(verts, 2, 0, target)
    verts[:, 0] = verts_transformed[:, 0]
    verts[:, 1] = verts_transformed[:, 1]

    # facing y
    verts_transformed, rotation_y = rotate_along_axis(verts, 1, 0, target)
    verts[:, 0] = verts_transformed[:, 0]
    verts[:, 2] = verts_transformed[:, 1]

    # facing x
    verts_transformed, rotation_x = rotate_along_axis(verts, 0, 1, target)
    verts[:, 1] = verts_transformed[:, 0]
    verts[:, 2] = verts_transformed[:, 1]
    
    """combines the two rotations"""
    rot_right = np.array([rotation_x, rotation_y, rotation_z])
    rot = (rot_right + rot_left)/2
    
    """append the average rotation"""
    print([rot[0], rot[1], rot[2]])
    
    euler=Euler((
        rot[0], 
        -rot[1], 
        rot[2]), 
        'XYZ')
    ob = bpy.data.objects["Cube"]
    ob.rotation_euler=euler  
    ob.keyframe_insert(data_path="rotation_euler", frame=frame)
