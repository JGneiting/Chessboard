from flask import Flask, render_template, request

import WebConfig
from WebConfig.DataStructures import *
import os

def read_engines():
    engines = []
    engines_dir = "WebConfig/EngineList"

    for filename in os.listdir(engines_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(engines_dir, filename)) as f:
                lines = f.readlines()
                name = lines[0].strip().split(": ")[1]
                elo = lines[1].strip().split(": ")[1]
                path = lines[2].strip().split(": ")[1]
                engine = Engine(name, elo, path)
                engines.append(engine)

    return engines


app = Flask(__name__)

@app.route('/')
def index():
    white_player = WebConfig.white
    black_player = WebConfig.black
    engines = read_engines()
    return render_template('MainScreen.html', white=white_player, black=black_player, engine_files=engines)

@app.route('/set_white', methods=['POST'])
def set_white():
    engine_name = request.json['engineName']
    print(engine_name)
    WebConfig.white.engine = engine_name
    return 'OK'

@app.route('/set_black', methods=['POST'])
def set_black():
    engine_name = request.json['engineName']
    print(engine_name)
    WebConfig.black.engine = engine_name
    return 'OK'

@app.route('/set_white_human', methods=['POST'])
def set_white_human():
    human = request.json['human']
    print(human)
    WebConfig.white.human = human == True
    return 'OK'

@app.route('/set_black_human', methods=['POST'])
def set_black_human():
    human = request.json['human']
    print(human)
    WebConfig.black.human = human == True
    return 'OK'


if __name__ == '__main__':
    app.run()
