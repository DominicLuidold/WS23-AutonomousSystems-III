import rospy
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped
from sensor_msgs.msg import LaserScan
from move_base_msgs.msg import MoveBaseGoal, MoveBaseAction
from nav_msgs.msg import MapMetaData, OccupancyGrid, Odometry
from current_pos.msg import PoseInMap
import math
from os import path
import json
import tf
import actionlib


class NavigationScheduler:
    def __init__(self):
        rospy.init_node('navigation_scheduler', log_level=rospy.DEBUG, anonymous=True)
        rospy.loginfo("NavigationScheduler: Startup")

        self._filename = "/killerrobot/token_positions.json"

        #self._client = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        self._tokenpositions = {}
        listener = tf.TransformListener()

        if path.isfile(self._filename):
            with open(self._filename) as fp:
                tokenpositions = json.load(fp)



        #(trans,rot) = listener.lookupTransform('/odom', '/map', rospy.Time(0))

        rospy.loginfo("Loaded token positions")

        self._mapFrame = "map"
        self._robotFrame = "base_footprint"

        self._mapInfo = MapMetaData()
        self._mapInfo = rospy.wait_for_message("map", OccupancyGrid).info

        self._move_base_client = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=1)

        for pos in tokenpositions:
            odomPose = self.calculateOdom(pos)
            self._tokenpositions[pos["name"]] = odomPose

        rospy.logdebug(str(self._tokenpositions))
        #Calculate closest token
        #for each self._tokenpositions
        #self.calculateDistance(odomPose)

        while not rospy.is_shutdown():

            self.driveToPosition(self._tokenpositions[0])

        rospy.logdebug("AAAAAh - finished")


    def calculateOdom(self, mapPose):
        rospy.logdebug("Calculating odom")
        rospy.logdebug(str(self._mapInfo))
        resolution = self._mapInfo.resolution
        x = (mapPose["map_position"]["x"] * resolution) + self._mapInfo.origin.position.x # is this the offset?
        y = (mapPose["map_position"]["x"] * resolution) + self._mapInfo.origin.position.y
        z = 0.0
        return [x,y,z], [0.0,0.0,0.0,-1.0]

    def calculateDistance(self, pos):
        odomPos = rospy.wait_for_message("odom", Odometry).pose.pose
        distance = math.sqrt(math.pow(pos[0] - odomPos.x, 2) + math.pow(pos[1] - odomPos.y,2))
        return distance

    def driveToPosition(self, pos):
        rospy.logdebug("Drive to Position")
        target_pose = Pose(Point(pos[0][0],pos[0][1],pos[0][2]), Quaternion(0.0,0.0,0.0,-1.0))
        rospy.logdebug(str(target_pose))
        
        target = PoseStamped()
        target.header.frame_id = "base_link"
        #target.target_pose.header.frame_id = "map"
        target.pose = target_pose

        self._move_base_client.publish(target)

        #client.wait_for_result()
        rospy.logdebug("Sent pose")

def main():
    try:
        node = NavigationScheduler()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main()