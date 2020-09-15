from flask import Flask, jsonify, request, session, render_template, send_file, make_response, redirect
import os, string, random, datetime, sys
import requests
from functools import wraps
from flask_cors import CORS
import jwt
from MOOCFiRipper import MOOCFiRipper

PORT = os.environ.get('PORT') or 5492
app = Flask(__name__, static_folder='templates/', static_url_path='')
debugMode = os.environ.get('DebugMode') or False
app.config['SECRET_KEY'] = "DebugPurposes"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
CORS(app)
TOKEN_DICT = {}


def check_user(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('token') or request.cookies.get('token')
        if not token:
            return jsonify({'status': 0, 'msg': 'No Token Found In Either Cookies or Header'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            resp = make_response(jsonify({'status': 0, 'msg': 'Invalid Token'}))
            resp.set_cookie('token', expires=0)
            return resp, 403
        return func(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    if request.cookies.get('token'):
        if request.cookies.get('token') in TOKEN_DICT:
            return redirect("/panel", code=302)
        elif request.cookies.get('token') not in TOKEN_DICT:
            resp = make_response(render_template('login.html'))
            resp.set_cookie('token', expires=0)
            return resp
    return render_template('login.html')

#For the Panel - Tells frontend if server is alive
@app.route("/pingServer", methods=['GET'])
def pingServer():
    token = request.args.get('token') or request.cookies.get('token')
    r = requests.get("https://tmc.mooc.fi/assets/organizations-0caa66a7730c06b013b579ca90ac61263f38a7a3d9a9f755bcc3f2fc8ea28c6f.css", allow_redirects=True, timeout=5, stream=True)
    if (r.status_code >= 200 or r.status_code <= 299) == False:
        return jsonify({'status': 1, 'login': -1, 'tmc': 0, 'msg': 'You have a connection to the server but we cannot connect to the MOOC.fi servers. Ensure your ISP or DNS is not blocking https://tmc.mooc.fi/'})
    if not token or token not in TOKEN_DICT:
        return jsonify({'status': 1, 'login': 0, 'tmc': 1, 'msg': "You have a connection to the server but you are not logged in!"})
    return jsonify({'status': 1, 'login': 1, 'tmc': 1})

#Added so the user is told to use POST to login
@app.route("/login", methods=['GET'])
def loginGETMethod():
    return jsonify({'status': 0, 'msg': 'You are trying to submit using GET, try POST instead'}), 404


@app.route("/login", methods=['POST'])
def login():
    if not request.form.get("username") or not request.form.get("password") or not request.form.get("user_agent"):
        return jsonify({'status': 0, 'msg': 'Missing Login Forms', 'arguments': {'username': request.form.get("username"), 'password': request.form.get("password"), 'user_agent': request.form.get("user_agent")}}), 403
    MOOCFiObject = MOOCFiRipper(username=request.form.get("username"), password=request.form.get("password"), user_agent=request.form.get("user_agent"))
    if MOOCFiObject.checkLogin()['status'] == 1:
        token = jwt.encode({
            'username': request.form.get("username"),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        },
        app.config['SECRET_KEY'])
        TOKEN_DICT[token.decode('utf-8')] = MOOCFiObject
        resp = make_response(jsonify({'status': 1, 'msg': 'Login to MOOC.fi Successful', 'token': token.decode('utf-8'), 'username': request.form.get("username"), 'user_agent': request.form.get("user_agent") }))
        resp.set_cookie('token', token.decode('utf-8'))
        return resp
    elif MOOCFiObject.checkLogin()['status'] == 0:
        return jsonify({'status': 0, 'msg': 'Login Failed', 'username': request.form.get("username"), 'user_agent': request.form.get("user_agent")})

@app.route("/panel")
@check_user
def panel():
    token = request.args.get('token') or request.cookies.get('token')
    if token not in TOKEN_DICT:
        resp = make_response(redirect("/", code=302))
        resp.set_cookie('token', expires=0)
        return resp
    return render_template('panel.html')

#Logout (For the Panel but you can do the same with API)
@app.route("/logout")
@check_user
def logout():
    token = request.args.get('token') or request.cookies.get('token')
    resp = make_response(redirect("/", code=302))
    resp.set_cookie('token', expires=0)
    try:
        del TOKEN_DICT[token]
    except:
        pass
    return resp

#Check if login is valid (good if your specifically using API)
@app.route("/checkLogin", methods=['GET'])
@check_user
def checkLogin():
    token = request.args.get('token') or request.cookies.get('token')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    MOOCFIObject = TOKEN_DICT[token]
    res = MOOCFIObject.checkLogin()
    if res['status'] == 0:
        return jsonify(res), 403
    return jsonify(res)

#Return all assignments
@app.route("/retAllAssn", methods=['GET'])
@check_user
def retAllAssn():
    token = request.args.get('token') or request.cookies.get('token')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    MOOCFIObject = TOKEN_DICT[token]
    res = MOOCFIObject.retAllAssn()
    if res['status'] == 0:
        return jsonify(res), 403
    return jsonify(res)

#Return all completed assignments - This will take awhile to load since it has to check each assignment
@app.route("/retCompAssn", methods=['GET'])
@check_user
def retCompAssn():
    token = request.args.get('token') or request.cookies.get('token')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    MOOCFIObject = TOKEN_DICT[token]
    res = MOOCFIObject.retCompAssn()
    if res['status'] == 0:
        return jsonify(res), 403
    return jsonify(res)

#Return results for a specific assignment
@app.route("/retCompAssnById", methods=['GET'])
@check_user
def retCompAssnById():
    token = request.args.get('token') or request.cookies.get('token')
    exer_id = request.args.get('exer_id')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    if not exer_id or len(exer_id) != 5:
        return jsonify({'status': 0, 'msg': 'Invalid Exercise ID - Must be 5 digits long'}), 403
    MOOCFIObject = TOKEN_DICT[token]
    res = MOOCFIObject.retCompAssnById(exer_id=exer_id)
    if res['status'] == 0:
        return jsonify(res), 403
    return jsonify(res)

#Download suggested answer as a zip
@app.route("/download_suggestion", methods=['GET'])
@check_user
def download_suggestion():
    token = request.args.get('token') or request.cookies.get('token')
    exer_id = request.args.get('exer_id')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    if not exer_id or len(exer_id) != 5:
        return jsonify({'status': 0, 'msg': 'Invalid Exercise ID - Must be 5 digits long', 'exer_id': exer_id, 'len': len(exer_id)}), 403
    MOOCFIObject = TOKEN_DICT[token]

    res = MOOCFIObject.download_suggestion(exer_id=request.args.get('exer_id'))
    if res['status'] == 1:
        return send_file(res['object'],
                        mimetype='application/zip',
                        as_attachment=True,
                        attachment_filename=f'{request.args.get("exer_id")}_suggestion.zip')
    elif res['status'] == 0:
        return jsonify(res), 403


#Download the beginners template of an exercise as a zip
@app.route("/download_template", methods=['GET'])
@check_user
def download_template():
    token = request.args.get('token') or request.cookies.get('token')
    exer_id = request.args.get('exer_id')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    if not exer_id or len(exer_id) != 5:
        return jsonify({'status': 0, 'msg': 'Invalid Exercise ID - Must be 5 digits long', 'exer_id': exer_id, 'len': len(exer_id)}), 403
    MOOCFIObject = TOKEN_DICT[token]
    res = MOOCFIObject.download_template(exer_id=request.args.get('exer_id'))
    if res['status'] == 1:
        return send_file(res['object'],
                        mimetype='application/zip',
                        as_attachment=True,
                        attachment_filename=f'{request.args.get("exer_id")}_template.zip')
    elif res['status'] == 0:
        return jsonify(res), 403


#Download your successful submission
@app.route("/download_success", methods=['GET'])
@check_user
def download_success():
    token = request.args.get('token') or request.cookies.get('token')
    exer_id = request.args.get('exer_id')
    if token not in TOKEN_DICT:
        return jsonify({'status': 0, 'msg': 'Token does not exist'}), 403
    if not exer_id or len(exer_id) != 5:
        return jsonify({'status': 0, 'msg': 'Invalid Exercise ID - Must be 5 digits long', 'exer_id': exer_id, 'len': len(exer_id)}), 403
    MOOCFIObject = TOKEN_DICT[token]

    res = MOOCFIObject.download_your_success_submission(exer_id=request.args.get('exer_id'))
    if res['status'] == 1:
        return send_file(res['object'],
                        mimetype='application/zip',
                        as_attachment=True,
                        attachment_filename=f'{request.args.get("exer_id")}_success_submission.zip')
    elif res['status'] == 0:
        return jsonify(res), 403

if __name__ == "__main__":
    print("MOOCFi Tools Server Running - To Shut Down, Press Cntrl/Command + C")
    if len(sys.argv) == 2:
        PORT = sys.argv[1]
    if len(sys.argv) == 3:
        PORT = sys.argv[1]
        debugMode = (True if sys.argv[2] == "1" else False)
    app.run(port=PORT, debug=True)