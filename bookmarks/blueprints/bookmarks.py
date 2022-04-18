from flask import Blueprint, request, jsonify
import validators
from bookmarks.constants import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_406_NOT_ACCEPTABLE
from bookmarks.database.models import Bookmark
from bookmarks.database import db
from flask_jwt_extended import get_jwt_identity, jwt_required


bookmarks = Blueprint("bookmaks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.post('/')
@jwt_required()
def create():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid URL'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_400_BAD_REQUEST

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'create_at': bookmark.create_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED


@bookmarks.get('/')
@bookmarks.get('/<int:id>')
@jwt_required()
def get(id=None):

    current_user = get_jwt_identity()

    if id:

        bookmark = Bookmark.query.filter_by(
            user_id=current_user,
            id=id
        ).first()

        if not bookmark:

            return jsonify({
                'message': 'Item not found'
            }), HTTP_406_NOT_ACCEPTABLE

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'create_at': bookmark.create_at,
            'updated_at': bookmark.updated_at
        }), HTTP_200_OK

    else:

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 1, type=int)
        bookmarks = Bookmark.query.filter_by(
            user_id=current_user
        ).paginate(page=page, per_page=per_page)

        data = []

        for bookmark in bookmarks.items:

            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visit': bookmark.visits,
                'body': bookmark.body,
                'create_at': bookmark.create_at,
                'updated_at': bookmark.updated_at
            })

        meta = {
            'page': bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev
        }

        return jsonify({
            'data': data, 'meta': meta
        }), HTTP_200_OK


@bookmarks.put('/<int:id>')
@jwt_required()
def update(id):

    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(
        user_id=current_user,
        id=id
    ).first()

    if not bookmark:
        return jsonify({
            'message': 'Item not found'
        }), HTTP_406_NOT_ACCEPTABLE

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid URL'
        }), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'create_at': bookmark.create_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK
