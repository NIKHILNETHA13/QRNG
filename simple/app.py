from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__) # This line was missing
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"User connected with session ID: {request.sid}")
    all_users = list(socketio.server.eio.sockets.keys())
    emit('user_list', {'users': all_users}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)