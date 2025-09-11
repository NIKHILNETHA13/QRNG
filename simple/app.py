from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# Initialize the Flask app and SocketIO instance.
app = Flask(__name__)
# Set a secret key for session management, required by Flask-SocketIO.
app.config['SECRET_KEY'] = 'a_secret_key_for_session_management'
# Enable CORS for development. This allows connections from different domains.
socketio = SocketIO(app, cors_allowed_origins="*")

# A dictionary to keep track of connected users and their session IDs.
users = {}

@app.route('/')
def index():
    """Renders the main index page of the chat application."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
    Handles a new client connection.
    When a new user connects, their session ID is used as their unique identifier.
    We add this user to our dictionary and broadcast the updated user list to all clients.
    """
    session_id = request.sid
    print(f'Client connected: {session_id}')
    users[session_id] = {'id': session_id}
    
    # Broadcast the updated list of users to all connected clients.
    # The 'public_keys' event name is used to indicate the list of available chat partners.
    emit('public_keys', users, broadcast=True)
    
    # Send the unique session ID back to the newly connected client.
    emit('user_info', {'id': session_id}, room=session_id)

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles a client disconnection.
    When a user disconnects, they are removed from the users dictionary.
    The updated user list is then broadcast to all remaining clients.
    """
    session_id = request.sid
    if session_id in users:
        print(f'Client disconnected: {session_id}')
        del users[session_id]
        
    # Broadcast the updated user list to all remaining clients.
    emit('public_keys', users, broadcast=True)

@socketio.on('message')
def handle_message(data):
    """
    Handles a message sent from a client.
    The message and the sender's ID are received from the client.
    The server then emits the message to the intended recipient's session ID.
    """
    receiver_sid = data.get('receiver_sid')
    message = data.get('message')
    sender_sid = data.get('sender_sid')

    print(f'Message from {sender_sid} to {receiver_sid}: {message}')
    
    # Emit the message to the specific receiver's session ID.
    emit('new_message', {'message': message, 'sender_sid': sender_sid}, room=receiver_sid)

if __name__ == '__main__':
    # Run the application with SocketIO.
    # The host='0.0.0.0' is important for deployment on platforms like Render.
    socketio.run(app, debug=True, host='0.0.0.0')
