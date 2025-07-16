import yaml
import streamlit as st
from epj_neck import ESP32NeckController, test_velocities, test_servos
st.set_page_config(layout="wide")

class ServoControl:
    def __init__(self, id, settings):
        self.id = id
        self.max_cw_vel = settings["pwm_config"]["max_cw"]
        self.max_ccw_vel = settings["pwm_config"]["max_ccw"]
        self.stop_vel = settings["pwm_config"]["stop"]

    def main_widget(self):
        st.markdown(f"## Servo: {self.id}")
        self.velocity_widget()
        self.servo_widget()

    def velocity_widget(self):
        st.markdown(f"### Velocity")
        self.servo_vel = st.slider(
            label=f"servo_{self.id}_vel",
            min_value=self.max_ccw_vel,
            max_value=self.max_cw_vel,
            step=1, value=self.stop_vel)

    def servo_widget(self):
        st.markdown(f"### Servo move")
        self.servo_angle = st.slider(
            label=f"servo_{self.id}_vel",
            min_value=-180,
            max_value=180,
            step=1, value=0)

    def reset_widget(self):
        pass


class WebServoController:
    def __init__(self, settings="neck_config.yaml"):
        with open(settings, "r") as stream:
            self.settings = yaml.safe_load(stream)

        self.servo_settings = self.settings["servo_settings"]
        self.servo_widgets = []
        for key, setting in self.servo_settings.items():
            self.servo_widgets.append(ServoControl(key, setting))
        self.cols = st.columns(len(self.servo_widgets) + 1)


    def main(self):
        vel_cmd = "V "
        vpwm_list = []
        ang_cmd = "A "
        apwm_list = []
        for i, widget in enumerate(self.servo_widgets):
            with self.cols[i]:
                widget.main_widget()
            vel_cmd += f"{widget.servo_vel} "
            vpwm_list.append(widget.servo_vel)
            ang_cmd += f"{widget.servo_angle} "
            apwm_list.append(widget.servo_angle)

        with self.cols[-1]:
            st.markdown("## Serial communication")
            st.code(vel_cmd)
            st.code(ang_cmd)
            if st.button("Send velocity cmd", use_container_width=True):
                with ESP32NeckController("/dev/esp32") as controller:
                    controller.set_pwm(vpwm_list)
                st.success(vel_cmd)
            if st.button("Send angle cmd", use_container_width=True):
                with ESP32NeckController("/dev/esp32") as controller:
                    controller.move_angles(apwm_list)
                st.success(ang_cmd)

        if st.button("Test servos", use_container_width=True):
            test_servos()
        if st.button("Stop All", use_container_width=True):
            with ESP32NeckController("/dev/esp32") as controller:
                controller.stop_all()
        if st.button("Test velocities", use_container_width=True):
            test_velocities()



WebServoController("neck_config.yaml").main()



