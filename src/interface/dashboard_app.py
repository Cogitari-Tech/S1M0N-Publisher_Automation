"""
S1M0N Dashboard v8.2 - Stability & i18n Release
Phases: 1 (Structure Restoration), 2 (Contrast/UI), 3 (Deep i18n)
Refactored for Phase 4 (Templates & Static Assets)
"""
import os
import json
import logging
import threading
import psutil
import gc
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib

# Imports da Arquitetura
from src.config.database import get_db, init_db
from src.models.schema import PublishedArticle, SystemSettings, RSSFeed, CachedContent, PendingArticle, Thread, Message
from src.services.content_engine import ContentEngine
from src.services.validators import InputValidator, SecurityFlags, requires_api_key, validate_request_data

# Configuração de Assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)
if not os.path.exists(TEMPLATE_DIR): os.makedirs(TEMPLATE_DIR)

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
CORS(app)

# --- SECURITY CONFIGURATION ---
# 1. Rate Limiting (Prevention of Brute Force/DDoS)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# 2. Security Headers (CSP, HSTS, etc.)
# Using nonce to allow inline scripts safely. 'unsafe-inline' removed for strict security.
csp = {
    'default-src': '\'self\'',
    'script-src': ['\'self\'', 'https://cdn.jsdelivr.net'], # Bootstrap JS
    'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://fonts.googleapis.com', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'], # Bootstrap CSS, FontAwesome
    'font-src': ['\'self\'', 'https://fonts.gstatic.com', 'https://cdnjs.cloudflare.com'], # FontAwesome Webfonts
    'img-src': ['\'self\'', 'data:', 'https:'],
}

# Note: Report Only mode helps finding violations without breaking the app immediately.
# Switch content_security_policy_report_only to False when stable.
talisman = Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
    content_security_policy_report_only=False
)

logger = logging.getLogger(__name__)

# Estado Global
SYSTEM_STATE = "STOPPED"

# ==============================================================================
# FLASK ROUTES
# ==============================================================================

@app.route('/test')
def test():
    return render_template_string("""<!DOCTYPE html>
<html><head><title>TEST</title></head>
<body style='background:black;color:lime;font-size:30px;padding:50px;'>
<h1>✅ SERVER WORKING</h1>
<p>If you see this, the server is responding.</p>
<button onclick='alert("JS WORKS!")' style='font-size:20px;padding:20px;'>CLICK TO TEST JS</button>
<script nonce="{{ csp_nonce() }}">
document.body.innerHTML += '<p style="color:yellow;">✅ JAVASCRIPT EXECUTED</p>';
</script>
</body></html>""")

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename): 
    return send_from_directory(STATIC_DIR, filename)

import gc
from sqlalchemy import text

@app.route('/api/control', methods=['POST'])
def control():
    global SYSTEM_STATE
    action = request.json.get('action')
    if action == 'START': SYSTEM_STATE = 'RUNNING'
    elif action == 'PAUSE': SYSTEM_STATE = 'PAUSED'
    elif action == 'STOP': SYSTEM_STATE = 'STOPPED'
    elif action == 'OPTIMIZE':
        try:
            # 1. Memory Cleanup
            gc.collect()
            # 2. Database Vacuum (SQLite)
            db = get_db()
            db.execute(text("VACUUM"))
            db.close()
            logging.info("System manually optimized (GC + VACUUM).")
            return jsonify({'state': SYSTEM_STATE, 'message': 'System Optimized'})
        except Exception as e:
            logging.error(f"Optimization failed: {str(e)}")
            return jsonify({'state': SYSTEM_STATE, 'error': 'An internal error occurred during optimization'}), 500

    return jsonify({'state': SYSTEM_STATE})

@app.route('/api/stats')
def stats():
    db = get_db()
    try:
        total = db.query(PublishedArticle).count()
        today = db.query(PublishedArticle).filter(PublishedArticle.published_date >= datetime.now().date()).count()
        pending = db.query(PendingArticle).filter(PendingArticle.status == 'PENDING').count()
        cache = db.query(CachedContent).count()
        return jsonify({'total_articles': total, 'today': today, 'pending': pending, 'cache_count': cache})
    finally: db.close()

@app.route('/api/logs')
def logs():
    log_path = os.path.join(os.getcwd(), 'robot.log')
    try:
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                return jsonify({'logs': f.readlines()[-50:]})
        return jsonify({'logs': ['Log vazio.']})
    except: return jsonify({'logs': []})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    with open('robot.log', 'w') as f: f.write('')
    return jsonify({'success': True})

@app.route('/api/performance')
def performance():
    return jsonify({'cpu': psutil.cpu_percent(interval=0.1), 'ram': psutil.virtual_memory().percent, 'disk': psutil.disk_usage('/').percent})

@app.route('/api/performance/optimize', methods=['POST'])
def optimize():
    gc.collect()
    return jsonify({'success': True})

@app.route('/api/rss', methods=['GET'])
def get_rss():
    db = get_db(); feeds = db.query(RSSFeed).all()
    res = [{'id': f.id, 'name': f.name, 'url': f.url, 'is_active': f.is_active} for f in feeds]
    db.close(); return jsonify(res)

@app.route('/api/rss', methods=['POST'])
def add_rss():
    data = request.json; db = get_db()
    # FASE 1: THEME FIELD RESTORED
    db.add(RSSFeed(name=data.get('name'), url=data['url'], theme=data.get('theme', 'Geral')))
    db.commit(); db.close(); return jsonify({'success': True})

@app.route('/api/rss/<int:id>', methods=['DELETE'])
def delete_rss(id):
    db = get_db(); db.query(RSSFeed).filter(RSSFeed.id == id).delete(); db.commit(); db.close(); return jsonify({'success': True})

@app.route('/api/rss/delete_all', methods=['POST'])
def delete_all_rss():
    db = get_db(); db.query(RSSFeed).delete(); db.commit(); db.close(); return jsonify({'success': True})

@app.route('/api/rss/<int:id>/toggle', methods=['POST'])
def toggle_rss(id):
    db = get_db(); f = db.query(RSSFeed).filter(RSSFeed.id == id).first()
    if f: f.is_active = not f.is_active
    db.commit(); db.close(); return jsonify({'success': True})

@app.route('/api/settings', methods=['GET', 'POST'])
def settings_route():
    db = get_db()
    if request.method == 'GET':
        s = db.query(SystemSettings).all(); res = {k.key: k.value for k in s}; db.close(); return jsonify(res)
    else:
        for k, v in request.json.items():
             obj = db.query(SystemSettings).filter(SystemSettings.key == k).first()
             val_str = str(v).lower() if isinstance(v, bool) else str(v)
             if obj: obj.value = val_str
             else: db.add(SystemSettings(key=k, value=val_str))
        db.commit(); db.close(); return jsonify({'success': True})

@app.route('/api/evergreen', methods=['POST'])
@limiter.limit("5 per minute")
def evergreen():
    topic = request.json.get('topic')
    threading.Thread(target=lambda: ContentEngine().run_evergreen(topic)).start()
    return jsonify({'status': 'ok'})

# ==============================================================================
# NEW BACKEND CONTROL & SECURITY ENDPOINTS
# ==============================================================================
from src.services.deployment_service import DeploymentService

@app.route('/api/status/deployment')
def deployment_status():
    """Returns current environment status (DEV/PROD) and readiness."""
    env = os.getenv('FLASK_ENV', 'DEV').upper()
    try:
        is_ready = DeploymentService.prepare_build(env)
        return jsonify({'env': env, 'ready': is_ready, 'version': 'v8.3'})
        except Exception:
        logging.exception("Deployment status check failed for env %s", env)
        return jsonify({'env': env, 'ready': False, 'error': 'Internal deployment status check failed'})
        return jsonify({'env': env, 'ready': False, 'error': 'Internal deployment status check failed'})

@app.route('/api/providers/toggle', methods=['POST'])
@validate_request_data({'provider': str, 'enabled': bool})
def toggle_provider():
    """
    Enable/disable news API providers with validation.
    Checks if API key exists before allowing activation.
    """
    data = request.json
    provider = data['provider']
    enabled = data['enabled']
    
    # Map provider names to their API key settings
    provider_key_map = {
        'gnews': 'gnews_api_key',
        'newsapi': 'newsapi_key',
        'currents': 'currents_api_key'
    }
    
    if provider not in provider_key_map:
        return jsonify({
            'success': False,
            'error': f'Unknown provider: {provider}'
        }), 400
    
    db = get_db()
    try:
        # If enabling, validate API key exists and is valid
        if enabled:
            key_setting = provider_key_map[provider]
            setting = db.query(SystemSettings).filter(
                SystemSettings.key == key_setting
            ).first()
            
            api_key = setting.value if setting else None
            
            if not api_key or api_key.strip() == "":
                return jsonify({
                    'success': False,
                    'error': f'{provider.upper()} API key not configured',
                    'blocked': True
                }), 403
            
            # Validate format
            is_valid, error = InputValidator.validate_api_key(api_key, provider)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error,
                    'blocked': True
                }), 403
        
        # Update provider state
        provider_state_key = f'enable_{provider}'
        state_setting = db.query(SystemSettings).filter(
            SystemSettings.key == provider_state_key
        ).first()
        
        if state_setting:
            state_setting.value = str(enabled).lower()
        else:
            db.add(SystemSettings(key=provider_state_key, value=str(enabled).lower()))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'provider': provider,
            'enabled': enabled
        })
    finally:
        db.close()


@app.route('/api/cycle/adjust', methods=['POST'])
@validate_request_data({'minutes': (int, float)})
def adjust_cycle():
    """
    Adjust the interval between content generation cycles.
    Validates against min/max limits (30 min - 24 hours).
    """
    data = request.json
    minutes = int(data['minutes'])
    
    # Validate interval
    is_valid, error = InputValidator.validate_cycle_interval(minutes)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    db = get_db()
    try:
        # Update cycle interval setting
        setting = db.query(SystemSettings).filter(
            SystemSettings.key == 'cycle_interval_minutes'
        ).first()
        
        if setting:
            setting.value = str(minutes)
        else:
            db.add(SystemSettings(key='cycle_interval_minutes', value=str(minutes)))
        
        db.commit()
        
        logger.info(f"✅ Cycle interval adjusted to {minutes} minutes")
        
        return jsonify({
            'success': True,
            'interval_minutes': minutes,
            'interval_hours': round(minutes / 60, 2),
            'message': f'Cycle interval set to {minutes} minutes'
        })
    finally:
        db.close()


@app.route('/api/categories/audit', methods=['POST'])
def audit_categories():
    """
    Scan news APIs for available categories and auto-add missing ones.
    This helps keep the UI dropdowns up-to-date with provider capabilities.
    """
    import requests
    
    discovered_categories = {
        'gnews': [],
        'newsapi': [],
        'currents': []
    }
    
    db = get_db()
    try:
        # GNews categories (from documentation)
        discovered_categories['gnews'] = [
            'general', 'world', 'nation', 'business', 
            'technology', 'entertainment', 'sports', 
            'science', 'health'
        ]
        
        # NewsAPI categories (from documentation)
        discovered_categories['newsapi'] = [
            'business', 'entertainment', 'general', 
            'health', 'science', 'sports', 'technology'
        ]
        
        # Currents categories (from documentation)
        discovered_categories['currents'] = [
            'regional', 'technology', 'lifestyle', 
            'business', 'general', 'programming', 
            'science', 'entertainment', 'world', 
            'sports', 'finance', 'academia', 
            'politics', 'health', 'opinion', 'food'
        ]
        
        # Get current categories from database
        for provider in ['gnews', 'newsapi', 'currents']:
            key = f'{provider}_categories'
            setting = db.query(SystemSettings).filter(
                SystemSettings.key == key
            ).first()
            
            current_cats = []
            if setting and setting.value:
                try:
                    import json
                    current_cats = json.loads(setting.value)
                except:
                    current_cats = []
            
            # Merge with discovered categories
            all_cats = list(set(current_cats + discovered_categories[provider]))
            
            # Update database
            if setting:
                setting.value = json.dumps(all_cats)
            else:
                db.add(SystemSettings(key=key, value=json.dumps(all_cats)))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'discovered': discovered_categories,
            'message': 'Category audit completed'
        })
    except Exception as e:
        logger.error(f"Category audit failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()


@app.route('/api/security/validate', methods=['POST'])
@validate_request_data({'field': str, 'value': str, 'type': str})
def validate_input():
    """
    Validate user inputs against security patterns.
    Sets security flags if validation fails.
    """
    data = request.json
    field = data['field']
    value = data['value']
    input_type = data['type']
    
    session_id = request.remote_addr  # Simple session tracking
    
    # Clear previous alerts for this field
    SecurityFlags.clear_alert(session_id, field)
    
    is_valid = True
    error_message = None
    
    # Validate based on type
    if input_type == 'api_key':
        is_valid, error_message = InputValidator.validate_api_key(value)
    elif input_type == 'url':
        is_valid, error_message = InputValidator.validate_url(value)
    elif input_type == 'username':
        is_valid, error_message = InputValidator.validate_username(value)
    elif input_type == 'feed_name':
        is_valid, error_message = InputValidator.validate_feed_name(value)
    else:
        return jsonify({
            'success': False,
            'error': f'Unknown validation type: {input_type}'
        }), 400
    
    if not is_valid:
        SecurityFlags.set_alert(session_id, field, error_message)
    
    return jsonify({
        'valid': is_valid,
        'error': error_message,
        'has_alerts': SecurityFlags.has_alerts(session_id)
    })


@app.route('/api/security/events', methods=['POST'])
@validate_request_data({'event': str, 'field': str})
def security_event():
    """
    Track security-relevant events (clipboard, paste, etc).
    Sets flags for suspicious activity.
    """
    data = request.json
    event = data['event']
    field = data['field']
    
    session_id = request.remote_addr
    
    # Sensitive fields that should trigger alerts on clipboard events
    sensitive_fields = [
        'google_api_key', 'youtube_api_key', 'wordpress_password',
        'gnews_api_key', 'newsapi_key', 'currents_api_key'
    ]
    
    if field in sensitive_fields and event in ['paste', 'copy']:
        SecurityFlags.set_alert(
            session_id, 
            field, 
            f'Clipboard {event} detected on sensitive field'
        )
        
        logger.warning(f"⚠️ Security: {event} event on {field} from {session_id}")
    
    return jsonify({
        'success': True,
        'event_logged': True,
        'has_alerts': SecurityFlags.has_alerts(session_id)
    })


@app.route('/api/security/alerts', methods=['GET'])
def get_security_alerts():
    """Get all active security alerts for the current session."""
    session_id = request.remote_addr
    alerts = SecurityFlags.get_alerts(session_id)
    
    return jsonify({
        'has_alerts': SecurityFlags.has_alerts(session_id),
        'alerts': alerts
    })


@app.route('/api/history/<session_id>', methods=['GET'])
def get_history_detail(session_id):
    """Retorna histórico completo de uma sessão (Thread + Messages)."""
    db = get_db()
    try:
        thread = db.query(Thread).filter(Thread.session_id == session_id).first()
        if not thread:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
            
        messages = db.query(Message).filter(Message.thread_id == thread.id).order_by(Message.timestamp).all()
        
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
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@app.route('/api/history', methods=['GET', 'DELETE'])
def get_history_list():
    """
    GET: Retorna lista de sessões (Threads).
    DELETE: Apaga todo o histórico (Threads e Matches).
    """
    db = get_db()
    try:
        if request.method == 'DELETE':
            # SQLite ON DELETE CASCADE should handle messages if configured, 
            # otherwise we manually delete.
            # Assuming models are CASCADE compliant or we just delete threads.
            num = db.query(Thread).delete()
            db.commit()
            return jsonify({'success': True, 'count': num})

        # GET Handling
        # Grouping logic ideal here (Today, Yesterday, etc) but simple list first

        threads = db.query(Thread).order_by(Thread.created_at.desc()).limit(50).all()
        return jsonify({
            'success': True,
            'threads': [
                {
                    'id': t.id,
                    'session_id': t.session_id,
                    'title': t.title,
                    'date': t.created_at.strftime("%Y-%m-%d %H:%M"),
                    'status': t.status
                } for t in threads
            ]
        })
    finally:
        db.close()

@app.route('/api/model', methods=['GET', 'POST'])
def model_config():
    """Get or Set current AI Model Mode (Pro vs Flash)."""
    db = get_db()
    try:
        if request.method == 'POST':
            data = request.json
            mode = data.get('mode', 'pro').lower()
            if mode not in ['pro', 'flash']:
                return jsonify({'success': False, 'error': 'Invalid mode'}), 400
            
            # Save to DB
            s = db.query(SystemSettings).filter_by(key='ai_model_mode').first()
            if s:
                s.value = mode
            else:
                db.add(SystemSettings(key='ai_model_mode', value=mode))
            db.commit()
            
            # Force Reload of AI Client in Content Engine?
            # Ideally we restart service or reloading happens on next use.
            # Since AIService is inside ContentEngine instance in main.py...
            # But the dashboard runs in a separate process or same?
            # dashboard_app.py imports ContentEngine class but doesn't instantiate the global robot.
            # However, for the 'Chat' feature (if implemented via AIService here), we need to reload.
            # We don't have a global aiservice instance exposed here easily. 
            # But ModelFactory reads DB every time `create_client` is called.
            # So if we instantiate a new client, it picks up the change.
            
            return jsonify({'success': True, 'mode': mode})
            
        else:
            # GET
            s = db.query(SystemSettings).filter_by(key='ai_model_mode').first()
            mode = s.value if s else os.getenv('AI_MODEL_TYPE', 'pro')
            return jsonify({'success': True, 'mode': mode})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()

# Review System Routes
@app.route('/api/pending')
def get_pending():
    db = get_db()
    items = db.query(PendingArticle).filter(PendingArticle.status == 'PENDING').all()
    res = [{'id': i.id, 'title': i.title, 'source': i.source_name, 'content': i.content_json, 'date': i.created_at.strftime('%Y-%m-%d %H:%M'), 'image': i.image_path} for i in items]
    db.close()
    return jsonify(res)

@app.route('/api/approve', methods=['POST'])
def approve_pending():
    data = request.json
    db = get_db()
    try:
        pend = db.query(PendingArticle).filter(PendingArticle.id == data['id']).first()
        if pend:
            content = json.loads(pend.content_json)
            content['conteudo_completo'] = data.get('content', content['conteudo_completo'])
            
            # WP Publish Mode Logic
            s = db.query(SystemSettings).filter_by(key='wp_publish_mode').first()
            status = s.value if s else 'publish'
            
            # Create Published Record
            pub = PublishedArticle(
                hash=hashlib.md5(pend.original_url.encode()).hexdigest(),
                title=pend.title,
                full_content=content['conteudo_completo'],
                source=pend.source_name,
                published_date=datetime.now(),
                wordpress_url=f"wp_{status}_approved_{int(time.time())}"
            )
            db.add(pub)
            pend.status = 'APPROVED'
            db.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Not found'}), 404
    except Exception as e:
        logger.error(f"Approval error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    finally:
        db.close()

@app.route('/api/reject', methods=['POST'])
def reject_pending():
    db = get_db()
    try:
        db.query(PendingArticle).filter(PendingArticle.id == request.json['id']).update({'status': 'REJECTED'})
        db.commit()
        return jsonify({'success': True})
    finally:
        db.close()

@app.route('/api/gemini/validate', methods=['POST'])
@limiter.limit("10 per minute")
def gemini_validate():
    """
    Validates Gemini API Key and fetches available models.
    Filters for 'generateContent' capability.
    """
    data = request.json
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'success': False, 'error': 'Missing API Key'}), 400

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        import requests
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            models_data = resp.json().get('models', [])
            # Filter for models that support content generation
            valid_models = []
            for m in models_data:
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods:
                    # Clean name (remove 'models/' prefix)
                    name = m['name'].replace('models/', '')
                    valid_models.append(name)
            
            # Sort with preference for 1.5-flash and 1.5-pro
            valid_models.sort(key=lambda x: (
                0 if 'flash' in x else 
                1 if 'pro' in x else 
                2
            ))
            
            return jsonify({'success': True, 'models': valid_models})
        else:
            return jsonify({'success': False, 'error': f"Google API Error: {resp.status_code}"}), resp.status_code
            
    except Exception as e:
        logger.error(f"Gemini Validation Error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error while validating Gemini API key'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
