#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32, String
import random

def publisher_node():
    rospy.init_node('random_publisher', anonymous=True)
    float_pub = rospy.Publisher('random_float', Float32, queue_size=10)
    string_pub = rospy.Publisher('status', String, queue_size=10)

    rate = rospy.Rate(20)  # 20 Hz
    while not rospy.is_shutdown():
        random_float = random.uniform(0, 10.0)
        status = random.choice(["active", "inactive"])

        float_pub.publish(random_float)
        string_pub.publish(status)

        rospy.loginfo(f"Published: {random_float}, Status: {status}")
        rate.sleep()

if __name__ == '__main__':
    try:
        publisher_node()
    except rospy.ROSInterruptException:
        pass
