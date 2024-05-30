from flask import Blueprint, render_template, jsonify, current_app as app
from app.aggregations import (
    total_repositories,
    repositories_by_license,
    activity_metrics,
    top_keywords_from_descriptions,
    top_keywords_from_readmes
)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/api/total_repositories', methods=['GET'])
def get_total_repositories():
    result = total_repositories(app.db)
    return jsonify(result)

@main.route('/api/repositories_by_license', methods=['GET'])
def get_repositories_by_license():
    result = repositories_by_license(app.db)
    return jsonify(result)

@main.route('/api/activity_metrics', methods=['GET'])
def get_activity_metrics():
    result = activity_metrics(app.db)
    return jsonify(result)

@main.route('/api/top_keywords_from_descriptions', methods=['GET'])
def get_top_keywords_from_descriptions():
    result = top_keywords_from_descriptions(app.db)
    return jsonify(result)

@main.route('/api/top_keywords_from_readmes', methods=['GET'])
def get_top_keywords_from_readmes():
    result = top_keywords_from_readmes(app.db)
    return jsonify(result)
