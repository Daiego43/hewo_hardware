import yaml
import subprocess
import os

WORKDIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(WORKDIR, 'neck_config.yaml')
DEFAULT_DEV = "/dev/esp32"
DEFAULT_BAUDRATE = 115200


class FirmwareFlasher:
    def __init__(self, config_file=DEFAULT_CONFIG):
        self.settings = self.load_settings(config_file)
        self.arduino_cli = self.resolve_cli()
        self.board = self.settings['board_settings']
        self.fqbn = self.board['fqbn']
        self.sketch_path = self.board['sketch']
        self.port = self.resolve_port()
        self.baudrate = self.board.get('baudrate', DEFAULT_BAUDRATE)

    def load_settings(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def resolve_cli(self):
        cli_path = self.settings.get('arduino_cli_path')
        if cli_path and cli_path.lower() != "none":
            return cli_path
        return "arduino-cli"  # fallback to default in PATH

    def resolve_port(self):
        port = self.board.get('port')
        if port:
            return port
        elif os.path.exists(DEFAULT_DEV):
            print(f"🔌 Using detected device: {DEFAULT_DEV}")
            return DEFAULT_DEV
        else:
            raise RuntimeError("❌ No port defined and /dev/esp32 not found.")

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
        subprocess.run([self.arduino_cli, "monitor", "-p", self.port, "--baudrate", str(self.baudrate)])

    def show_settings(self):
        print("🔧 Current settings:")
        print(f"  sketch:    {self.sketch_path}")
        print(f"  fqbn:      {self.fqbn}")
        print(f"  port:      {self.port}")
        print(f"  baudrate:  {self.baudrate}")
        print(f"  cli path:  {self.arduino_cli}")

    def __repr__(self):
        return f"<FirmwareFlasher sketch='{self.sketch_path}' port='{self.port}' fqbn='{self.fqbn}'>"


if __name__ == "__main__":
    flasher = FirmwareFlasher()
    flasher.show_settings()
    flasher.flash()
