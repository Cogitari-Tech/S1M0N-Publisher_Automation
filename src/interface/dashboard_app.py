"""
S1M0N Dashboard v8.2 - Stability & i18n Release
"""
import os
import json
import logging
import threading
import psutil
import gc
import time
from datetime import datetime
from flask import (
    Flask, render_template, jsonify, request,
    send_from_directory, render_template_string, current_app
)
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
from sqlalchemy import text

from src.config.database import get_db, init_db
from src.models.schema import (
    PublishedArticle, SystemSettings, RSSFeed,
    CachedContent, PendingArticle, Thread, Message
)
from src.services.content_engine import ContentEngine
from src.services.validators import (
    InputValidator, SecurityFlags, validate_request_data
)
from src.services.deployment_service import DeploymentService

# ------------------------------------------------------------------------------
# App & Security Setup
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "https://cdn.jsdelivr.net"],
    'style-src': [
        "'self'", "'unsafe-inline'",
        "https://fonts.googleapis.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com"
    ],
    'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
    'img-src': ["'self'", "data:", "https:"],
}

# Desativar Talisman em desenvolvimento
if os.getenv('DOCKER_ENV') == 'production':
    Talisman(
        app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        content_security_policy_report_only=False
    )

logger = logging.getLogger(__name__)
SYSTEM_STATE = "STOPPED"

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    """Rota principal - renderiza o dashboard"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'dashboard'}), 200

@app.route('/api/control', methods=['POST'])
def control():
    global SYSTEM_STATE
    action = request.json.get('action')

    if action in ['START', 'PAUSE', 'STOP']:
        SYSTEM_STATE = action if action != 'START' else 'RUNNING'
        return jsonify({'state': SYSTEM_STATE})

    if action == 'OPTIMIZE':
        try:
            gc.collect()
            db = get_db()
            db.execute(text("VACUUM"))
            db.close()
            logger.info("System optimized manually")
            return jsonify({'state': SYSTEM_STATE, 'message': 'System Optimized'})
        except Exception:
            logger.exception("System optimization failed")
            return jsonify({
                'state': SYSTEM_STATE,
                'error': 'Internal optimization error'
            }), 500

    return jsonify({'state': SYSTEM_STATE})


@app.route('/api/status/deployment')
def deployment_status():
    env = os.getenv('FLASK_ENV', 'DEV').upper()
    try:
        is_ready = DeploymentService.prepare_build(env)
        return jsonify({'env': env, 'ready': is_ready, 'version': 'v8.3'})
    except Exception:
        current_app.logger.exception(
            "Deployment status check failed for env %s", env
        )
        return jsonify({
            'env': env,
            'ready': False,
            'error': 'Internal deployment status check failed'
        }), 500


@app.route('/api/providers/toggle', methods=['POST'])
@validate_request_data({'provider': str, 'enabled': bool})
def toggle_provider():
    data = request.json
    provider = data['provider']
    enabled = data['enabled']

    provider_key_map = {
        'gnews': 'gnews_api_key',
        'newsapi': 'newsapi_key',
        'currents': 'currents_api_key'
    }

    if provider not in provider_key_map:
        return jsonify({'success': False, 'error': 'Unknown provider'}), 400

    db = get_db()
    try:
        if enabled:
            key_setting = provider_key_map[provider]
            setting = db.query(SystemSettings).filter(
                SystemSettings.key == key_setting
            ).first()

            api_key = setting.value if setting else None
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'API key not configured',
                    'blocked': True
                }), 403

            valid, error = InputValidator.validate_api_key(api_key, provider)
            if not valid:
                return jsonify({
                    'success': False,
                    'error': error,
                    'blocked': True
                }), 403

        state_key = f'enable_{provider}'
        state = db.query(SystemSettings).filter(
            SystemSettings.key == state_key
        ).first()

        if state:
            state.value = str(enabled).lower()
        else:
            db.add(SystemSettings(key=state_key, value=str(enabled).lower()))

        db.commit()
        return jsonify({'success': True, 'provider': provider, 'enabled': enabled})
    finally:
        db.close()


@app.route('/api/history/<session_id>', methods=['GET'])
def get_history_detail(session_id):
    db = get_db()
    try:
        thread = db.query(Thread).filter(Thread.session_id == session_id).first()
        if not thread:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        messages = db.query(Message).filter(
            Message.thread_id == thread.id
        ).order_by(Message.timestamp).all()

        return jsonify({
            'success': True,
            'session_id': thread.session_id,
            'title': thread.title,
            'created_at': thread.created_at.isoformat(),
            'status': thread.status,
            'messages': [
                {
                    'role': m.role,
                    'content': m.content,
                    'tokens': m.tokens_count,
                    'timestamp': m.timestamp.isoformat()
                } for m in messages
            ]
        })
    except Exception:
        logger.exception("Error fetching history")
        return jsonify({
            'success': False,
            'error': 'Internal server error while fetching history'
        }), 500
    finally:
        db.close()


@app.route('/api/model', methods=['GET', 'POST'])
def model_config():
    db = get_db()
    try:
        if request.method == 'POST':
            mode = request.json.get('mode', 'pro').lower()
            if mode not in ['pro', 'flash']:
                return jsonify({'success': False, 'error': 'Invalid mode'}), 400

            setting = db.query(SystemSettings).filter_by(
                key='ai_model_mode'
            ).first()

            if setting:
                setting.value = mode
            else:
                db.add(SystemSettings(key='ai_model_mode', value=mode))

            db.commit()
            return jsonify({'success': True, 'mode': mode})

        setting = db.query(SystemSettings).filter_by(
            key='ai_model_mode'
        ).first()
        return jsonify({'success': True, 'mode': setting.value if setting else 'pro'})
    except Exception:
        logger.exception("Model configuration failed")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    finally:
        db.close()


@app.route('/api/gemini/validate', methods=['POST'])
@limiter.limit("10 per minute")
def gemini_validate():
    api_key = request.json.get('api_key')
    if not api_key:
        return jsonify({'success': False, 'error': 'Missing API key'}), 400

    try:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'External API error'
            }), resp.status_code

        models = resp.json().get('models', [])
        valid = [
            m['name'].replace('models/', '')
            for m in models
            if 'generateContent' in m.get('supportedGenerationMethods', [])
        ]

        valid.sort(key=lambda x: (0 if 'flash' in x else 1))
        return jsonify({'success': True, 'models': valid})

    except Exception:
        logger.exception("Gemini validation failed")
        return jsonify({
            'success': False,
            'error': 'Internal server error while validating API key'
        }), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
