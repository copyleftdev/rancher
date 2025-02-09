from flask import Flask, request
from threading import Thread
import requests

# Constants
DINGTALK_MESSAGE = "Dingtalk setting validated"
MICROSOFTTEAMS_MESSAGE = "MicrosoftTeams setting validated"


class MockServer(Thread):
    def __init__(self, port=5000):
        super().__init__()
        self.port = port
        self.app = Flask(__name__)
        self.url = f"http://127.0.0.1:{self.port}"
        self.app.add_url_rule("/shutdown", view_func=self._shutdown_server)

    def _shutdown_server(self):
        if 'werkzeug.server.shutdown' not in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'

    def shutdown_server(self):
        requests.get(f"http://127.0.0.1:{self.port}/shutdown", headers={'Connection': 'close'})
        self.join()

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, threaded=True)


class MockReceiveAlert(MockServer):
    def api_microsoft_teams(self):
        message = request.json.get("text")
        assert message == MICROSOFTTEAMS_MESSAGE
        return "success"

    def api_dingtalk(self, url):
        message = request.json.get("text")
        assert message.get('content') == DINGTALK_MESSAGE
        return '{"errcode":0,"errmsg":""}'

    def add_endpoints(self):
        self.app.add_url_rule("/microsoftTeams", view_func=self.api_microsoft_teams, methods=('POST',))
        self.app.add_url_rule("/dingtalk/<path:url>/", view_func=self.api_dingtalk, methods=('POST',))

    def __init__(self, port):
        super().__init__(port)
        self.add_endpoints()
