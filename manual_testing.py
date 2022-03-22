import os
import sys
from mathutils import Vector
from math import degrees
import bpy

# getting access to the current dir - necessary to access blender file location
blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)
# append sys path to dir
main_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'module')
sys.path.append(main_dir)

from src.cgt_blender.utils import objects
from src.cgt_utils import m_V
import numpy as np
import math

finger_names = ["CGT_WRIST",
                "CGT_THUMB_CMC",
                "CGT_THUMB_MCP",
                "CGT_THUMP_IP",
                "CGT_THUMB_TIP",
                "CGT_INDEX_FINGER_MCP",
                "CGT_INDEX_FINGER_PIP",
                "CGT_INDEX_FINGER_DIP",
                "CGT_INDEX_FINGER_TIP",
                "CGT_MIDDLE_FINGER_MCP",
                "CGT_MIDDLE_FINGER_PIP",
                "CGT_MIDDLE_FINGER_DIP",
                "CGT_MIDDLE_FINGER_TIP",
                "CGT_RING_FINGER_MCP",
                "CGT_RING_FINGER_PIP",
                "CGT_RING_FINGER_DIP",
                "CGT_RING_FINGER_TIP",
                "CGT_PINKY_MCP",
                "CGT_PINKY_PIP",
                "CGT_PINKY_DIP",
                "CGT_PINKY_TIP"]

fingers = [
    [1, 5],  # thumb
    [5, 9],  # index finger
    [9, 13],  # middle finger
    [13, 17],  # ring finger
    [17, 21],  # pinky
]
    
def m_hand():
    _fingers = get_fingers()
    _hand = get_hand(".R")
    hand = [[idx, vertex.location, vertex] for idx, vertex in enumerate(_hand)]
    return hand

def get_hand(_dir = ".L"):
    names = [name + _dir for name in finger_names]
    return [objects.get_object_by_name(name) for name in names]

def get_fingers(_dir = ".L"):
    names = []
    for finger in fingers:
        vertex_names = [finger_names[idx] + _dir for idx in range(finger[0], finger[1]-1)]
        for name in vertex_names:
            names.append(name)
    return [objects.get_object_by_name(name) for name in names]


def get_y_angles(hand):
    joints = np.array([[0, 1, 2]])
    data = [0] * 20
    plane_tris = [
        [1, 5], # thumb
        [5, 9], # index
        [9, 13], # middle
        [13, 17], # ring -> basically [13, 9]
        [17, 21] # pinky -> [17, 13]
    ]
    
    # palm based plane
    plane = np.array([
        np.array([0, 0, 0]),
        hand[5][1],
        hand[17][1]
    ])
    
    # project proximal phalanges on plane based on surrounding metacarpals
    for idx, finger in enumerate(fingers):  
        if idx == 0:
            # thumb based plane
            plane = np.array([
                np.array([0, 0, 0]),
                hand[1][1],
                hand[5][1]
            ])
            
        ### PROJ MCP ###
        proj_mcp = m_V.project_vec_on_plane(plane, joints, hand[finger[0]][1])
        hand[finger[0]][2].location = proj_mcp
        
        ### PROJ PIP ON PLANE###
        pip = hand[finger[0]+1]
        proj_pip = m_V.project_vec_on_plane(plane,joints,np.array(pip[1]))
        pip[2].location = proj_pip
        proj_pip = np.array(pip[1])
        # vector to chain mcps
        if idx < 3:
            proj_mcp_b = m_V.project_vec_on_plane(plane, joints, hand[finger[1]][1])
            mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)
            mcp_vector = m_V.to_vector(hand[finger[1]][1], hand[finger[0]][1])
            
        else:
            # changing vector direction?
            proj_mcp_b = m_V.project_vec_on_plane(plane, joints, hand[fingers[idx-1][0]][1])
            mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)
            mcp_vector = m_V.to_vector(hand[fingers[idx-1][0]][1], hand[fingers[idx-1][1]][1])
            
        # mcp to pip vec
        tar_vec = m_V.to_vector(np.array(proj_mcp), np.array(proj_pip))
        angle = m_V.angle_between(np.array(tar_vec), np.array(mcp_vector))
        t = m_V.angle_between(proj_mcp, proj_mcp_b)
        #angle = angle/fac
        #angle = m_V.angle_between(np.array(proj_mcp), np.array(proj_pip))
        if angle is None:
            break

        data[finger[0]] = (degrees(angle))
    
    angles = [int(d) for d in data if d != 0]
    print(angles)
    # return data


def get_distances(hand):
    distances = []
    joints = np.array([[0, 1, 2]])
    
    plane = np.array([
        np.array([0, 0, 0]),
        hand[5][1],
        hand[17][1]
    ])
    
    for idx in range(0,4):
        if idx == 0:
            # thumb based plane
            plane = np.array([
                np.array([0, 0, 0]),
                hand[1][1],
                hand[5][1]
            ])
        
        
        # TRUE
        p_a = hand[fingers[idx][0]+1][1]
        p_b = hand[fingers[idx+1][0]+1][1]
        pip_test = m_V.get_vector_distance(np.array(p_a), np.array(p_b))
        
        m_a = hand[fingers[idx][0]][1]
        m_b = hand[fingers[idx+1][0]][1]
        mcp_test = m_V.get_vector_distance(np.array(m_a), np.array(m_b))
        
        
        # PLANE
        mcp_a = m_V.project_vec_on_plane(plane, joints, m_a)
        mcp_b = m_V.project_vec_on_plane(plane, joints, m_b)
        mcp_dist_p = m_V.get_vector_distance(mcp_a, mcp_b)
        
        pip_a = m_V.project_vec_on_plane(plane, joints, p_a)
        pip_b = m_V.project_vec_on_plane(plane, joints, p_b)
        pip_dist_p = m_V.get_vector_distance(pip_a, pip_b)
        
        
        # VECTOR
        mcp_a = m_V.project_point_on_vector(np.array(m_a), np.array(hand[5][1]), np.array(hand[17][1]))
        mcp_b = m_V.project_point_on_vector(np.array(m_b), np.array(hand[5][1]), np.array(hand[17][1]))
        mcp_dist_v = m_V.get_vector_distance(mcp_a, mcp_b)
        
        pip_a = m_V.project_point_on_vector(np.array(p_a), np.array(hand[6][1]), np.array(hand[18][1]))
        pip_b = m_V.project_point_on_vector(np.array(p_b), np.array(hand[6][1]), np.array(hand[18][1]))
        pip_dist_v = m_V.get_vector_distance(pip_a, pip_b)
        #distances.append([pip_test, mcp_test])
        distances.append([int((pip_dist_v/mcp_dist_v)*1000), int((pip_test/mcp_test)*1000), int((pip_dist_p/mcp_dist_p)*1000)])
        
    print(distances)


def get_thumb_angle(hand):
    pass


def project_mcps_on_vec(hand):
    # project mcps to vector from index to pinky mcp
    mcps = []
    for idx, finger in enumerate(fingers[1:]):  
        mcp = hand[finger[0]][1]
        proj_mcp = m_V.project_point_on_vector(
            np.array(mcp), np.array(hand[5][1]), np.array(hand[17][1])
        )
        
        hand[finger[0]][2].location = proj_mcp
        mcps.append(proj_mcp)
    
    return mcps


def get_mcp_pip_dist(hand, mcps):
    dists = []
    for idx, finger in enumerate(fingers[1:]):
        mcp = mcps[idx]
        pip = np.array(hand[finger[0]+1][1])
        dist = m_V.get_vector_distance(mcp, pip)
        dists.append(dist)
    return dists

def mcp_vectors(hand):
    tangent = m_V.to_vector(
        np.array(hand[5][1]), np.array(hand[17][1]))
    t_center = m_V.center_point(hand[5][1], hand[17][1])
    normal = m_V.to_vector(t_center, np.array([0, 0, 0]))
    return normal, tangent
    
def main():
    hand = m_hand()
    # frames to target:
    print("\n\nREMEASURING")
    measure_container = [
        ["\nfront open", [0, 40, 80]],
        ["front straight", [120, 150, 180]],
        ["front closed", [190, 210, 240]],
        
        ["\nback open", [420, 440, 460]],
        ["back straight", [490, 510, 530]],
        ["back closed", [300, 350, 390]] 
    ]

    for container in measure_container:
        print(container[0])
        for frame in container[1]:
            bpy.context.scene.frame_set(frame)
            get_distances(hand)
            #get_y_angles(hand)


def circular_rotation():
    U = np.array([1, 0, 0])
    # vA = vUsin(2pi/t)+vVcos(2pi/t)
    V = np.array([0, 1, 1])
    r = np.sin(U*np.pi/180) + np.cos(V*np.pi/180)
    print(f"{U} -> {r}")

    

def create_angled_circle(angle=90, points=10, axis="x"):
    rot = angle
    thetha = np.linspace(0, 2*np.pi, points)
    r = .025
    
    y = np.cos(thetha)
    z = np.sin(thetha)
        
    # set angle
    phi = np.deg2rad(rot)
        
    # apply angle
    x = y*np.cos(phi) * r
    y = y*np.sin(phi) * r
    z = z*r
        
    circle = [[x[i], y[i], z[i]] for i in range(0, len(x))]
        
    for i, point in enumerate(circle):
        # print(i, point)
        ob = objects.add_empty(0.001, f"test{i}")
        res = point+origin
        ob.location = res


def circle_on_normal():
    #P = Center + Radius*cos(Angle), U + Radius*sin(Angle), V 
    
    points=10
    thetha = np.linspace(0, 2*np.pi, points)
    r = .025
    rot=0
    
    origin = np.array([0, 0, 0])
    tangent = np.array([1, 0, 0])
    
    normal = np.array([0, 0, 1])
    
    cross = np.cross(tangent, normal)
    print(cross)
    
    y = np.cos(thetha)
    z = np.sin(thetha)
        
    # set angle
    phi = np.deg2rad(rot)
        
    # apply angle
    x = y*np.cos(phi) * r
    y = y*np.sin(phi) * r
    z = z*r
        
    circle = [[x[i], y[i], z[i]] for i in range(0, len(x))]
        
    for i, point in enumerate(circle):
        # print(i, point)
        ob = objects.add_empty(0.001, f"test{i}")
        res = point+origin
        ob.location = res
    


def circle():
    create_circle()
    return
    
    r=.01
    thetha = np.linspace(0, 2*np.pi, 10)
    origin=np.array([.01, 0, 0])
    
    
    for i, t in enumerate(thetha):
        y = np.cos(t) *r
        z = np.sin(t) * r
        ob = objects.add_empty(0.001, f"test{i}")
        ob.location = [0, y, z]
     
        

def orbit_towards(hand):
    normal, tangent = mcp_vectors(hand)
    perpendicular = np.cross(normal, tangent)
    mcps = project_mcps_on_vec(hand)
    dists = get_mcp_pip_dist(hand, mcps)





if __name__ == "__main__":
    #main()
    #orbit_towards(m_hand())
    circle_on_normal()
    #get_y_angles(m_hand())
