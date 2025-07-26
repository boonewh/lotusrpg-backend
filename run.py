# run.py - Updated for WebSocket support
from lotusrpg import create_app
from lotusrpg.websockets import socketio

app = create_app()

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=True,
        log_output=True
    )