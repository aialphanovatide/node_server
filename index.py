from flask import Flask
from flask_cors import CORS
from routes.docker.docker import docker_bp
from routes.system.system_info import system_bp
from routes.net_test.network_test import net_test_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(system_bp)
app.register_blueprint(docker_bp)
app.register_blueprint(net_test_bp)


if __name__ == '__main__':
    app.run(debug=False, use_reloader=True)
