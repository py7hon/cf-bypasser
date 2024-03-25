from flask import Flask, jsonify, request, Response
from CFSession import cfSession, cfDirectory
import threading
import os
import logging
import json

CACHE_DIR = os.path.join(os.getcwd(), "cache")
WEB_TARGET = "https://multimovies.art/"
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Renewer():
    def __init__(self, target: str):
        self.renewing = False
        self.target = target
        self._thread = None

    def _renew_backend(self, session: cfSession):
        self.renewing = True
        try:
            resp = session.get(self.target)
            logger.info(f"Renewal request for {self.target} completed with status code {resp.status_code}")
        except Exception as e:
            logger.error(f"Renewal request for {self.target} failed with error: {str(e)}")
        finally:
            self.renewing = False
    
    def renew(self, session: cfSession):
        cookie_invalid = False
        if self.renewing:
            return {"status": False, "reason": "Renew process undergoing, please be patient"}
        response = session.session.get(self.target)
        cookie_availability = response.status_code == 200

        cookie_status = cookie_availability
        if cookie_status:
            return {"status": False, "reason": "Cookie is valid"}
        else:
            cookie_invalid = True
        self._thread = threading.Thread(target=self._renew_backend, args=(session,))
        self._thread.start() 
        return {"status": True, "reason": "Cookie was invalid, recreating..." if (cookie_invalid) else "Cookies will be created soon"}

def json_resp(jsondict, status=200):
    resp = jsonify(jsondict)
    resp.status_code = status
    return resp

def isSiteValid(url):
    response = session.session.get(url)
    return response.status_code == 200

def reverse_proxy(url, method, headers, data, params=None):
    if params:
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        target_url = f"{WEB_TARGET}{url}?{query_string}"
    else:
        target_url = WEB_TARGET + url
    res = session.get(target_url)
    content = res.content.decode('utf-8')
    return content

@app.before_request
def before_request():
    if not isSiteValid(WEB_TARGET):
        renew_resp = renewer.renew(session)
        if not renew_resp["status"]:
            logger.warning(f"Failed to renew cookies for {WEB_TARGET}. Reason: {renew_resp['reason']}")
            return {"status": False, "reason": "Renewer is not initialized yet"}, 403

@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    headers = {key: value for (key, value) in request.headers}
    data = request.get_data()
    method = request.method
    res = reverse_proxy(path, method, headers, data, request.args)
    response = Response(res)
    return response

@app.route("/", methods=["GET"])
def homeproxy():
    headers = {key: value for (key, value) in request.headers}
    data = request.get_data()
    method = request.method
    res = reverse_proxy(request.path, method, headers, data, request.args)
    response = Response(res)
    return response

@app.route("/getcookie",methods=["GET"])
def getcookie():
    renew_resp = renewer.renew(session)
    if not renew_resp["status"]: 
        return json_resp(renew_resp, status=403)
    else: 
        return json_resp(renew_resp, status=200)

if __name__ == "__main__":
    session = cfSession(directory=cfDirectory(CACHE_DIR), headless_mode=True)
    renewer = Renewer(target=WEB_TARGET)
    app.run("0.0.0.0", port=8080)