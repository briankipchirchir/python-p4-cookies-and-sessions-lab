#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200


@app.route('/articles')
def index_articles():
    # Fetch all articles from the database
    articles = Article.query.all()
    articles_list = [{
        'id': article.id,
        'title': article.title,
        'author': article.author,
        'preview': article.content[:50]  # Assuming preview is the first 50 chars of content
    } for article in articles]

    return jsonify(articles_list), 200

@app.route('/articles/<int:id>', methods=['GET'])
def show_article(id):
    # Convert article ID to string when storing in the session
    str_id = str(id)
    
    if 'page_views' not in session:
        session['page_views'] = {}

    if str_id not in session['page_views']:
        session['page_views'][str_id] = 0

    if session['page_views'][str_id] < 3:
        session['page_views'][str_id] += 1
        article = db.session.get(Article, id)

        if article:
            words = len(article.content.split())
            minutes_to_read = max(1, words // 200)  # Assuming 200 words per minute

            return jsonify({
                'id': article.id,
                'title': article.title,
                'author': article.author,
                'content': article.content,
                'preview': article.content[:50],
                'page_views': session['page_views'][str_id],
                'minutes_to_read': minutes_to_read
            }), 200
        else:
            return jsonify({'error': 'Article not found'}), 404
    else:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

if __name__ == '__main__':
    app.run(port=5555)
