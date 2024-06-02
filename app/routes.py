from flask import Blueprint, render_template, g, jsonify, current_app as app
from app.models import MongoModels
import logging

from app.aggregations import (
    total_repositories,
    repositories_by_license,
    activity_metrics,
    top_keywords_from_descriptions,
    top_keywords_from_readmes
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
def get_lda():
    try:
        from pyspark.ml.linalg import DenseVector
        models = get_models()
        result = models.get_sample()
        if result:
            transformed, topics_words = models.lda_predict(result)
        
            if transformed:
                transformed_data = transformed.select("topicDistribution").collect()
                transformed_data_json = [
                    {key: (value.tolist() if isinstance(value, DenseVector) else value) for key, value in row.asDict().items()}
                    for row in transformed_data
                ]
            else:
                transformed_data_json = []

            return jsonify({
                'transformed': transformed_data_json,
                'topics_words': topics_words
            })
        else:
            return jsonify({"error": "Failed to get sample data"}), 500
    except Exception as e:
        app.logger.error(f"Error performing LDA: {e}")
        return jsonify({"error": "An error occurred"}), 500
