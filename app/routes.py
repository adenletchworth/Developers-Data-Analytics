from flask import Blueprint, render_template, g, jsonify, current_app as app
from app.models import MongoModels
from app.extensions import cache

from app.aggregations import (
    total_repositories,
    repositories_by_license,
    activity_metrics,
    top_keywords_from_descriptions,
    top_keywords_from_readmes,
    avg_statistics,
    stars_over_time,
    repositories_by_language,
    language_pairs,
)

main = Blueprint('main', __name__)

def get_models():
    if 'models' not in g:
        g.models = MongoModels(app.config['MONGO_URI'], "Developer", "github_repos")
    return g.models

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/test')
def test():
    return render_template('test.html')

@main.route('/force')
def force():
    return render_template('force.html')

@main.route('/api/total_repositories', methods=['GET'])
def get_total_repositories():
    try:
        result = total_repositories(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching total repositories: {e}")
        return jsonify({"error": "An error occurred"}), 500

@main.route('/api/repositories_by_license', methods=['GET'])
def get_repositories_by_license():
    try:
        result = repositories_by_license(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching repositories by license: {e}")
        return jsonify({"error": "An error occurred"}), 500

@main.route('/api/language_pairs', methods=['GET'])
def get_language_pairs():
    try:
        result = language_pairs(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching language pairs: {e}")
        return jsonify({"error": "An error occurred"}), 500
    
@main.route('/api/repositories_by_language', methods=['GET'])
def get_repositories_by_language():
    try:
        result = repositories_by_language(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching repositories by language: {e}")
        return jsonify({"error": "An error occurred"}), 500

@main.route('/api/activity_metrics', methods=['GET'])
def get_activity_metrics():
    try:
        result = activity_metrics(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching activity metrics: {e}")
        return jsonify({"error": "An error occurred"}), 500

@main.route('/api/top_keywords_from_descriptions', methods=['GET'])
def get_top_keywords_from_descriptions():
    try:
        result = top_keywords_from_descriptions(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching top keywords from descriptions: {e}")
        return jsonify({"error": "An error occurred"}), 500

@main.route('/api/top_keywords_from_readmes', methods=['GET'])
def get_top_keywords_from_readmes():
    try:
        result = top_keywords_from_readmes(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching top keywords from readmes: {e}")
        return jsonify({"error": "An error occurred"}), 500

@main.route('/api/lda', methods=['GET'])
@cache.cached(timeout=60*60)  # 1 hr
def get_lda():
    try:
        models = get_models()
        topics_words = models.fit_lda()

        if topics_words:
            return jsonify({
                'topics_words': topics_words
            })
        else:
            return jsonify({"error": "Failed to fit LDA model"}), 500
    except Exception as e:
        app.logger.error(f"Error performing LDA: {e}")
        return jsonify({"error": "An error occurred"}), 500
    

@main.route('/api/avg_statistics', methods=['GET'])
def get_avg_statistics():
    try:
        result = avg_statistics(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching average statistics: {e}")
        return jsonify({"error": "An error occurred"}), 500
    
@main.route('/api/stars_over_time', methods=['GET'])
def get_stars_over_time():
    try:
        result = stars_over_time(app.db)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error fetching stars over time: {e}")
        return jsonify({"error": "An error occurred"}), 500
        


