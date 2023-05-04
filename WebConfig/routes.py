from flask import Flask, render_template, request, jsonify
import WebConfig
from WebConfig.DataStructures import *
import os

def read_engines():
    engines = []
    engines_dir = "/root/PycharmProjects/ChessBoard/WebConfig/EngineList"

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

app = WebConfig.app

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

@app.route('/launch_game', methods=["POST"])
def launch_game():
    WebConfig.launch_game()
    return 'OK'

@app.route('/set_autoplay', methods=["POST"])
def set_autoplay():
    WebConfig.autoplay = request.json['autoplay'] == True
    return 'OK'

@app.route('/reset_joycons', methods=["POST"])
def reset_joycons():
    # WebConfig.remove_paired_joycons()
    WebConfig.restart_paired_joycons()
    return 'OK'

@app.route('/reset_game', methods=["POST"])
def reset_game():
    WebConfig.reset_game()
    return 'OK'

@app.route('/quit_game', methods=["POST"])
def quit_game():
    WebConfig.quit()
    return 'OK'

@app.route('/connect-joycons', methods=["POST"])
def connect_joycons():
    for i in range(2):
        WebConfig.connect_joycon()
    joycon_r_status = WebConfig.right_connected  # Example value
    joycon_l_status = WebConfig.left_connected  # Example value

    # Return a JSON response with the updated label values
    return jsonify(joyconRConnected=joycon_r_status, joyconLConnected=joycon_l_status)



if __name__ == '__main__':
    app.run()
