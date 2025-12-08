"""
S1M0N Dashboard v8.2 - Stability & i18n Release
Phases: 1 (Structure Restoration), 2 (Contrast/UI), 3 (Deep i18n)
"""
import os
import json
import logging
import threading
import psutil
import gc
import time
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_cors import CORS

# Imports da Arquitetura
from src.config.database import get_db, init_db
from src.models.schema import PublishedArticle, SystemSettings, RSSFeed, CachedContent, PendingArticle
from src.services.content_engine import ContentEngine

# Configuração de Assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)

# Estado Global
SYSTEM_STATE = "STOPPED"

# ==============================================================================
# HTML TEMPLATE (FULL STACK UI v8.2)
# ==============================================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S1M0N - Automation Core</title>
    <link rel="icon" type="image/png" href="/static/logo.png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* --- 1. THEME VARIABLES --- */
        :root {
            --primary: #FF6B6B;
            --primary-hover: #ee5253;
            --bg-body: #f4f6f9;
            --bg-card: #ffffff;
            --text-main: #333333;
            --text-sec: #6c757d;
            --border: #e0e0e0;
            --input-bg: #ffffff;
            --input-border: #ced4da;
            --input-text: #495057;
            --placeholder: #adb5bd;
            --sidebar-width: 260px;
            --sidebar-collapsed-width: 80px;
            --dropdown-bg: #ffffff;
            --dropdown-hover: #f8f9fa;
        }

        [data-theme="dark"] {
            --primary: #FF6B6B;
            --bg-body: #121212;
            --bg-card: #1e1e1e;
            --text-main: #e0e0e0;
            --text-sec: #b0b0b0;
            --border: #333333;
            --input-bg: #2c2c2c;
            --input-border: #444;
            --input-text: #ffffff;
            --placeholder: rgba(255, 255, 255, 0.5);
            --dropdown-bg: #2c2c2c;
            --dropdown-hover: #3a3a3a;
        }

        /* --- 2. GLOBAL LAYOUT --- */
        body { background-color: var(--bg-body); color: var(--text-main); font-family: 'Segoe UI', sans-serif; overflow-x: hidden; transition: background 0.3s; }
        .wrapper { display: flex; width: 100%; align-items: stretch; }
        
        /* --- 3. SIDEBAR --- */
        .sidebar {
            min-width: var(--sidebar-width); max-width: var(--sidebar-width);
            background: var(--bg-card); border-right: 1px solid var(--border);
            min-height: 100vh; display: flex; flex-direction: column; padding: 20px;
            position: fixed; height: 100%; z-index: 1000; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .sidebar.collapsed { min-width: var(--sidebar-collapsed-width); max-width: var(--sidebar-collapsed-width); padding: 20px 10px; }
        
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .sidebar.collapsed .sidebar-header { flex-direction: column-reverse; gap: 15px; justify-content: center; }
        .brand-logo { max-height: 45px; width: auto; transition: all 0.3s; }
        .sidebar.collapsed .brand-logo { max-height: 30px; }
        
        .nav-link { color: var(--text-sec); padding: 10px; border-radius: 8px; margin-bottom: 5px; cursor: pointer; white-space: nowrap; overflow: hidden; display: flex; align-items: center; }
        .nav-link:hover, .nav-link.active { background-color: rgba(255, 107, 107, 0.1); color: var(--primary); }
        .nav-link i { width: 30px; text-align: center; margin-right: 10px; font-size: 1.1rem; }
        .sidebar.collapsed .nav-text { display: none; }
        .sidebar.collapsed .nav-link { justify-content: center; }
        .sidebar.collapsed .nav-link i { margin-right: 0; }

        /* --- 4. MAIN CONTENT --- */
        .main-content { margin-left: var(--sidebar-width); width: calc(100% - var(--sidebar-width)); padding: 30px; transition: all 0.3s; }
        .sidebar.collapsed + .main-content { margin-left: var(--sidebar-collapsed-width); width: calc(100% - var(--sidebar-collapsed-width)); }

        /* --- 5. COMPONENTS (FASE 2: Contraste & Layout) --- */
        .card { background-color: var(--bg-card); border: 1px solid var(--border); color: var(--text-main); margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        
        /* Centralização de Títulos */
        .card-header { 
            background-color: rgba(0,0,0,0.02); 
            border-bottom: 1px solid var(--border); 
            font-weight: 600; 
            padding: 15px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }
        .card-header > span { flex-grow: 1; text-align: center; margin-left: 24px; } /* Offset para centralizar visualmente */
        .card-header div { display: flex; align-items: center; gap: 8px; }

        /* Inputs Contrast Fix */
        .form-control, .form-select { 
            background-color: var(--input-bg); 
            border-color: var(--border); 
            color: var(--text-main); 
            padding-right: 30px;
        }
        .form-control:focus { 
            border-color: var(--primary); 
            box-shadow: 0 0 0 0.2rem rgba(255, 107, 107, 0.25); 
            background-color: var(--input-bg); 
            color: var(--text-main); 
        }
        .form-control::placeholder { color: var(--placeholder); opacity: 1; }
        
        /* Dropdowns (Floating Menus) */
        .dropdown-menu { background-color: var(--dropdown-bg); border-color: var(--border); }
        .dropdown-label { color: var(--text-main); cursor: pointer; padding: 4px 12px; display: block; }
        .dropdown-label:hover { background-color: var(--dropdown-hover); }

        /* Tables Contrast */
        .table { color: var(--text-main); border-color: var(--border); }
        .table thead th { border-bottom: 2px solid var(--border); color: var(--text-sec); }
        .table td { border-color: var(--border); }

        .stat-val { font-size: 2rem; font-weight: 700; color: var(--text-main); }
        .log-box { background: #1e1e1e; color: #4ade80; font-family: 'Consolas', monospace; padding: 15px; border-radius: 6px; height: 350px; overflow-y: auto; font-size: 0.85rem; border: 1px solid #333; }
        
        .btn-primary { background-color: var(--primary); border-color: var(--primary); }
        .btn-primary:hover { background-color: #ff5252; border-color: #ff5252; }
        
        /* Utils */
        .settings-section { display: none; animation: fadeIn 0.3s ease; }
        .settings-section.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        
        .security-msg { color: #ef4444; font-size: 0.8rem; margin-top: 4px; display: none; font-weight: 600; }
        .security-msg.visible { display: block; animation: shake 0.3s; }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }

        /* FASE 1.1: Container Controls */
        .accordion-icon { transition: transform 0.3s ease; }
        .collapsed-card .accordion-icon { transform: rotate(-90deg); }
        .card-body { transition: max-height 0.3s ease-out, opacity 0.3s ease-out; overflow: hidden; }
        .collapsed-card .card-body { display: none; }
        .card-header { cursor: pointer; user-select: none; }
        
        /* Footer */
        .sidebar-footer { margin-top: auto; padding-top: 20px; border-top: 1px solid var(--border); }
        .sidebar.collapsed .sidebar-footer { display: none; }
        .footer-copyright { margin-top: 20px; text-align: center; font-size: 0.8rem; opacity: 0.7; }
        
        /* Manual */
        .manual-content h6 { color: var(--primary); margin-top: 15px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }
        .manual-content a { color: var(--primary); text-decoration: underline; }
        
        /* Input Cleaner UX */
        .input-group-custom { position: relative; }
        .input-clear-btn { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: var(--text-sec); cursor: pointer; display: none; z-index: 10; }
        .form-control:not(:placeholder-shown) + .input-clear-btn { display: block; }
    </style>
</head>
<body>

<div class="wrapper">
    <nav id="sidebar" class="sidebar">
        <div class="sidebar-header">
            <img src="/static/logo.png" alt="Logo" class="brand-logo">
            <i class="fas fa-bars text-muted" onclick="toggleSidebar()" style="cursor: pointer;"></i>
        </div>
        
        <ul class="nav flex-column">
            <li class="nav-item"><a class="nav-link active" onclick="showTab('dashboard')" data-i18n-tooltip="menu_dashboard"><i class="fas fa-chart-pie"></i> <span class="nav-text" data-i18n="menu_dashboard">Visão Geral</span></a></li>
            <li class="nav-item"><a class="nav-link" onclick="showTab('performance')" data-i18n-tooltip="menu_performance"><i class="fas fa-tachometer-alt"></i> <span class="nav-text" data-i18n="menu_performance">Performance</span></a></li>
            <li class="nav-item"><a class="nav-link" onclick="showTab('evergreen')" data-i18n-tooltip="menu_evergreen"><i class="fas fa-seedling"></i> <span class="nav-text" data-i18n="menu_evergreen">Evergreen</span></a></li>
            <li class="nav-item"><a class="nav-link" onclick="showTab('sources')" data-i18n-tooltip="menu_sources"><i class="fas fa-rss"></i> <span class="nav-text" data-i18n="menu_sources">Fontes RSS</span></a></li>
            <li class="nav-item"><a class="nav-link" onclick="showTab('settings')" data-i18n-tooltip="menu_settings"><i class="fas fa-sliders-h"></i> <span class="nav-text" data-i18n="menu_settings">Configurações</span></a></li>
            <li class="nav-item"><a class="nav-link" onclick="showTab('manual')" data-i18n-tooltip="menu_manual"><i class="fas fa-book"></i> <span class="nav-text" data-i18n="menu_manual">Manual do Usuário</span></a></li>
        </ul>

        <div class="sidebar-footer">
            <div class="d-grid gap-2 mb-3">
                <button class="btn btn-sm btn-outline-secondary text-start" onclick="new bootstrap.Modal('#policyModal').show()" data-i18n-tooltip="btn_policies"><i class="fas fa-shield-alt me-2"></i> <span class="nav-text" data-i18n="btn_policies">Políticas & Dados</span></button>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-3">
                <select id="langSelect" class="form-select form-select-sm w-auto" onchange="changeLang(this.value)">
                    <option value="pt">BR</option><option value="en">EN</option><option value="es">ES</option>
                </select>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="darkModeSwitch" onchange="toggleDarkMode()" data-bs-toggle="tooltip" title="Modo Escuro">
                </div>
            </div>
            <small class="text-muted" id="systemStatus">STATUS: <span class="badge bg-secondary">STOPPED</span></small>
        </div>
    </nav>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="h4 m-0" id="pageTitle" data-i18n="dash_title">Visão Geral</h2>
            <div class="btn-group">
                <button id="btn-main" class="btn btn-success" onclick="controlSystem('START')" data-i18n-tooltip="btn_start_tt"><i class="fas fa-play"></i> <span data-i18n="btn_start">Iniciar</span></button>
                <button id="btn-pause" class="btn btn-warning text-white disabled" onclick="controlSystem('PAUSE')" disabled data-i18n-tooltip="btn_pause_tt"><i class="fas fa-pause"></i> <span data-i18n="btn_pause">Pausar</span></button>
            </div>
        </div>

        <div id="tab-dashboard" class="settings-section active">
            <div class="row mb-4">
                <div class="col-md-3"><div class="card p-3 text-center">
                    <small class="text-muted" style="display:block"><span data-i18n="stat_total_label">Total de Publicados</span> <i class="fas fa-question-circle" data-i18n-tooltip="stat_total_tooltip"></i></small>
                    <div class="stat-val" id="totalArticles">-</div>
                </div></div>
                <div class="col-md-3"><div class="card p-3 text-center">
                    <small class="text-muted" style="display:block"><span data-i18n="stat_today_label">Gerados Hoje</span> <i class="fas fa-question-circle" data-i18n-tooltip="stat_today_tooltip"></i></small>
                    <div class="stat-val" id="todayArticles">-</div>
                </div></div>
                <div class="col-md-3"><div class="card p-3 text-center">
                    <small class="text-muted" style="display:block"><span data-i18n="stat_pending_label">Fila de Aprovação</span> <i class="fas fa-question-circle" data-i18n-tooltip="stat_pending_tooltip"></i></small>
                    <div class="stat-val text-warning" id="pendingCount">-</div>
                </div></div>
                <div class="col-md-3"><div class="card p-3 text-center">
                    <small class="text-muted" style="display:block"><span data-i18n="stat_cache_label">Economia via Cache</span> <i class="fas fa-question-circle" data-i18n-tooltip="stat_cache_tooltip"></i></small>
                    <div class="stat-val text-primary" id="cacheCount">-</div>
                </div></div>
            </div>
            <div class="card" id="card-logs">
                <div class="card-header" onclick="toggleCard('card-logs')">
                    <span><i class="fas fa-terminal me-2"></i> <span data-i18n="log_title">Registro de Execução</span></span>
                    <div>
                        <button class="btn btn-sm btn-outline-danger me-2" onclick="event.stopPropagation(); clearLogs()" data-i18n-tooltip="btn_clear_logs"><i class="fas fa-trash"></i></button>
                        <button class="btn btn-sm btn-outline-secondary me-2" onclick="event.stopPropagation(); loadLogs()" data-i18n-tooltip="btn_refresh"><i class="fas fa-sync"></i></button>
                        <i class="fas fa-chevron-down accordion-icon"></i>
                    </div>
                </div>
                <div class="card-body p-0"><div class="log-box" id="logBox">Loading...</div></div>
            </div>
        </div>

        <div id="tab-performance" class="settings-section">
            <div class="row mb-4">
                <div class="col-md-4"><div class="card p-3 text-center"><h5>CPU</h5><div class="progress" style="height:20px"><div id="cpuBar" class="progress-bar bg-info" style="width:0%"></div></div><span id="cpuVal">0%</span></div></div>
                <div class="col-md-4"><div class="card p-3 text-center"><h5>RAM</h5><div class="progress" style="height:20px"><div id="ramBar" class="progress-bar bg-warning" style="width:0%"></div></div><span id="ramVal">0%</span></div></div>
                <div class="col-md-4"><div class="card p-3 text-center"><h5>Disk</h5><div class="progress" style="height:20px"><div id="diskBar" class="progress-bar bg-success" style="width:0%"></div></div><span id="diskVal">0%</span></div></div>
            </div>
            <div class="card" id="card-perf-history">
                <div class="card-header" onclick="toggleCard('card-perf-history')">
                    <span><i class="fas fa-history me-2"></i> <span data-i18n="hist_opt_title">Histórico de Otimização</span></span>
                    <div>
                        <button class="btn btn-sm btn-outline-danger me-2" onclick="event.stopPropagation(); clearHistory('perf')" data-i18n-tooltip="btn_clear_hist"><i class="fas fa-trash"></i></button>
                        <i class="fas fa-chevron-down accordion-icon"></i>
                    </div>
                </div>
                <div class="card-body"><table class="table table-sm table-hover"><thead><tr><th data-i18n="th_date">Data/Hora</th><th data-i18n="th_action">Ação</th><th data-i18n="th_status">Status</th></tr></thead><tbody id="perfHistoryTable"></tbody></table></div>
            </div>
        </div>

        <div id="tab-evergreen" class="settings-section">
            <div class="card p-4 mb-4">
                <label class="form-label fw-bold" data-i18n="input_topic">Tópico Principal</label>
                <div class="input-group">
                    <input type="text" id="evergreenTopic" class="form-control" data-i18n-placeholder="ph_evergreen">
                    <button class="btn btn-success" onclick="triggerEvergreen()"><i class="fas fa-magic"></i> <span data-i18n="btn_generate">Gerar</span></button>
                </div>
            </div>
            <div class="card" id="card-evergreen-hist">
                <div class="card-header" onclick="toggleCard('card-evergreen-hist')">
                    <span data-i18n="hist_gen_title">Histórico de Artigos Gerados</span>
                    <div>
                        <button class="btn btn-sm btn-outline-secondary me-2" onclick="event.stopPropagation(); renderEvergreenHistory()" data-i18n-tooltip="btn_refresh"><i class="fas fa-sync"></i></button>
                        <button class="btn btn-sm btn-outline-danger me-2" onclick="event.stopPropagation(); clearHistory('evergreen')" data-i18n-tooltip="btn_clear_hist"><i class="fas fa-trash"></i></button>
                        <i class="fas fa-chevron-down accordion-icon"></i>
                    </div>
                </div>
                <div class="card-body"><table class="table table-striped"><thead><tr><th data-i18n="th_date">Data</th><th data-i18n="th_title">Título</th><th data-i18n="th_cat">Categorias</th></tr></thead><tbody id="evergreenTableBody"></tbody></table></div>
            </div>
        </div>

        <div id="tab-sources" class="settings-section">
            <div class="d-flex justify-content-between mb-4">
                <button class="btn btn-outline-danger" onclick="deleteAllSources()" data-i18n-tooltip="btn_delete_sources"><i class="fas fa-bomb"></i> <span data-i18n="btn_delete_sources_txt">Apagar Fontes</span></button>
                <button class="btn btn-primary" onclick="openRssModal()" data-i18n-tooltip="btn_add_feed_tt">+ Add Feed</button>
            </div>
            <div class="card" id="card-rss">
                <div class="card-header" onclick="toggleCard('card-rss')">
                    <span><i class="fas fa-stream me-2"></i> <span data-i18n="rss_manager_title">Gerenciador de Fontes</span></span>
                    <i class="fas fa-chevron-down accordion-icon"></i>
                </div>
                <div class="card-body"><table class="table table-hover"><thead><tr><th data-i18n="th_active">Ativo</th><th data-i18n="th_name">Nome</th><th data-i18n="th_url">URL</th><th></th></tr></thead><tbody id="rssTableBody"></tbody></table></div>
            </div>
        </div>

        <div id="tab-settings" class="settings-section">
            <form id="settingsForm">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4 border-primary" id="card-google">
                            <div class="card-header bg-primary text-white" onclick="toggleCard('card-google')"><span><span data-i18n="sec_google_title">Google Ecosystem</span></span><i class="fas fa-chevron-down accordion-icon text-white"></i></div>
                            <div class="card-body">
                                <div class="mb-3"><label>Project ID</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="google_project_id" data-i18n-placeholder="ph_google_project"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div><small class="security-msg">Bloqueado.</small></div>
                                <div class="mb-3"><label>Gemini Key</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="google_api_key"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div><small class="security-msg">Bloqueado.</small></div>
                                <div class="mb-3"><label>YouTube Key</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="youtube_api_key"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div><small class="security-msg">Bloqueado.</small></div>
                            </div>
                        </div>
                        <div class="card mb-4 border-success" id="card-news">
                            <div class="card-header bg-success text-white" onclick="toggleCard('card-news')"><span><span data-i18n="sec_news_title">Fontes de Notícias</span></span><i class="fas fa-chevron-down accordion-icon text-white"></i></div>
                            <div class="card-body">
                                <div class="mb-2">
                                    <label>GNews Key</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="gnews_api_key"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div>
                                    <div class="dropdown mt-1"><button class="btn btn-outline-secondary btn-sm dropdown-toggle w-100 text-start" type="button" data-bs-toggle="dropdown">Categorias</button><ul class="dropdown-menu w-100 p-2"><li><label class="dropdown-label"><input class="form-check-input me-2" type="checkbox" name="gnews_categories" value="general">General</label></li><li><label class="dropdown-label"><input class="form-check-input me-2" type="checkbox" name="gnews_categories" value="technology">Technology</label></li><li><label class="dropdown-label"><input class="form-check-input me-2" type="checkbox" name="gnews_categories" value="business">Business</label></li></ul></div>
                                </div>
                                <div class="mb-2">
                                    <label>NewsAPI Key</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="newsapi_key"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div>
                                    <div class="dropdown mt-1"><button class="btn btn-outline-secondary btn-sm dropdown-toggle w-100 text-start" type="button" data-bs-toggle="dropdown">Categorias</button><ul class="dropdown-menu w-100 p-2"><li><label class="dropdown-label"><input class="form-check-input me-2" type="checkbox" name="newsapi_categories" value="general">General</label></li><li><label class="dropdown-label"><input class="form-check-input me-2" type="checkbox" name="newsapi_categories" value="technology">Technology</label></li></ul></div>
                                </div>
                                <div class="mb-2">
                                    <label>Currents Key</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="currents_api_key"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div>
                                    <div class="dropdown mt-1"><button class="btn btn-outline-secondary btn-sm dropdown-toggle w-100 text-start" type="button" data-bs-toggle="dropdown">Categorias</button><ul class="dropdown-menu w-100 p-2"><li><label class="dropdown-label"><input class="form-check-input me-2" type="checkbox" name="currents_categories" value="technology">Technology</label></li></ul></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4" id="card-wp">
                            <div class="card-header" onclick="toggleCard('card-wp')"><span><span data-i18n="sec_wp_title">WordPress</span></span><i class="fas fa-chevron-down accordion-icon"></i></div>
                            <div class="card-body">
                                <div class="mb-2"><label>URL</label><div class="input-group-custom"><input type="text" class="form-control" name="wordpress_url" data-i18n-placeholder="ph_wp_url"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div></div>
                                <div class="mb-2"><label data-i18n="lbl_user">User</label><div class="input-group-custom"><input type="text" class="form-control" name="wordpress_username"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div></div>
                                <div class="mb-2"><label>Pass</label><div class="input-group-custom"><input type="password" class="form-control secure-input" name="wordpress_password"><span class="input-clear-btn" onclick="clearInput(this)"><i class="fas fa-times"></i></span></div><small class="security-msg">Bloqueado.</small></div>
                                <hr>
                                <div class="form-check form-switch"><input class="form-check-input" type="checkbox" name="require_manual_approval"><label class="form-check-label" data-i18n="tg_review">Revisão Manual</label></div>
                            </div>
                        </div>
                        
                        <div class="card mb-4 control-panel-card" id="card-control-panel">
                            <div class="card-header" onclick="toggleCard('card-control-panel')"><span data-i18n="cp_title">Painel de Controle</span><i class="fas fa-chevron-down accordion-icon"></i></div>
                            <div class="card-body p-4">
                                <div class="bg-light p-3 rounded mb-3 border">
                                    <div class="form-check form-switch mb-2"><input class="form-check-input" type="checkbox" name="enable_global_images"><label class="form-check-label" data-i18n="tg_images">Images (Vertex)</label></div>
                                    <div class="form-check form-switch"><input class="form-check-input" type="checkbox" name="enable_youtube_embed"><label class="form-check-label" data-i18n="tg_videos">Videos (YT)</label></div>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="button" class="btn btn-primary w-100" onclick="saveSettings()"><i class="fas fa-save"></i> <span data-i18n="btn_save_all">Salvar Tudo</span></button>
                                    <button type="button" class="btn btn-outline-danger w-100" onclick="clearAllHistories()"><i class="fas fa-skull"></i> <span data-i18n="btn_clear_global">Apagar Todos os Históricos</span></button>
                                    <button type="button" class="btn btn-success w-100" onclick="optimizeSystem()" data-i18n-tooltip="btn_optimize_tt"><i class="fas fa-broom"></i> <span data-i18n="btn_optimize">Otimizar Sistema</span></button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <div id="tab-manual" class="settings-section">
            <div class="card p-4" id="manualContainer"></div>
        </div>
        
        <div class="footer-copyright">&copy; <span id="yr"></span> <span data-i18n="footer_copy">Equipe Cogitari</span></div>
    </div>
</div>

<div class="modal fade" id="rssModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" data-i18n="rss_modal_title">Feed RSS</h5><button class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><input type="text" id="rssName" class="form-control mb-2" data-i18n-placeholder="ph_rss_name"><input type="text" id="rssTheme" class="form-control mb-2" data-i18n-placeholder="ph_rss_theme"><input type="text" id="rssUrl" class="form-control" data-i18n-placeholder="ph_rss_url"></div><div class="modal-footer"><button class="btn btn-primary" onclick="saveRss()" data-i18n="btn_save">Salvar</button></div></div></div></div>
<div class="modal fade" id="policyModal" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content"><div class="modal-header"><h5 data-i18n="btn_policies">Legal</h5><button class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><div class="accordion" id="accPol"><div class="accordion-item"><h2 class="accordion-header"><button class="accordion-button" data-bs-toggle="collapse" data-bs-target="#c1" data-i18n="pol_priv_t">Privacidade</button></h2><div id="c1" class="accordion-collapse collapse show" data-bs-parent="#accPol"><div class="accordion-body" data-i18n="pol_priv_d">...</div></div></div><div class="accordion-item"><h2 class="accordion-header"><button class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#c2" data-i18n="pol_terms_t">Termos</button></h2><div id="c2" class="accordion-collapse collapse" data-bs-parent="#accPol"><div class="accordion-body" data-i18n="pol_terms_d">...</div></div></div></div></div></div></div></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    // --- FASE 3: i18n FULL RESTORATION ---
    const i18n = {
        pt: {
            menu_dashboard: "Visão Geral", menu_performance: "Performance", menu_evergreen: "Evergreen", menu_sources: "Fontes RSS", menu_settings: "Configurações", menu_manual: "Manual do Usuário", btn_policies: "Políticas & Dados",
            dash_title: "Visão Geral", log_title: "Registro de Execução", btn_start: "Iniciar", btn_pause: "Pausar", btn_stop: "Parar",
            stat_total_label: "Total de Publicados", stat_today_label: "Gerados Hoje", stat_pending_label: "Fila de Aprovação", stat_cache_label: "Economia via Cache",
            stat_total_tooltip: "Contagem absoluta.", stat_today_tooltip: "Últimas 24h.", stat_pending_tooltip: "Aguardando.", stat_cache_tooltip: "Economia API.",
            sec_google_title: "Ecossistema Google", sec_news_title: "Fontes de Notícias", sec_wp_title: "WordPress", cp_title: "Painel de Controle",
            btn_generate: "Gerar", btn_save_all: "Salvar Tudo", btn_optimize: "Otimizar Sistema", btn_clear_global: "Apagar Todos os Históricos", btn_delete_sources_txt: "Apagar Fontes",
            btn_optimize_tt: "Limpa RAM e Cache", btn_clear_hist: "Limpar esta lista", btn_delete_sources: "Remove feeds RSS", btn_refresh: "Atualizar", btn_clear_logs: "Limpar Logs", btn_add_feed_tt: "Novo Feed",
            hist_opt_title: "Histórico de Otimização", hist_gen_title: "Histórico de Artigos Gerados", rss_manager_title: "Gerenciador de Fontes", rss_modal_title: "Adicionar Feed RSS",
            btn_use_gnews: "Usar GNews", btn_use_newsapi: "Usar NewsAPI", btn_use_currents: "Usar Currents", footer_copy: "Equipe Cogitari",
            tg_images: "Gerar Imagens (Vertex)", tg_videos: "Buscar Vídeos (YT)", tg_review: "Revisão Manual",
            ph_google_project: "Ex: my-project", ph_wp_url: "Ex: site.com", ph_rss_name: "Nome da Fonte", ph_rss_theme: "Tema", ph_rss_url: "URL", ph_evergreen: "Tópico...",
            th_date: "Data/Hora", th_action: "Ação", th_status: "Status", th_title: "Título", th_cat: "Categorias", th_active: "Ativo", th_name: "Nome", th_url: "URL",
            man_intro_t: "1. Início", man_intro_d: "<p>Bem-vindo ao S1M0N.</p>",
            man_setup_t: "2. Setup", man_setup_d: "<p>Configure as APIs na aba Configurações.</p>",
            man_gen_t: "3. Uso", man_gen_d: "<p>Use Evergreen ou RSS.</p>",
            pol_title: "Políticas", pol_priv_t: "Privacidade", pol_priv_d: "<p>Dados locais apenas.</p>", pol_terms_t: "Termos", pol_terms_d: "<p>Uso responsável.</p>"
        },
        en: {
            menu_dashboard: "Overview", menu_performance: "Performance", menu_evergreen: "Evergreen", menu_sources: "RSS Feeds", menu_settings: "Settings", menu_manual: "User Manual", btn_policies: "Policies & Data",
            dash_title: "Overview", log_title: "Execution Log", btn_start: "Start", btn_pause: "Pause", btn_stop: "Stop",
            stat_total_label: "Total Published", stat_today_label: "Generated Today", stat_pending_label: "Approval Queue", stat_cache_label: "Cache Savings",
            stat_total_tooltip: "Absolute count.", stat_today_tooltip: "Last 24h.", stat_pending_tooltip: "Waiting.", stat_cache_tooltip: "API savings.",
            sec_google_title: "Google Eco", sec_news_title: "News Sources", sec_wp_title: "WordPress", cp_title: "Control Panel",
            btn_generate: "Generate", btn_save_all: "Save All", btn_optimize: "Optimize System", btn_clear_global: "Clear All Histories", btn_delete_sources_txt: "Delete Feeds",
            btn_optimize_tt: "Clears RAM/Cache", btn_clear_hist: "Clear list", btn_delete_sources: "Remove RSS feeds", btn_refresh: "Refresh", btn_clear_logs: "Clear Logs", btn_add_feed_tt: "New Feed",
            hist_opt_title: "Optimization History", hist_gen_title: "Generation History", rss_manager_title: "Source Manager", rss_modal_title: "Add RSS Feed",
            btn_use_gnews: "Use GNews", btn_use_newsapi: "Use NewsAPI", btn_use_currents: "Use Currents", footer_copy: "Cogitari Team",
            tg_images: "Generate Images (Vertex)", tg_videos: "Fetch Videos (YT)", tg_review: "Manual Review",
            ph_google_project: "Ex: my-project", ph_wp_url: "Ex: site.com", ph_rss_name: "Source Name", ph_rss_theme: "Theme", ph_rss_url: "URL", ph_evergreen: "Topic...",
            th_date: "Date/Time", th_action: "Action", th_status: "Status", th_title: "Title", th_cat: "Categories", th_active: "Active", th_name: "Name", th_url: "URL",
            man_intro_t: "1. Intro", man_intro_d: "<p>Welcome to S1M0N.</p>", man_setup_t: "2. Setup", man_setup_d: "<p>Configure APIs in Settings.</p>", man_gen_t: "3. Usage", man_gen_d: "<p>Use Evergreen or RSS.</p>",
            pol_title: "Policies", pol_priv_t: "Privacy", pol_priv_d: "<p>Local data only.</p>", pol_terms_t: "Terms", pol_terms_d: "<p>Responsible use.</p>"
        },
        es: {
            menu_dashboard: "Visión General", menu_performance: "Rendimiento", menu_evergreen: "Evergreen", menu_sources: "Fuentes RSS", menu_settings: "Configuraciones", menu_manual: "Manual de Usuario", btn_policies: "Políticas y Datos",
            dash_title: "Visión General", log_title: "Registro de Ejecución", btn_start: "Iniciar", btn_pause: "Pausar", btn_stop: "Parar",
            stat_total_label: "Total Publicados", stat_today_label: "Generados Hoy", stat_pending_label: "Cola de Aprobación", stat_cache_label: "Ahorro Caché",
            stat_total_tooltip: "Conteo absoluto.", stat_today_tooltip: "Últimas 24h.", stat_pending_tooltip: "Espera.", stat_cache_tooltip: "Ahorro API.",
            sec_google_title: "Ecosistema Google", sec_news_title: "Fuentes de Noticias", sec_wp_title: "WordPress", cp_title: "Panel de Control",
            btn_generate: "Generar", btn_save_all: "Guardar Todo", btn_optimize: "Optimizar Sistema", btn_clear_global: "Borrar Historiales", btn_delete_sources_txt: "Borrar Fuentes",
            btn_optimize_tt: "Limpia RAM/Caché", btn_clear_hist: "Limpiar lista", btn_delete_sources: "Eliminar feeds", btn_refresh: "Actualizar", btn_clear_logs: "Limpiar Logs", btn_add_feed_tt: "Nuevo Feed",
            hist_opt_title: "Historial de Optimización", hist_gen_title: "Historial de Generación", rss_manager_title: "Gestor de Fuentes", rss_modal_title: "Añadir Feed RSS",
            btn_use_gnews: "Usar GNews", btn_use_newsapi: "Usar NewsAPI", btn_use_currents: "Usar Currents", footer_copy: "Equipo Cogitari",
            tg_images: "Generar Imágenes (Vertex)", tg_videos: "Buscar Videos (YT)", tg_review: "Revisión Manual",
            ph_google_project: "Ej: my-project", ph_wp_url: "Ej: sitio.com", ph_rss_name: "Nombre", ph_rss_theme: "Tema", ph_rss_url: "URL", ph_evergreen: "Tema...",
            th_date: "Fecha/Hora", th_action: "Acción", th_status: "Estado", th_title: "Título", th_cat: "Categorías", th_active: "Activo", th_name: "Nombre", th_url: "URL",
            man_intro_t: "1. Introducción", man_intro_d: "<p>Bienvenido a S1M0N.</p>", man_setup_t: "2. Configuración", man_setup_d: "<p>Configure APIs.</p>", man_gen_t: "3. Uso", man_gen_d: "<p>Use Evergreen o RSS.</p>",
            pol_title: "Políticas", pol_priv_t: "Privacidad", pol_priv_d: "<p>Datos locales.</p>", pol_terms_t: "Términos", pol_terms_d: "<p>Uso responsable.</p>"
        }
    };

    function init() {
        const lang = localStorage.getItem('s1m0n_lang') || 'pt';
        document.getElementById('langSelect').value = lang;
        
        if(localStorage.getItem('s1m0n_theme') === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            document.getElementById('darkModeSwitch').checked = true;
        }

        document.getElementById('yr').innerText = new Date().getFullYear();
        
        // FASE 1: INPUT CLEAR LOGIC
        window.clearInput = function(el) {
            const input = el.previousElementSibling;
            input.value = '';
            input.focus();
        };
        
        // Tooltip Init
        changeLang(lang);

        renderHistories(); renderManual();
        setInterval(updateData, 5000); updateData();
    }

    function toggleSidebar() { document.querySelector('.sidebar').classList.toggle('collapsed'); }
    function toggleCard(id) { document.getElementById(id).classList.toggle('collapsed-card'); }
    
    function showTab(tabId) {
        document.querySelectorAll('.settings-section').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
        document.getElementById('tab-' + tabId).classList.add('active');
        event.currentTarget.classList.add('active');
        if(tabId === 'sources') loadRss();
        if(tabId === 'settings') loadSettings();
    }

    function changeLang(lang) {
        localStorage.setItem('s1m0n_lang', lang);
        const t = i18n[lang] || i18n['pt'];
        
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const k = el.getAttribute('data-i18n');
            if(t[k]) el.innerHTML = t[k];
        });
        
        // Dispose old tooltips before creating new ones to avoid ghosts
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            const instance = bootstrap.Tooltip.getInstance(el);
            if(instance) instance.dispose();
        });

        // Smart Tooltips (Fase 3)
        document.querySelectorAll('[data-i18n-tooltip]').forEach(el => {
            const k = el.getAttribute('data-i18n-tooltip');
            if(t[k]) el.setAttribute('title', t[k]);
            new bootstrap.Tooltip(el);
        });
        
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const k = el.getAttribute('data-i18n-placeholder');
            if(t[k]) el.setAttribute('placeholder', t[k]);
        });

        renderManual();
    }

    function toggleDarkMode() {
        const isDark = document.getElementById('darkModeSwitch').checked;
        document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
        localStorage.setItem('s1m0n_theme', isDark ? 'dark' : 'light');
    }
    
    function showToast(msg, type='success') {
        const toast = document.createElement('div'); toast.className = 'toast-custom';
        toast.innerHTML = `<i class="fas fa-${type==='success'?'check-circle':'info-circle'} text-${type}"></i> ${msg}`;
        document.getElementById('toast-container').appendChild(toast); toast.style.display = 'flex';
        setTimeout(() => toast.remove(), 3000);
    }

    async function controlSystem(action) {
        if(!confirm(action + '?')) return;
        const res = await fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action})});
        const data = await res.json();
        const badge = document.getElementById('systemStatus').querySelector('.badge');
        badge.innerText = data.state;
        badge.className = `badge bg-${data.state==='RUNNING'?'success':data.state==='PAUSED'?'warning':'secondary'}`;
        
        const btnMain = document.getElementById('btn-main');
        const btnPause = document.getElementById('btn-pause');
        const lang = localStorage.getItem('s1m0n_lang') || 'pt';
        
        if(data.state === 'RUNNING') {
            btnMain.className = 'btn btn-danger'; btnMain.innerHTML = `<i class="fas fa-stop"></i> ${i18n[lang].btn_stop}`; btnMain.onclick = () => controlSystem('STOP');
            btnPause.classList.remove('disabled'); btnPause.onclick = () => controlSystem('PAUSE');
        } else {
            btnMain.className = 'btn btn-success'; btnMain.innerHTML = `<i class="fas fa-play"></i> ${i18n[lang].btn_start}`; btnMain.onclick = () => controlSystem('START');
            btnPause.classList.add('disabled');
        }
    }

    async function updateData() {
        try {
            const s = await (await fetch('/api/stats')).json();
            document.getElementById('totalArticles').innerText = s.total_articles;
            document.getElementById('todayArticles').innerText = s.today;
            document.getElementById('pendingCount').innerText = s.pending;
            document.getElementById('cacheCount').innerText = s.cache_count;
        } catch {}
        if(document.getElementById('tab-dashboard').classList.contains('active')) loadLogs();
        if(document.getElementById('tab-performance').classList.contains('active')) loadPerf();
    }

    async function loadLogs() {
        try {
            const res = await (await fetch('/api/logs')).json();
            document.getElementById('logBox').innerHTML = res.logs.map(l => `<div>${l}</div>`).join('');
        } catch {}
    }
    
    async function clearLogs() { await fetch('/api/logs/clear', {method:'POST'}); loadLogs(); }

    async function loadPerf() {
        const p = await (await fetch('/api/performance')).json();
        document.getElementById('cpuBar').style.width = p.cpu + '%'; document.getElementById('cpuVal').innerText = p.cpu + '%';
        document.getElementById('ramBar').style.width = p.ram + '%'; document.getElementById('ramVal').innerText = p.ram + '%';
        document.getElementById('diskBar').style.width = p.disk + '%'; document.getElementById('diskVal').innerText = p.disk + '%';
    }

    // FASE 3: UPDATED HISTORY COLUMNS
    function renderHistories() {
        const lang = localStorage.getItem('s1m0n_lang') || 'pt';
        const ok = lang === 'pt' ? 'Sucesso' : 'Success';
        const perfH = JSON.parse(localStorage.getItem('s1m0n_perf_hist') || '[]');
        document.getElementById('perfHistoryTable').innerHTML = perfH.slice(0,5).map(h => `<tr><td>${h.date}</td><td>${h.action}</td><td><span class="badge bg-success">${ok}</span></td></tr>`).join('');
        
        const genH = JSON.parse(localStorage.getItem('s1m0n_evergreen_hist') || '[]');
        document.getElementById('evergreenTableBody').innerHTML = genH.slice(0,5).map(h => `<tr><td>${h.date}</td><td>${h.title}</td><td>${h.cat}</td></tr>`).join('');
    }

    function clearHistory(type) { 
        if(confirm('Limpar?')) { 
            localStorage.removeItem(`s1m0n_${type}_hist`); 
            renderHistories(); 
        } 
    }
    function clearAllHistories() {
        if(confirm('ATENÇÃO: Apagar TODOS os históricos?')) {
            localStorage.removeItem('s1m0n_perf_hist');
            localStorage.removeItem('s1m0n_evergreen_hist');
            renderHistories();
            alert('Históricos apagados.');
        }
    }

    async function optimizeSystem() {
        await fetch('/api/performance/optimize', {method:'POST'});
        const h = JSON.parse(localStorage.getItem('s1m0n_perf_hist') || '[]');
        h.unshift({date: new Date().toLocaleTimeString(), action: 'Otimização'});
        localStorage.setItem('s1m0n_perf_hist', JSON.stringify(h));
        renderHistories();
    }

    async function triggerEvergreen() {
        const topic = document.getElementById('evergreenTopic').value;
        if(!topic) return;
        await fetch('/api/evergreen', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({topic})});
        const h = JSON.parse(localStorage.getItem('s1m0n_evergreen_hist') || '[]');
        h.unshift({date: new Date().toLocaleDateString(), title: topic, cat: 'Geral'});
        localStorage.setItem('s1m0n_evergreen_hist', JSON.stringify(h));
        renderHistories();
        alert('Iniciado!');
    }

    async function loadRss() {
        const feeds = await (await fetch('/api/rss')).json();
        document.getElementById('rssTableBody').innerHTML = feeds.map(f => `
            <tr>
                <td><div class="form-check form-switch"><input class="form-check-input" type="checkbox" ${f.is_active?'checked':''} onclick="toggleRss(${f.id})"></div></td>
                <td>${f.name}</td>
                <td><small>${f.url}</small></td>
                <td><button class="btn btn-sm btn-outline-danger" onclick="delRss(${f.id})"><i class="fas fa-trash"></i></button></td>
            </tr>
        `).join('');
    }
    
    async function saveRss() {
        await fetch('/api/rss', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
            name: document.getElementById('rssName').value,
            url: document.getElementById('rssUrl').value,
            theme: document.getElementById('rssTheme').value // FASE 1: THEME INPUT RESTORED
        })});
        bootstrap.Modal.getInstance(document.getElementById('rssModal')).hide();
        loadRss();
    }
    async function delRss(id) { if(confirm('Delete?')) { await fetch(`/api/rss/${id}`, {method:'DELETE'}); loadRss(); } }
    async function toggleRss(id) { await fetch(`/api/rss/${id}/toggle`, {method:'POST'}); }
    
    async function deleteAllSources() {
        if(confirm('Apagar TODOS?')) {
            await fetch('/api/rss/delete_all', {method:'POST'});
            loadRss();
        }
    }

    async function loadSettings() {
        const d = await (await fetch('/api/settings')).json();
        const f = document.getElementById('settingsForm');
        ['enable_global_images', 'enable_youtube_embed', 'require_manual_approval'].forEach(k => {
             if(f.elements[k]) f.elements[k].checked = (d[k] === 'true');
        });
        
        for(const [k, v] of Object.entries(d)) {
            if(k.includes('_categories')) {
                 try{const vals=JSON.parse(v); Array.from(document.querySelectorAll(`input[name="${k}"]`)).forEach(cb=>{cb.checked=vals.includes(cb.value)})}catch{}
            } else if(f.elements[k] && f.elements[k].type !== 'checkbox') {
                f.elements[k].value = v;
            }
        }
    }

    async function saveSettings() {
        const f = document.getElementById('settingsForm');
        const d = {};
        const formData = new FormData(f);
        
        ['gnews_categories', 'newsapi_categories', 'currents_categories'].forEach(catName => {
            const selected = [];
            document.querySelectorAll(`input[name="${catName}"]:checked`).forEach(cb => selected.push(cb.value));
            d[catName] = JSON.stringify(selected);
        });
        
        for (const [key, value] of formData.entries()) { if (!key.includes('_categories')) d[key] = value; }
        ['enable_global_images', 'enable_youtube_embed', 'require_manual_approval'].forEach(k => d[k] = f.elements[k].checked);
        
        await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(d)});
        alert('Salvo!');
    }

    function renderManual() {
        const lang = document.getElementById('langSelect').value;
        const t = i18n[lang] || i18n['pt'];
        const items = [
            {t: t.man_intro_t, d: t.man_intro_d},
            {t: t.man_setup_t, d: t.man_setup_d},
            {t: t.man_gen_t, d: t.man_gen_d}
        ];
        document.getElementById('manualContainer').innerHTML = items.map((item, i) => `
            <div class="manual-item">
                <div class="manual-title" onclick="document.getElementById('mc${i}').classList.toggle('show')">
                    <i class="fas fa-chevron-right me-2"></i> ${item.t}
                </div>
                <div class="manual-content" id="mc${i}">${item.d}</div>
            </div>
        `).join('');
    }

    window.onload = init;
</script>
</body>
</html>
"""

# ==============================================================================
# FLASK ROUTES
# ==============================================================================

@app.route('/')
def index(): return render_template_string(DASHBOARD_HTML)

@app.route('/static/<path:filename>')
def serve_static(filename): return send_from_directory(STATIC_DIR, filename)

@app.route('/api/control', methods=['POST'])
def control():
    global SYSTEM_STATE
    action = request.json.get('action')
    if action == 'START': SYSTEM_STATE = 'RUNNING'
    elif action == 'PAUSE': SYSTEM_STATE = 'PAUSED'
    elif action == 'STOP': SYSTEM_STATE = 'STOPPED'
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
def evergreen():
    topic = request.json.get('topic')
    threading.Thread(target=lambda: ContentEngine().run_evergreen(topic)).start()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)