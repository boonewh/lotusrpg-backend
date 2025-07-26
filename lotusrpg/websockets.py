# lotusrpg/websockets.py
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_security import current_user
from functools import wraps

socketio = SocketIO(cors_allowed_origins="*")

def authenticated_only(f):
    """Decorator to require authentication for WebSocket events"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        return f(*args, **kwargs)
    return wrapped

@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        emit('connected', {
            'message': 'Connected successfully',
            'user': {
                'id': current_user.id,
                'username': current_user.username
            }
        })
    else:
        emit('connected', {'message': 'Connected as guest'})

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    print(f'User disconnected: {current_user.username if current_user.is_authenticated else "Guest"}')

# Forum real-time features
@socketio.on('join_forum')
@authenticated_only
def on_join_forum():
    """Join the general forum room for real-time updates"""
    join_room('forum')
    emit('joined_room', {'room': 'forum'})

@socketio.on('join_post')
@authenticated_only
def on_join_post(data):
    """Join a specific post room for real-time comments"""
    post_id = data.get('post_id')
    if post_id:
        room = f'post_{post_id}'
        join_room(room)
        emit('joined_room', {'room': room})

@socketio.on('leave_post')
@authenticated_only
def on_leave_post(data):
    """Leave a specific post room"""
    post_id = data.get('post_id')
    if post_id:
        room = f'post_{post_id}'
        leave_room(room)
        emit('left_room', {'room': room})

# Real-time notifications for new posts/comments
def notify_new_post(post_data):
    """Notify all forum users of a new post"""
    socketio.emit('new_post', post_data, room='forum')

def notify_new_comment(comment_data, post_id):
    """Notify users in a post room of a new comment"""
    socketio.emit('new_comment', comment_data, room=f'post_{post_id}')

def notify_post_update(post_data):
    """Notify users of post updates"""
    socketio.emit('post_updated', post_data, room=f'post_{post_data["id"]}')

def notify_comment_update(comment_data, post_id):
    """Notify users of comment updates"""
    socketio.emit('comment_updated', comment_data, room=f'post_{post_id}')

# Dice rolling real-time
@socketio.on('roll_dice')
@authenticated_only
def on_roll_dice(data):
    """Handle real-time dice rolling"""
    import random
    
    dice_type = data.get('type', 'double10')
    
    if dice_type == 'double10':
        # Your existing double10 logic
        total = 0
        rolls = []
        
        first_roll = [random.randint(1, 10), random.randint(1, 10)]
        rolls.append(first_roll.copy())
        total += sum(first_roll)
        
        if first_roll[0] == 10 and first_roll[1] == 10:
            while True:
                new_roll = [random.randint(1, 10), random.randint(1, 10)]
                rolls.append(new_roll.copy())
                total += sum(new_roll)
                
                if 10 in new_roll:
                    if new_roll[0] == 10 and new_roll[1] == 10:
                        continue
                    elif new_roll[0] == 10 or new_roll[1] == 10:
                        reroll = 0 if new_roll[0] == 10 else 1
                        while new_roll[reroll] == 10:
                            explode_roll = random.randint(1, 10)
                            rolls[-1][reroll] += explode_roll
                            total += explode_roll
                            if explode_roll != 10:
                                break
                        break
                else:
                    break
        
        result = {
            'total': total,
            'rolls': rolls,
            'user': current_user.username
        }
        
        # Emit to the user and optionally to a room if they're in one
        emit('dice_result', result)
        
        # If in a shared room, broadcast to others
        if 'room' in data:
            emit('shared_dice_roll', result, room=data['room'], include_self=False)

# Admin real-time features
@socketio.on('join_admin')
@authenticated_only
def on_join_admin():
    """Join admin room for real-time admin updates"""
    if current_user.has_role('admin'):
        join_room('admin')
        emit('joined_room', {'room': 'admin'})
    else:
        emit('error', {'message': 'Admin access required'})

def notify_admin_action(action_data):
    """Notify admins of important actions"""
    socketio.emit('admin_notification', action_data, room='admin')

# Content editing real-time collaboration
@socketio.on('join_editor')
@authenticated_only
def on_join_editor(data):
    """Join a content editing session"""
    if current_user.has_role('admin'):
        section_id = data.get('section_id')
        if section_id:
            room = f'editor_{section_id}'
            join_room(room)
            emit('joined_editor', {'room': room, 'section_id': section_id})

@socketio.on('editor_update')
@authenticated_only
def on_editor_update(data):
    """Handle real-time editor updates"""
    if current_user.has_role('admin'):
        section_id = data.get('section_id')
        content = data.get('content')
        cursor_position = data.get('cursor_position')
        
        if section_id:
            room = f'editor_{section_id}'
            emit('editor_change', {
                'content': content,
                'cursor_position': cursor_position,
                'user': current_user.username,
                'timestamp': data.get('timestamp')
            }, room=room, include_self=False)