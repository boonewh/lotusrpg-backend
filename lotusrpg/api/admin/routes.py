# lotusrpg/api/admin/routes.py
from flask import request
from flask_security import current_user
from lotusrpg.models import User, Role, Post, Comment, Section, Content, db
from lotusrpg.schemas import user_schema, users_schema, PaginationSchema
from lotusrpg.api.base import AdminResource, api_response, api_error
from lotusrpg.api import api
from lotusrpg.websockets import notify_admin_action
from marshmallow import Schema, fields

class UserRoleUpdateSchema(Schema):
    role_ids = fields.List(fields.Int(), required=True)

class AdminDashboardResource(AdminResource):
    def get(self):
        """Get dashboard statistics"""
        stats = {
            'total_users': User.query.count(),
            'total_sections': Section.query.count(),
            'total_contents': Content.query.count(),
            'total_posts': Post.query.count(),
            'total_comments': Comment.query.count(),
            'active_users': User.query.filter_by(active=True, is_banned=False).count(),
            'banned_users': User.query.filter_by(is_banned=True).count(),
            'locked_users': User.query.filter(User.lockout_until.isnot(None)).count()
        }
        
        # Recent activity
        recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
        recent_users = User.query.order_by(User.id.desc()).limit(5).all()
        
        return api_response(data={
            'stats': stats,
            'recent_posts': [{
                'id': p.id,
                'title': p.title,
                'author': p.author.username,
                'date_posted': p.date_posted.isoformat()
            } for p in recent_posts],
            'recent_users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email
            } for u in recent_users]
        })

class UserManagementResource(AdminResource):
    def get(self):
        """Get users with pagination and search"""
        schema = PaginationSchema()
        try:
            args = schema.load(request.args)
        except Exception as e:
            return api_error('Invalid parameters', 400)
        
        query = User.query
        
        # Search functionality
        if args['search']:
            search_term = f"%{args['search']}%"
            query = query.filter(
                User.username.ilike(search_term) | 
                User.email.ilike(search_term)
            )
        
        # Filter by status
        status = request.args.get('status')
        if status == 'banned':
            query = query.filter_by(is_banned=True)
        elif status == 'active':
            query = query.filter_by(is_banned=False, active=True)
        elif status == 'locked':
            query = query.filter(User.lockout_until.isnot(None))
        
        users = query.paginate(
            page=args['page'],
            per_page=args['per_page'],
            error_out=False
        )
        
        return api_response(data={
            'users': users_schema.dump(users.items),
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })

class UserActionResource(AdminResource):
    def post(self, user_id, action):
        """Perform actions on users (ban, unban, unlock, delete)"""
        user = User.query.get_or_404(user_id)
        
        if action == 'ban':
            user.is_banned = True
            message = f'User {user.username} has been banned'
            
        elif action == 'unban':
            user.is_banned = False
            message = f'User {user.username} has been unbanned'
            
        elif action == 'unlock':
            user.failed_login_attempts = 0
            user.lockout_until = None
            message = f'User {user.username} has been unlocked'
            
        elif action == 'delete':
            # Check if user is admin
            if user.has_role('admin'):
                return api_error('Cannot delete admin user', 400)
            
            # Delete user's posts and comments
            Comment.query.filter_by(user_id=user_id).delete()
            Post.query.filter_by(user_id=user_id).delete()
            
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            # Notify other admins
            notify_admin_action({
                'action': 'user_deleted',
                'target': username,
                'admin': current_user.username
            })
            
            return api_response(message=f'User {username} has been deleted')
            
        else:
            return api_error('Invalid action', 400)
        
        db.session.commit()
        
        # Notify other admins
        notify_admin_action({
            'action': action,
            'target': user.username,
            'admin': current_user.username
        })
        
        return api_response(
            data=user_schema.dump(user),
            message=message
        )

class UserRoleResource(AdminResource):
    def get(self, user_id):
        """Get user's roles and available roles"""
        user = User.query.get_or_404(user_id)
        all_roles = Role.query.all()
        
        return api_response(data={
            'user': user_schema.dump(user),
            'available_roles': [{
                'id': role.id,
                'name': role.name,
                'description': role.description
            } for role in all_roles]
        })
    
    def put(self, user_id):
        """Update user's roles"""
        user = User.query.get_or_404(user_id)
        
        schema = UserRoleUpdateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        # Get new roles
        new_roles = Role.query.filter(Role.id.in_(data['role_ids'])).all()
        user.roles = new_roles
        
        db.session.commit()
        
        # Notify other admins
        notify_admin_action({
            'action': 'roles_updated',
            'target': user.username,
            'new_roles': [role.name for role in new_roles],
            'admin': current_user.username
        })
        
        return api_response(
            data=user_schema.dump(user),
            message='User roles updated successfully'
        )

api.add_resource(AdminDashboardResource, '/admin/dashboard')
api.add_resource(UserManagementResource, '/admin/users')
api.add_resource(UserActionResource, '/admin/users/<int:user_id>/<string:action>')
api.add_resource(UserRoleResource, '/admin/users/<int:user_id>/roles')