import yaml
from jinja2 import Template

def generate_ino(config_path, template_path, output_path, html_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    servo_settings = config['servo_settings']
    first_servo = list(servo_settings.values())[0]

    constants = {
        'NUM_SERVOS': len(servo_settings),
        'STOP_PWM': first_servo['pwm_config']['stop'],
        'MAX_CW_PWM': first_servo['pwm_config']['max_cw'],
        'MAX_CCW_PWM': first_servo['pwm_config']['max_ccw'],
        'MS_PER_DEG': int(1000 / first_servo['degrees_per_second'] * first_servo['calibration_factor']),
        'DEADZONE': first_servo['deadzone'],
        'SERVO_PINS': ', '.join(str(s['gpio']) for s in servo_settings.values()),
        'AP_SSID': 'SPJ-Platform',
        'AP_PASSWORD': 'spjp1234',
    }

    with open(html_path, 'r') as f:
        html_content = f.read().replace('"""', '\"\"\"')

    # Wrap as rawliteral
    index_html_literal = f'const char index_html[] PROGMEM = R"rawliteral({html_content})rawliteral";'
    constants['INDEX_HTML'] = index_html_literal

    with open(template_path, 'r') as f:
        template = Template(f.read())

    ino_code = template.render(**constants)

    with open(output_path, 'w') as f:
        f.write(ino_code)
    print(f"✅ INO generado en: {output_path}")

if __name__ == '__main__':
    generate_ino(
        config_path='neck_config.yaml',
        template_path='ino_template.ino',
        output_path='epj-neck/epj-neck.ino',
        html_path='index.html'
    )
