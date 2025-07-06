import yaml
import subprocess
import os

WORKDIR = os.path.dirname(os.path.abspath(__file__))
ARDUINO_CLI = os.path.join(WORKDIR, 'bin', 'arduino-cli')
DEFAULT_CONFIG = os.path.join(WORKDIR, 'board_settings.yaml')


class FirmwareFlasher:
    def __init__(self, config_file=DEFAULT_CONFIG, arduino_cli=ARDUINO_CLI):
        self.arduino_cli = arduino_cli
        self.config_file = config_file
        self.settings = self.load_settings(config_file)
        self.fqbn = self.settings['fqbn']
        self.port = self.settings['port']
        self.sketch_path = self.settings['sketch']

    def load_settings(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _run(self, args, msg):
        print(msg)
        return subprocess.run([self.arduino_cli] + args, check=True)

    def compile(self):
        self._run(["compile", "--fqbn", self.fqbn, self.sketch_path],
                  f"📦 Compiling sketch in {self.sketch_path} for {self.fqbn}...")

    def upload(self):
        self._run(["upload", "-p", self.port, "--fqbn", self.fqbn, self.sketch_path],
                  f"⚡ Uploading to {self.port}...")

    def flash(self):
        self.compile()
        self.upload()
        print("✅ Done.")

    def monitor(self):
        print(f"🔍 Opening serial monitor at {self.port}...")
        subprocess.run([self.arduino_cli, "monitor", "-p", self.port])

    def show_settings(self):
        print("🔧 Current settings:")
        for key, value in self.settings.items():
            print(f"  {key}: {value}")

    def __repr__(self):
        return f"<FirmwareFlasher sketch='{self.sketch_path}' port='{self.port}' fqbn='{self.fqbn}'>"


if __name__ == "__main__":
    flasher = FirmwareFlasher()
    flasher.show_settings()
    flasher.compile()
    flasher.flash()
