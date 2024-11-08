#!/usr/bin/env python3

# Students: [Hambal Tella] 
# Lab 4: Pick and Place
# Date: [November 8th 2024]
# Acknowledgements: [https://moveit.github.io/ and ChatGPT]

import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import tf.transformations
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import sys

def open_gripper():
    posture = JointTrajectory()
    posture.joint_names = ["panda_finger_joint1", "panda_finger_joint2"]
    posture.points.append(JointTrajectoryPoint(positions=[0.04, 0.04], time_from_start=rospy.Duration(0.5)))
    return posture

def closed_gripper():
    posture = JointTrajectory()
    posture.joint_names = ["panda_finger_joint1", "panda_finger_joint2"]
    posture.points.append(JointTrajectoryPoint(positions=[0.00, 0.00], time_from_start=rospy.Duration(0.5)))
    return posture

def pick(move_group, object_name):
    grasps = []
    
    grasp = moveit_msgs.msg.Grasp()
    grasp.grasp_pose.header.frame_id = "panda_link0"
    orientation = tf.transformations.quaternion_from_euler(-1.57, -0.785, -1.57)
    grasp.grasp_pose.pose.orientation = geometry_msgs.msg.Quaternion(*orientation)
    grasp.grasp_pose.pose.position.x = 0.5
    grasp.grasp_pose.pose.position.y = 0
    grasp.grasp_pose.pose.position.z = 0.5

    grasp.pre_grasp_approach.direction.header.frame_id = "panda_link0"
    grasp.pre_grasp_approach.direction.vector.x = 1.0
    grasp.pre_grasp_approach.min_distance = 0.095
    grasp.pre_grasp_approach.desired_distance = 0.115

    grasp.post_grasp_retreat.direction.header.frame_id = "panda_link0"
    grasp.post_grasp_retreat.direction.vector.z = 1.0
    grasp.post_grasp_retreat.min_distance = 0.1
    grasp.post_grasp_retreat.desired_distance = 0.25

    grasp.pre_grasp_posture = open_gripper()
    grasp.grasp_posture = closed_gripper()

    grasps.append(grasp)

    move_group.set_support_surface_name("table1")
    move_group.pick(object_name, grasps)

def place(move_group, object_name):
    place_locations = []

    place_location = moveit_msgs.msg.PlaceLocation()
    place_location.place_pose.header.frame_id = "panda_link0"
    orientation = tf.transformations.quaternion_from_euler(0, 0, 1.57)
    place_location.place_pose.pose.orientation = geometry_msgs.msg.Quaternion(*orientation)
    place_location.place_pose.pose.position.x = 0
    place_location.place_pose.pose.position.y = 0.5
    place_location.place_pose.pose.position.z = 0.5

    place_location.pre_place_approach.direction.header.frame_id = "panda_link0"
    place_location.pre_place_approach.direction.vector.z = -1.0
    place_location.pre_place_approach.min_distance = 0.095
    place_location.pre_place_approach.desired_distance = 0.115

    place_location.post_place_retreat.direction.header.frame_id = "panda_link0"
    place_location.post_place_retreat.direction.vector.y = -1.0
    place_location.post_place_retreat.min_distance = 0.1
    place_location.post_place_retreat.desired_distance = 0.25

    place_location.post_place_posture = open_gripper()

    place_locations.append(place_location)

    move_group.set_support_surface_name("table2")
    move_group.place(object_name, place_locations)

def add_collision_object(planning_scene_interface):
    # Add Table 1 as a collision object with larger size
    table1_pose = geometry_msgs.msg.PoseStamped()
    table1_pose.header.frame_id = "panda_link0"
    table1_pose.pose.position.x = 0.7
    table1_pose.pose.position.y = 0
    table1_pose.pose.position.z = 0.2  # Height from the ground
    table1_height = 0.2  # Table 1 height
    planning_scene_interface.add_box("table1", table1_pose, size=(0.65, 0.7, table1_height))

    # Add Table 2 as a collision object with larger size
    table2_pose = geometry_msgs.msg.PoseStamped()
    table2_pose.header.frame_id = "panda_link0"
    table2_pose.pose.position.x = 0
    table2_pose.pose.position.y = 0.7
    table2_pose.pose.position.z = 0.2  # Height from the ground
    table2_height = 0.45  # Table 2 height
    planning_scene_interface.add_box("table2", table2_pose, size=(0.7, 0.6, table2_height))

    # Define positions and sizes for six objects to align with the top of Table 1
    z_position = table1_pose.pose.position.z + table1_height / 2 + 0.08  # Align bottom of each object with table surface
    object_positions_sizes = [
        (0.75, 0, z_position, (0.02, 0.02, 0.2)),
        (0.75, 0.1, z_position, (0.04, 0.04, 0.2)),
        (0.85, -0.1, z_position, (0.05, 0.05, 0.2)),
        (0.95, -0.2, z_position, (0.03, 0.05, 0.2)),
        (0.95, -0.3, z_position, (0.04, 0.03, 0.2)),
        (0.95, 0.2, z_position, (0.05, 0.04, 0.2))
    ]

    # Add each object as a collision object
    for i, (x, y, z, size) in enumerate(object_positions_sizes):
        object_pose = geometry_msgs.msg.PoseStamped()
        object_pose.header.frame_id = "panda_link0"
        object_pose.pose.position.x = x
        object_pose.pose.position.y = y
        object_pose.pose.position.z = z  # Set bottom to table's top height

        # Add object to the planning scene
        object_name = f"object_{i+1}"
        planning_scene_interface.add_box(object_name, object_pose, size=size)

        # Wait for each object to be added to the planning scene
        rospy.sleep(0.5)

    # Ensure objects are fully added
    rospy.sleep(2)

def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('panda_arm_pick_place', anonymous=True)
    
    planning_scene_interface = moveit_commander.PlanningSceneInterface()
    move_group = moveit_commander.MoveGroupCommander("panda_arm")
    move_group.set_planning_time(45.0)
    move_group.set_num_planning_attempts(10)

    add_collision_object(planning_scene_interface)
    rospy.sleep(2)

    # Keep changing the object_1, object_2 ... object_6 to pick
    pick(move_group, "object_6") 
    rospy.sleep(1)
    place(move_group, "object_6")
    rospy.sleep(1)

    moveit_commander.roscpp_shutdown()

if __name__ == '__main__':
    main()
