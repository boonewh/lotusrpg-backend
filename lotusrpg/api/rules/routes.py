# lotusrpg/api/rules/routes.py
from flask import request
from flask_restful import Resource
from lotusrpg.models import Section, Content, db
from lotusrpg.schemas import (
    section_schema, sections_schema, 
    content_schema, contents_schema,
    SectionCreateSchema, ContentCreateSchema,
    PaginationSchema
)
from lotusrpg.api.base import BaseResource, AuthenticatedResource, AdminResource, api_response, api_error
from lotusrpg.api import api
from sqlalchemy import or_

class RulebookChaptersResource(BaseResource):
    def get(self, rulebook):
        """Get all chapters for a rulebook"""
        if rulebook not in ['core', 'darkholme']:
            return api_error('Invalid rulebook', 400)
        
        chapters = db.session.query(Section.chapter).filter_by(rulebook=rulebook).distinct().all()
        
        chapter_data = []
        for chapter_tuple in chapters:
            chapter_name = chapter_tuple[0]
            sections = Section.query.filter_by(
                chapter=chapter_name, 
                rulebook=rulebook
            ).all()
            
            chapter_data.append({
                'title': chapter_name,
                'sections': [{
                    'id': s.id,
                    'title': s.title,
                    'slug': s.slug
                } for s in sections]
            })
        
        return api_response(data={'chapters': chapter_data})

class SectionResource(BaseResource):
    def get(self, slug):
        """Get a specific section with contents"""
        section = Section.query.filter_by(slug=slug).first()
        if not section:
            return api_error('Section not found', 404)
        
        return api_response(data=section_schema.dump(section))

class SectionListResource(BaseResource):
    def get(self):
        """Get sections with pagination and filtering"""
        schema = PaginationSchema()
        try:
            args = schema.load(request.args)
        except Exception as e:
            return api_error('Invalid parameters', 400)
        
        query = Section.query
        
        # Apply filters
        rulebook = request.args.get('rulebook')
        if rulebook:
            query = query.filter_by(rulebook=rulebook)
        
        chapter = request.args.get('chapter')
        if chapter:
            query = query.filter_by(chapter=chapter)
        
        # Search
        if args['search']:
            search_term = f"%{args['search']}%"
            query = query.filter(Section.title.ilike(search_term))
        
        # Paginate
        sections = query.paginate(
            page=args['page'],
            per_page=args['per_page'],
            error_out=False
        )
        
        return api_response(data={
            'sections': sections_schema.dump(sections.items),
            'pagination': {
                'page': sections.page,
                'pages': sections.pages,
                'per_page': sections.per_page,
                'total': sections.total,
                'has_next': sections.has_next,
                'has_prev': sections.has_prev
            }
        })

class SectionManagementResource(AdminResource):
    def post(self):
        """Create a new section"""
        schema = SectionCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        # Check if slug exists
        if Section.query.filter_by(slug=data['slug']).first():
            return api_error('Slug already exists', 409)
        
        section = Section(**data)
        db.session.add(section)
        db.session.commit()
        
        return api_response(
            data=section_schema.dump(section),
            message='Section created successfully',
            status=201
        )
    
    def put(self, section_id):
        """Update a section"""
        section = Section.query.get_or_404(section_id)
        
        schema = SectionCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        # Check slug uniqueness (excluding current section)
        existing = Section.query.filter(
            Section.slug == data['slug'],
            Section.id != section_id
        ).first()
        
        if existing:
            return api_error('Slug already exists', 409)
        
        # Update section
        for key, value in data.items():
            setattr(section, key, value)
        
        db.session.commit()
        
        return api_response(
            data=section_schema.dump(section),
            message='Section updated successfully'
        )
    
    def delete(self, section_id):
        """Delete a section"""
        section = Section.query.get_or_404(section_id)
        
        # Delete associated contents first
        Content.query.filter_by(section_id=section_id).delete()
        
        db.session.delete(section)
        db.session.commit()
        
        return api_response(message='Section deleted successfully')

class ContentResource(BaseResource):
    def get(self, content_id):
        """Get specific content"""
        content = Content.query.get_or_404(content_id)
        return api_response(data=content_schema.dump(content))

class ContentManagementResource(AdminResource):
    def post(self):
        """Create new content"""
        schema = ContentCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        content = Content(**data)
        db.session.add(content)
        db.session.commit()
        
        return api_response(
            data=content_schema.dump(content),
            message='Content created successfully',
            status=201
        )
    
    def put(self, content_id):
        """Update content"""
        content = Content.query.get_or_404(content_id)
        
        schema = ContentCreateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        for key, value in data.items():
            setattr(content, key, value)
        
        db.session.commit()
        
        return api_response(
            data=content_schema.dump(content),
            message='Content updated successfully'
        )
    
    def delete(self, content_id):
        """Delete content"""
        content = Content.query.get_or_404(content_id)
        db.session.delete(content)
        db.session.commit()
        
        return api_response(message='Content deleted successfully')

class SearchResource(BaseResource):
    def get(self):
        """Search across all content"""
        query = request.args.get('q', '').strip()
        if not query:
            return api_error('Search query required', 400)
        
        # Search in content data
        search_term = f"%{query}%"
        contents = Content.query.filter(
            Content.content_data.cast(db.String).ilike(search_term)
        ).limit(50).all()
        
        results = []
        for content in contents:
            section = Section.query.get(content.section_id)
            if section:
                results.append({
                    'section_title': section.title,
                    'slug': section.slug,
                    'rulebook': section.rulebook,
                    'content_type': content.content_type,
                    'content_preview': str(content.content_data)[:200] + '...'
                })
        
        return api_response(data={
            'results': results,
            'query': query,
            'count': len(results)
        })

# Register routes
api.add_resource(RulebookChaptersResource, '/rules/<string:rulebook>/chapters')
api.add_resource(SectionResource, '/rules/sections/<string:slug>')
api.add_resource(SectionListResource, '/rules/sections')
api.add_resource(SectionManagementResource, 
                '/rules/sections', 
                '/rules/sections/<int:section_id>')
api.add_resource(ContentResource, '/rules/content/<int:content_id>')
api.add_resource(ContentManagementResource, 
                '/rules/content', 
                '/rules/content/<int:content_id>')
api.add_resource(SearchResource, '/rules/search')