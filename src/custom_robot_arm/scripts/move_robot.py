#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

def move_robot():
    # Initialize the ROS node
    rospy.init_node('move_robot', anonymous=True)
    
    # Create a publisher for joint states
    joint_pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
    
    # Create a JointState message
    joint_state = JointState()
    joint_state.header = Header()
    joint_state.name = ['joint1', 'joint2', 'joint3']
    
    rate = rospy.Rate(10)  # 10 Hz
    while not rospy.is_shutdown():
        joint_state.header.stamp = rospy.Time.now()
        
        # Update joint positions (you can customize these values)
        # Position one
        # joint_state.position = [0.5, 1.0, 0.75]  
        # Position two
        # joint_state.position = [0.8, 0.3, 1.0]  # Joint 1 at 0.8, Joint 2 at 0.3, Joint 3 at 1.0
        # Position three
        
        joint_state.position = [0.2, 1.2, 0.5]  # Joint 1 at 0.2, Joint 2 at 1.2, Joint 3 at 0.5

        # Publish the joint states
        joint_pub.publish(joint_state)
        
        rate.sleep()

if __name__ == '__main__':
    try:
        move_robot()
    except rospy.ROSInterruptException:
        pass
