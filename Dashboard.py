"""
Dashboard Web para Content Robot v4.0
- ✅ Estatísticas de Cache
- ✅ Sistema de Otimização
- ✅ Limpeza Integrada
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.INFO)
import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_models import PublishedArticle, APIUsageLog, Base
from cache_manager import CacheManager
from system_optimizer import SystemOptimizer
import json

app = Flask(__name__)
CORS(app)

engine = create_engine('sqlite:///content_robot.db')
Session = sessionmaker(bind=engine)

# 🆕 Instanciar gerenciadores
cache_manager = CacheManager()
system_optimizer = SystemOptimizer()

@app.route('/')
def index():
    """Página principal do dashboard"""
    return DASHBOARD_HTML

# ========== ROTAS EXISTENTES (manter) ==========

@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas gerais"""
    session = Session()
    
    try:
        total = session.query(PublishedArticle).count()
        
        last_7_days = session.query(PublishedArticle).filter(
            PublishedArticle.published_date >= datetime.now() - timedelta(days=7)
        ).count()
        
        today = session.query(PublishedArticle).filter(
            PublishedArticle.published_date >= datetime.now().date()
        ).count()
        
        avg_quality = session.query(func.avg(PublishedArticle.quality_score)).scalar() or 0
        avg_originality = session.query(func.avg(PublishedArticle.originality_score)).scalar() or 0
        
        api_today = session.query(APIUsageLog).filter(
            APIUsageLog.date >= datetime.now().date()
        ).all()
        
        api_calls = sum(log.calls for log in api_today)
        api_tokens = sum(log.tokens_used for log in api_today)
        
        return jsonify({
            'total_articles': total,
            'today': today,
            'last_7_days': last_7_days,
            'avg_quality': round(avg_quality, 1),
            'avg_originality': round(avg_originality, 1),
            'api_calls_today': api_calls,
            'api_tokens_today': api_tokens
        })
        
    finally:
        session.close()

@app.route('/api/recent-articles')
def get_recent_articles():
    """Retorna últimos artigos publicados"""
    session = Session()
    
    try:
        articles = session.query(PublishedArticle).order_by(
            PublishedArticle.published_date.desc()
        ).limit(10).all()
        
        return jsonify([{
            'id': article.id,
            'title': article.title,
            'source': article.source,
            'published_date': article.published_date.strftime('%Y-%m-%d %H:%M'),
            'quality_score': article.quality_score,
            'originality_score': article.originality_score,
            'wordpress_url': article.wordpress_url
        } for article in articles])
        
    finally:
        session.close()

# ========== 🆕 NOVAS ROTAS v4.0 ==========

@app.route('/api/cache-stats')
def get_cache_stats():
    """Retorna estatísticas do cache"""
    try:
        stats = cache_manager.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-health')
def get_system_health():
    """Retorna saúde do sistema"""
    try:
        health = system_optimizer.get_system_health()
        return jsonify(health)
    except Exception as e:
        logging.exception("Error in get_system_health")
        return jsonify({'error': 'Ocorreu um erro interno.'}), 500

@app.route('/api/optimization-recommendations')
def get_optimization_recommendations():
    """Retorna recomendações de otimização"""
    try:
        recs = system_optimizer.get_optimization_recommendations()
        return jsonify(recs)
    except Exception as e:
        logging.exception("Error in get_optimization_recommendations")
        return jsonify({'error': 'Ocorreu um erro interno.'}), 500

@app.route('/api/cleanup/cache', methods=['POST'])
def cleanup_cache():
    """Limpa cache expirado"""
    try:
        deleted = cache_manager.clean_expired_cache()
        return jsonify({
            'success': True,
            'deleted': deleted
        })
    except Exception as e:
        logging.exception("Error in cleanup_cache")
        return jsonify({'error': 'Ocorreu um erro interno.'}), 500

@app.route('/api/cleanup/full', methods=['POST'])
def full_cleanup():
    """Limpeza completa do sistema"""
    try:
        aggressive = request.json.get('aggressive', False)
        result = system_optimizer.full_cleanup(aggressive)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logging.exception("Error in full_cleanup")
        return jsonify({'error': 'Ocorreu um erro interno.'}), 500

@app.route('/api/logs')
def get_logs():
    """Retorna últimas linhas do log"""
    try:
        with open('robot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_50 = lines[-50:]
            return jsonify({'logs': last_50})
    except Exception as e:
        logging.exception("Erro ao ler logs")
        return jsonify({'logs': ['Erro ao ler logs: Ocorreu um erro interno.']})

# ========== HTML DO DASHBOARD v4.0 ==========

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Content Robot v4.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            margin-right: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-warning {
            background: #ffc107;
            color: #333;
        }
        
        .recommendation {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .recommendation.critical {
            background: #ffebee;
            border-color: #f44336;
        }
        
        .recommendation.warning {
            background: #fff3e0;
            border-color: #ff9800;
        }
        
        .recommendation.info {
            background: #e3f2fd;
            border-color: #2196f3;
        }
        
        .recommendation.success {
            background: #e8f5e9;
            border-color: #4caf50;
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }
        
        .articles-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .article-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .article-item:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard - Content Robot v4.0</h1>
            <p>Monitoramento e Otimização do Sistema</p>
        </div>
        
        <!-- Estatísticas Principais -->
        <div class="stats-grid" id="mainStats">
            <div class="stat-card">
                <h3>Total de Artigos</h3>
                <div class="value" id="totalArticles">-</div>
            </div>
            <div class="stat-card">
                <h3>Hoje</h3>
                <div class="value" id="todayArticles">-</div>
            </div>
            <div class="stat-card">
                <h3>Últimos 7 Dias</h3>
                <div class="value" id="last7Days">-</div>
            </div>
            <div class="stat-card">
                <h3>Qualidade Média</h3>
                <div class="value" id="avgQuality">-</div>
            </div>
        </div>
        
        <!-- Cache Stats -->
        <div class="section">
            <h2>⚡ Estatísticas de Cache</h2>
            <div class="stats-grid" id="cacheStats">
                <div class="stat-card">
                    <h3>Conteúdos em Cache</h3>
                    <div class="value" id="contentCached">-</div>
                </div>
                <div class="stat-card">
                    <h3>Tamanho do Cache</h3>
                    <div class="value" id="cacheSize">-</div>
                    <small>MB</small>
                </div>
                <div class="stat-card">
                    <h3>Taxa de Hit</h3>
                    <div class="value" id="cacheHitRate">-</div>
                    <small>%</small>
                </div>
                <div class="stat-card">
                    <h3>Chamadas Economizadas</h3>
                    <div class="value" id="savedCalls">-</div>
                </div>
            </div>
        </div>
        
        <!-- System Health -->
        <div class="section">
            <h2>💻 Saúde do Sistema</h2>
            <div id="systemHealth">
                <p>CPU: <span id="cpuUsage">-</span>%</p>
                <div class="progress-bar"><div class="progress-bar-fill" id="cpuBar"></div></div>
                
                <p style="margin-top:15px">Memória: <span id="memoryUsage">-</span>%</p>
                <div class="progress-bar"><div class="progress-bar-fill" id="memoryBar"></div></div>
                
                <p style="margin-top:15px">Disco: <span id="diskUsage">-</span>% (<span id="diskFree">-</span> GB livres)</p>
                <div class="progress-bar"><div class="progress-bar-fill" id="diskBar"></div></div>
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="section">
            <h2>💡 Recomendações de Otimização</h2>
            <div id="recommendations">
                <p>Carregando...</p>
            </div>
        </div>
        
        <!-- Cleanup Actions -->
        <div class="section">
            <h2>🧹 Ferramentas de Limpeza</h2>
            <button class="btn btn-primary" onclick="cleanupCache()">🗑️ Limpar Cache Expirado</button>
            <button class="btn btn-warning" onclick="fullCleanup(false)">🧽 Limpeza Normal</button>
            <button class="btn btn-danger" onclick="fullCleanup(true)">⚠️ Limpeza Agressiva</button>
        </div>
        
        <!-- Recent Articles -->
        <div class="section">
            <h2>📝 Últimos Artigos</h2>
            <div class="articles-list" id="recentArticles">
                <p>Carregando...</p>
            </div>
        </div>
    </div>
    
    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalArticles').textContent = stats.total_articles;
                document.getElementById('todayArticles').textContent = stats.today;
                document.getElementById('last7Days').textContent = stats.last_7_days;
                document.getElementById('avgQuality').textContent = stats.avg_quality;
            } catch (error) {
                console.error('Erro ao carregar stats:', error);
            }
        }
        
        async function loadCacheStats() {
            try {
                const response = await fetch('/api/cache-stats');
                const stats = await response.json();
                
                document.getElementById('contentCached').textContent = stats.content_cached || 0;
                document.getElementById('cacheSize').textContent = stats.cache_size_mb || 0;
                document.getElementById('cacheHitRate').textContent = stats.content_hit_rate || 0;
                document.getElementById('savedCalls').textContent = stats.storage_saved_calls || 0;
            } catch (error) {
                console.error('Erro ao carregar cache stats:', error);
            }
        }
        
        async function loadSystemHealth() {
            try {
                const response = await fetch('/api/system-health');
                const health = await response.json();
                
                document.getElementById('cpuUsage').textContent = health.cpu_percent.toFixed(1);
                document.getElementById('cpuBar').style.width = health.cpu_percent + '%';
                
                document.getElementById('memoryUsage').textContent = health.memory_percent.toFixed(1);
                document.getElementById('memoryBar').style.width = health.memory_percent + '%';
                
                document.getElementById('diskUsage').textContent = health.disk_percent.toFixed(1);
                document.getElementById('diskFree').textContent = health.disk_free_gb;
                document.getElementById('diskBar').style.width = health.disk_percent + '%';
            } catch (error) {
                console.error('Erro ao carregar system health:', error);
            }
        }
        
        async function loadRecommendations() {
            try {
                const response = await fetch('/api/optimization-recommendations');
                const recs = await response.json();
                
                const container = document.getElementById('recommendations');
                container.innerHTML = recs.map(rec => `
                    <div class="recommendation ${rec.severity}">
                        ${rec.message}
                    </div>
                `).join('');
            } catch (error) {
                console.error('Erro ao carregar recomendações:', error);
            }
        }
        
        async function loadRecentArticles() {
            try {
                const response = await fetch('/api/recent-articles');
                const articles = await response.json();
                
                const container = document.getElementById('recentArticles');
                container.innerHTML = articles.map(article => `
                    <div class="article-item">
                        <strong>${article.title}</strong><br>
                        <small>${article.source} | ${article.published_date}</small><br>
                        <small>Qualidade: ${article.quality_score}/100</small>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Erro ao carregar artigos:', error);
            }
        }
        
        async function cleanupCache() {
            if (!confirm('Limpar cache expirado?')) return;
            
            try {
                const response = await fetch('/api/cleanup/cache', { method: 'POST' });
                const result = await response.json();
                
                alert(`✅ Cache limpo! ${JSON.stringify(result.deleted)} itens removidos`);
                loadCacheStats();
            } catch (error) {
                alert('❌ Erro ao limpar cache: ' + error.message);
            }
        }
        
        async function fullCleanup(aggressive) {
            const msg = aggressive ? 
                'LIMPEZA AGRESSIVA remove mais dados. Continuar?' : 
                'Executar limpeza normal?';
            
            if (!confirm(msg)) return;
            
            try {
                const response = await fetch('/api/cleanup/full', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({aggressive})
                });
                
                const result = await response.json();
                
                alert(`✅ Limpeza concluída!\\n${result.result.freed_mb.toFixed(2)} MB liberados`);
                
                loadStats();
                loadCacheStats();
                loadSystemHealth();
            } catch (error) {
                alert('❌ Erro na limpeza: ' + error.message);
            }
        }
        
        // Carregar dados iniciais
        loadStats();
        loadCacheStats();
        loadSystemHealth();
        loadRecommendations();
        loadRecentArticles();
        
        // Auto-refresh a cada 30 segundos
        setInterval(() => {
            loadStats();
            loadCacheStats();
            loadSystemHealth();
        }, 30000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║   📊 DASHBOARD v4.0                      ║
    ║                                          ║
    ║   🌐 Dashboard: http://localhost:5000    ║
    ║   🔄 Auto-refresh: 30 segundos           ║
    ║                                          ║
    ║   Pressione Ctrl+C para parar           ║
    ╚══════════════════════════════════════════╝
    """)
    
    app.run(debug=False, host='0.0.0.0', port=5000)