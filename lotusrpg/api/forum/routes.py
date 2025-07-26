# lotusrpg/api/forum/routes.py
from flask import request
from flask_security import current_user
from lotusrpg.models import Post, Comment, User, db
from lotusrpg.schemas import (
    post_schema, posts_schema,
    comment_schema, comments_schema,
    PaginationSchema
)
from lotusrpg.api.base import BaseResource, AuthenticatedResource, AdminResource, api_response, api_error
from lotusrpg.api import api
from marshmallow import Schema, fields

class PostCreateSchema(Schema):
    title = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 3)
    content = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)

class CommentCreateSchema(Schema):
    content = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1)

class ForumPostsResource(BaseResource):
    def get(self):
        """Get forum posts with pagination"""
        schema = PaginationSchema()
        try:
            args = schema.load(request.args)
        except Exception as e:
            return api_error('Invalid parameters', 400)
        
        query = Post.query.order_by(Post.date_posted.desc())
        
        # Search functionality
        if args['search']:
            search_term = f"%{args['search']}%"
            query = query.filter(
                Post.title.ilike(search_term) | 
                Post.content.ilike(search_term)
            )
        
        # Filter by author
        author = request.args.get('author')
        if author:
            user = User.query.filter_by(username=author).first()
            if user:
                query = query.filter_by(user_id=user.id)
        
        posts = query.paginate(
            page=args['page'],
            per_page=args['per_page'],
            error_out=False
        )
        
        return api_response(data={
            'posts': posts_schema.dump(posts.items),
            'pagination': {
                'page': posts.page,
                'pages': posts.pages,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        })

class PostResource(AuthenticatedResource):
    def get(self, post_id):
        """Get a specific post with comments"""
        post = Post.query.get_or_404(post_id)
        
        # Get comments with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        comments = Comment.query.filter_by(post_id=post_id)\
                              .order_by(Comment.date_posted.asc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
        
        return api_response(data={
            'post': post_schema.dump(post),
            'comments': comments_schema.dump(comments.items),
            'comments_pagination': {
                'page': comments.page,
                'pages': comments.pages,
                'per_page': comments.per_page,
                'total': comments.total,
                'has_next': comments.has_next,
                'has_prev': comments.has_prev
            }
        })
    
    def put(self, post_id):
        """Update a post (author or admin only)"""
        post = Post.query.get_or_404(post_id)
        
        # Check permissions
        if not (current_user == post.author or current_user.has_role('admin')):
            return api_error('Permission denied', 403)
        
        schema = PostCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        post.title = data['title']
        post.content = data['content']
        db.session.commit()
        
        return api_response(
            data=post_schema.dump(post),
            message='Post updated successfully'
        )
    
    def delete(self, post_id):
        """Delete a post (author or admin only)"""
        post = Post.query.get_or_404(post_id)
        
        # Check permissions
        if not (current_user == post.author or current_user.has_role('admin')):
            return api_error('Permission denied', 403)
        
        # Delete associated comments
        Comment.query.filter_by(post_id=post_id).delete()
        
        db.session.delete(post)
        db.session.commit()
        
        return api_response(message='Post deleted successfully')

class PostCreateResource(AuthenticatedResource):
    def post(self):
        """Create a new post"""
        schema = PostCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        post = Post(
            title=data['title'],
            content=data['content'],
            author=current_user
        )
        
        db.session.add(post)
        db.session.commit()
        
        return api_response(
            data=post_schema.dump(post),
            message='Post created successfully',
            status=201
        )

class CommentResource(AuthenticatedResource):
    def post(self, post_id):
        """Add a comment to a post"""
        post = Post.query.get_or_404(post_id)
        
        schema = CommentCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        comment = Comment(
            content=data['content'],
            user_id=current_user.id,
            post_id=post_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return api_response(
            data=comment_schema.dump(comment),
            message='Comment added successfully',
            status=201
        )
    
    def put(self, post_id, comment_id):
        """Update a comment (author or admin only)"""
        comment = Comment.query.get_or_404(comment_id)
        
        # Check permissions
        if not (current_user.id == comment.user_id or current_user.has_role('admin')):
            return api_error('Permission denied', 403)
        
        schema = CommentCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        comment.content = data['content']
        db.session.commit()
        
        return api_response(
            data=comment_schema.dump(comment),
            message='Comment updated successfully'
        )
    
    def delete(self, post_id, comment_id):
        """Delete a comment (author or admin only)"""
        comment = Comment.query.get_or_404(comment_id)
        
        # Check permissions
        if not (current_user.id == comment.user_id or current_user.has_role('admin')):
            return api_error('Permission denied', 403)
        
        db.session.delete(comment)
        db.session.commit()
        
        return api_response(message='Comment deleted successfully')

class UserPostsResource(BaseResource):
    def get(self, username):
        """Get posts by a specific user"""
        user = User.query.filter_by(username=username).first_or_404()
        
        schema = PaginationSchema()
        try:
            args = schema.load(request.args)
        except Exception as e:
            return api_error('Invalid parameters', 400)
        
        posts = Post.query.filter_by(author=user)\
                         .order_by(Post.date_posted.desc())\
                         .paginate(
                             page=args['page'],
                             per_page=args['per_page'],
                             error_out=False
                         )
        
        return api_response(data={
            'user': {
                'username': user.username,
                'image_file': user.image_file
            },
            'posts': posts_schema.dump(posts.items),
            'pagination': {
                'page': posts.page,
                'pages': posts.pages,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        })

# Register routes
api.add_resource(ForumPostsResource, '/forum/posts')
api.add_resource(PostCreateResource, '/forum/posts/create')
api.add_resource(PostResource, '/forum/posts/<int:post_id>')
api.add_resource(CommentResource, 
                '/forum/posts/<int:post_id>/comments',
                '/forum/posts/<int:post_id>/comments/<int:comment_id>')
api.add_resource(UserPostsResource, '/forum/users/<string:username>/posts')