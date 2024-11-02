#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32, String
import math

def callback(data_float, data_string):
    if data_string.data == "active":
        log_value = math.log(data_float.data)
        rospy.loginfo(f"log of {data_float.data}: {log_value}")

def subscriber_node():
    rospy.init_node('log_subscriber', anonymous=True)
    rospy.Subscriber('random_float', Float32, lambda msg: callback(msg, rospy.wait_for_message('status', String)))

    rospy.spin()

if __name__ == '__main__':
    try:
        subscriber_node()
    except rospy.ROSInterruptException:
        pass
