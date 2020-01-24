import os
import sys
import time
import rospy
import signal
import subprocess
from pathlib import Path
from rospy import Subscriber
from roslaunch import RLException
from ExperimentRunner.Controllers.ROS.IROSController import IROSController
from ExperimentRunner.Utilities.RobotRunnerOutput import RobotRunnerOutput as output


class ROS1Controller(IROSController):
    FNULL = open(os.devnull, 'w')  # block output from showing in terminal
    roscore_proc = None
    roslaunch_pid: str = "/tmp/roslaunch.pid"
    subscribed_topics = []

    def roslaunch_launch_file(self, launch_file: Path):  # TODO: add log_file to output roslaunch pipe to
        output.console_log(f"roslaunch {launch_file}")
        try:

            self.process = subprocess.Popen(f"roslaunch --pid=/tmp/roslaunch.pid {launch_file}",
                                            shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
        except RLException:
            output.console_log("Something went wrong launching the launch file.")
            sys.exit(1)

    def roscore(self):
        self.roscore_proc = subprocess.Popen('roscore', shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
        time.sleep(1)  # wait to be sure roscore is really launched

    def rosinit_robot_runner_node(self):
        try:
            rospy.init_node("robot_runner")
            output.console_log("Successfully initialised ROS node: robot_runner")
        except:
            output.console_log("Could not initialise robot_runner ROS node...")

    def subscribe_to_topic(self, topic, datatype, callback):
        output.console_log(f"Subscribed to topic: {topic}")
        sub = rospy.Subscriber(topic, datatype, callback)
        self.subscribed_topics.append(sub)
        return sub

    def ros_shutdown(self):
        output.console_log("Complete shutdown of all ROS instances initiated...")
        output.console_log("Unregistering all subscribed topics...")
        sub: Subscriber
        for sub in self.subscribed_topics:
            sub.unregister()

        output.console_log("Terminating roslaunch launch file...")
        self.process.send_signal(signal.SIGINT)
        try:
            with open("/tmp/roslaunch.pid", 'r') as myfile:
                pid = int(myfile.read())
                os.kill(pid, signal.SIGINT)
        except FileNotFoundError:
            output.console_log("roslaunch pid not found, continuing normally...")

        while self.process.poll() is None:
            output.console_log_animated("Waiting for graceful exit...")

        rospy.signal_shutdown("Run completed")
        output.console_log("Roslaunch launch file successfully terminated!")