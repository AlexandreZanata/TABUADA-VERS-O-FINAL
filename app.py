from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Dicionário para armazenar os maiores placares de cada sala
rooms = {}

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/join', methods=['POST'])
def join():
    room_code = request.form['room_code']
    if room_code not in rooms:
        rooms[room_code] = []
    return redirect(url_for('game', room_code=room_code))

@app.route('/game/<room_code>')
def game(room_code):
    return render_template('game.html', room_code=room_code)

@app.route('/save_score', methods=['POST'])
def save_score():
    player = request.form['player']
    score = int(request.form['score'])
    room_code = request.form['room_code']

    if room_code not in rooms:
        rooms[room_code] = []

    player_found = False
    for i, (p, s) in enumerate(rooms[room_code]):
        if p == player:
            if score > s:
                rooms[room_code][i] = (player, score)
            player_found = True
            break
    
    if not player_found:
        rooms[room_code].append((player, score))

    rooms[room_code].sort(key=lambda x: x[1], reverse=True)

    socketio.emit('update_scores', {'high_scores': rooms[room_code]}, room=room_code)
    return jsonify(high_scores=rooms[room_code])

@socketio.on('join')
def on_join(data):
    room_code = data['room_code']
    join_room(room_code)
    emit('update_scores', {'high_scores': rooms.get(room_code, [])}, room=room_code)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


