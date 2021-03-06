from Controllers.Experiment.Run.IRunController import IRunController
from Procedures.OutputProcedure import OutputProcedure as output


###     =========================================================
###     |                                                       |
###     |                  NativeRunController                  |
###     |       - Define how to perform a Native run            |
###     |       - Mostly use predefined, generic functions      |
###     |         as defined in the abstract parent             |
###     |                                                       |
###     |       * Any function which is implementation          |
###     |         specific (Native) should be declared here     |
###     |                                                       |
###     =========================================================
class NativeRunController(IRunController):
    def do_run(self):
        self.ros.roscore_start()

        self.wait_for_necessary_topics_and_nodes()

        output.console_log_bold("All necessary nodes and topics available, everything is ready for experiment!")

        self.ros.rosbag_start_recording_topics(
            self.config.topics_to_record,  # Topics to record
            str(self.run_dir.absolute()) + '/topics',  # Path to record .bag to
            f"rosbag_run{self.current_run}"  # Bagname to kill after run
        )

        self.run_runscript_if_present()
        self.set_run_stop()
        self.run_start()
        self.run_wait_completed()
        self.ros.rosbag_stop_recording_topics(f"rosbag_run{self.current_run}")
        self.ros.native_shutdown()
