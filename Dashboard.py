"""
Dashboard Web para Content Robot v5.0 (FINAL)
- ✅ Monitoramento em Tempo Real
- ✅ Gestão de Configurações (Settings)
- ✅ Controle de Cache e Limpeza
"""
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Modelos
from database_models import PublishedArticle, APIUsageLog, Base, SystemSettings
from cache_manager import CacheManager
from system_optimizer import SystemOptimizer

app = Flask(__name__)
CORS(app)

# Configuração do Banco
engine = create_engine('sqlite:///content_robot.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)

# Gerenciadores
cache_manager = CacheManager()
system_optimizer = SystemOptimizer()

# ============================================
# ROTAS DA INTERFACE (HTML)
# ============================================
@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

# ============================================
# API: ESTATÍSTICAS E DADOS (LEITURA)
# ============================================
@app.route('/api/stats')
def get_stats():
    session = Session()
    try:
        total = session.query(PublishedArticle).count()
        last_7 = session.query(PublishedArticle).filter(PublishedArticle.published_date >= datetime.now() - timedelta(days=7)).count()
        today = session.query(PublishedArticle).filter(PublishedArticle.published_date >= datetime.now().date()).count()
        
        avg_qual = session.query(func.avg(PublishedArticle.quality_score)).scalar() or 0
        
        return jsonify({
            'total_articles': total,
            'today': today,
            'last_7_days': last_7,
            'avg_quality': round(avg_qual, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/recent-articles')
def get_recent_articles():
    session = Session()
    try:
        articles = session.query(PublishedArticle).order_by(PublishedArticle.published_date.desc()).limit(10).all()
        return jsonify([{
            'id': a.id, 'title': a.title, 'source': a.source,
            'published_date': a.published_date.strftime('%d/%m %H:%M'),
            'quality_score': a.quality_score, 'wordpress_url': a.wordpress_url
        } for a in articles])
    finally:
        session.close()

@app.route('/api/cache-stats')
def get_cache_stats():
    return jsonify(cache_manager.get_cache_stats())

@app.route('/api/system-health')
def get_system_health():
    return jsonify(system_optimizer.get_system_health())

@app.route('/api/logs')
def get_logs():
    try:
        if os.path.exists('robot.log'):
            with open('robot.log', 'r', encoding='utf-8') as f:
                return jsonify({'logs': f.readlines()[-50:]})
        return jsonify({'logs': ['Arquivo de log não encontrado.']})
    except:
        return jsonify({'logs': ['Erro ao ler logs.']})

# ============================================
# 🆕 API: SETTINGS (CONFIGURAÇÕES)
# ============================================
@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Retorna todas as configurações do banco"""
    session = Session()
    try:
        settings = session.query(SystemSettings).all()
        return jsonify({s.key: s.value for s in settings})
    finally:
        session.close()

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Atualiza configurações"""
    data = request.json
    session = Session()
    try:
        for key, value in data.items():
            setting = session.query(SystemSettings).filter_by(key=key).first()
            if setting:
                setting.value = str(value)
                setting.updated_at = datetime.now()
            else:
                # Cria se não existir (segurança para novas chaves)
                new_setting = SystemSettings(key=key, value=str(value), description="Criado via Dashboard")
                session.add(new_setting)
        
        session.commit()
        return jsonify({'success': True, 'message': 'Configurações salvas com sucesso!'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

# ============================================
# API: AÇÕES DE LIMPEZA
# ============================================
@app.route('/api/cleanup/cache', methods=['POST'])
def cleanup_cache():
    return jsonify(cache_manager.clean_expired_cache())

@app.route('/api/cleanup/full', methods=['POST'])
def full_cleanup():
    aggressive = request.json.get('aggressive', False)
    return jsonify(system_optimizer.full_cleanup(aggressive))

# ============================================
# FRONTEND: SINGLE PAGE APPLICATION
# ============================================
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Robot v5.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --primary: #667eea; --secondary: #764ba2; --bg: #f4f6f9; }
        body { background-color: var(--bg); font-family: 'Segoe UI', sans-serif; }
        .sidebar { background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%); min-height: 100vh; color: white; padding: 20px; }
        .nav-link { color: rgba(255,255,255,0.8); margin-bottom: 10px; border-radius: 8px; cursor: pointer; }
        .nav-link:hover, .nav-link.active { background: rgba(255,255,255,0.2); color: white; }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .stat-val { font-size: 2rem; font-weight: bold; color: var(--secondary); }
        .log-box { background: #1e1e1e; color: #0f0; font-family: monospace; padding: 15px; border-radius: 8px; height: 300px; overflow-y: auto; font-size: 0.85rem; }
        .settings-section { display: none; }
        .settings-section.active { display: block; }
        .btn-primary { background-color: var(--primary); border-color: var(--primary); }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar">
                <h3 class="mb-4">🤖 Robot v5.0</h3>
                <nav class="nav flex-column">
                    <a class="nav-link active" onclick="showTab('dashboard')">📊 Monitoramento</a>
                    <a class="nav-link" onclick="showTab('settings')">⚙️ Configurações</a>
                    <a class="nav-link" href="http://localhost:5001" target="_blank">✅ Aprovações</a>
                </nav>
            </div>

            <div class="col-md-10 p-4">
                
                <div id="tab-dashboard" class="settings-section active">
                    <h2 class="mb-4">Monitoramento em Tempo Real</h2>
                    
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card p-3">
                                <small class="text-muted">Total Artigos</small>
                                <div class="stat-val" id="totalArticles">-</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3">
                                <small class="text-muted">Hoje</small>
                                <div class="stat-val" id="todayArticles">-</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3">
                                <small class="text-muted">Qualidade Média</small>
                                <div class="stat-val" id="avgQuality">-</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card p-3">
                                <small class="text-muted">Cache Hit Rate</small>
                                <div class="stat-val" id="cacheHit">-</div>
                            </div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-header bg-white">📋 Logs do Sistema</div>
                                <div class="card-body">
                                    <div class="log-box" id="logBox">Carregando logs...</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="card mb-3">
                                <div class="card-header bg-white">💻 Saúde do Sistema</div>
                                <div class="card-body">
                                    <p>CPU: <span id="cpuVal">-</span>%</p>
                                    <div class="progress mb-3" style="height: 5px;"><div class="progress-bar" id="cpuBar" style="width: 0%"></div></div>
                                    <p>Memória: <span id="memVal">-</span>%</p>
                                    <div class="progress mb-3" style="height: 5px;"><div class="progress-bar" id="memBar" style="width: 0%"></div></div>
                                    <p>Disco Livre: <span id="diskVal">-</span> GB</p>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-header bg-white">🧹 Manutenção</div>
                                <div class="card-body d-grid gap-2">
                                    <button class="btn btn-outline-primary btn-sm" onclick="cleanCache()">Limpar Cache</button>
                                    <button class="btn btn-outline-danger btn-sm" onclick="fullClean()">Limpeza Completa</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="tab-settings" class="settings-section">
                    <h2 class="mb-4">⚙️ Configurações do Sistema</h2>
                    <form id="settingsForm">
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card mb-4">
                                    <div class="card-header bg-white fw-bold">🔐 WordPress & APIs</div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <label class="form-label">URL do Blog</label>
                                            <input type="text" class="form-control" name="wordpress_url">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Usuário WP</label>
                                            <input type="text" class="form-control" name="wordpress_username">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Application Password</label>
                                            <input type="password" class="form-control" name="wordpress_password">
                                        </div>
                                        <hr>
                                        <div class="mb-3">
                                            <label class="form-label">YouTube API Key</label>
                                            <input type="password" class="form-control" name="youtube_api_key">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Stability AI Key</label>
                                            <input type="password" class="form-control" name="stability_api_key">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="card mb-4">
                                    <div class="card-header bg-white fw-bold">🚀 Operacional & IA</div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <label class="form-label text-danger">Limite de Artigos (Segurança)</label>
                                            <input type="number" class="form-control" name="max_articles_cycle">
                                            <div class="form-text">Máximo de posts por ciclo para evitar bloqueios.</div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Intervalo (minutos)</label>
                                            <input type="number" class="form-control" name="check_interval_minutes">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Estilo de Imagem (Prompt)</label>
                                            <textarea class="form-control" name="image_prompt_style" rows="2"></textarea>
                                        </div>
                                        <div class="mb-3 form-check">
                                            <input type="checkbox" class="form-check-input" id="chk_approval" name="require_manual_approval">
                                            <label class="form-check-label" for="chk_approval">Exigir Aprovação Manual</label>
                                        </div>
                                        <div class="mb-3 form-check">
                                            <input type="checkbox" class="form-check-input" id="chk_img" name="generate_images">
                                            <label class="form-check-label" for="chk_img">Gerar Imagens com IA</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="d-flex justify-content-end">
                            <button type="button" class="btn btn-primary btn-lg" onclick="saveSettings()">💾 Salvar Alterações</button>
                        </div>
                    </form>
                </div>

            </div>
        </div>
    </div>

    <script>
        // Navegação
        function showTab(tabName) {
            document.querySelectorAll('.settings-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            
            // Atualiza active na sidebar (simplificado)
            event.target.classList.add('active');
            
            if(tabName === 'settings') loadSettings();
        }

        // Dashboard Data
        async function loadDashboard() {
            // Stats
            const s = await (await fetch('/api/stats')).json();
            document.getElementById('totalArticles').innerText = s.total_articles;
            document.getElementById('todayArticles').innerText = s.today;
            document.getElementById('avgQuality').innerText = s.avg_quality;

            // Cache
            const c = await (await fetch('/api/cache-stats')).json();
            document.getElementById('cacheHit').innerText = c.content_hit_rate + '%';

            // Logs
            const l = await (await fetch('/api/logs')).json();
            document.getElementById('logBox').innerHTML = l.logs.map(line => `<div>${line}</div>`).join('');
            
            // Health
            const h = await (await fetch('/api/system-health')).json();
            document.getElementById('cpuVal').innerText = h.cpu_percent;
            document.getElementById('cpuBar').style.width = h.cpu_percent + '%';
            document.getElementById('memVal').innerText = h.memory_percent;
            document.getElementById('memBar').style.width = h.memory_percent + '%';
            document.getElementById('diskVal').innerText = h.disk_free_gb;
        }

        // Settings Logic
        async function loadSettings() {
            try {
                const data = await (await fetch('/api/settings')).json();
                const form = document.getElementById('settingsForm');
                
                for (const [key, value] of Object.entries(data)) {
                    const input = form.elements[key];
                    if (input) {
                        if (input.type === 'checkbox') {
                            input.checked = (value.toLowerCase() === 'true');
                        } else {
                            input.value = value;
                        }
                    }
                }
            } catch (e) { console.error("Erro ao carregar settings", e); }
        }

        async function saveSettings() {
            const form = document.getElementById('settingsForm');
            const formData = new FormData(form);
            const data = {};
            
            // Tratamento especial para checkboxes (que não enviam 'false' se desmarcados)
            const checkboxes = ['require_manual_approval', 'generate_images'];
            
            for (const [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            checkboxes.forEach(chk => {
                data[chk] = form.elements[chk].checked;
            });

            if(!confirm('Deseja aplicar estas alterações? O robô lerá as novas configs no próximo ciclo.')) return;

            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if(result.success) alert('✅ Configurações salvas!');
                else alert('❌ Erro: ' + result.error);
            } catch (e) { alert('❌ Erro de conexão'); }
        }

        async function cleanCache() {
            if(confirm('Limpar cache expirado?')) {
                await fetch('/api/cleanup/cache', {method: 'POST'});
                alert('Cache limpo!');
                loadDashboard();
            }
        }
        
        async function fullClean() {
            if(confirm('ATENÇÃO: Limpeza profunda. Continuar?')) {
                await fetch('/api/cleanup/full', {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({aggressive: true})
                });
                alert('Sistema otimizado!');
                loadDashboard();
            }
        }

        // Init
        loadDashboard();
        setInterval(loadDashboard, 10000); // Refresh a cada 10s
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Dashboard v5.0 rodando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)