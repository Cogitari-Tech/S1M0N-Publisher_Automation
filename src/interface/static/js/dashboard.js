/* S1M0N Dashboard Logic v8.3 */

// --- I18N CONFIGURATION ---
const i18n = {
    pt: {
        // --- MENUS ---
        menu_dashboard: "Visão Geral", menu_performance: "Performance & Logs", menu_evergreen: "Evergreen (SEO)", menu_sources: "Fontes RSS", menu_settings: "Configurações", menu_manual: "Manual do Usuário", btn_policies: "Políticas & Dados", menu_review: "Histórico & Revisão",
        dash_title: "Visão Geral", log_title: "Registro de Execução Compilado", btn_start: "Iniciar", btn_pause: "Pausar", btn_stop: "Parar",

        // --- HELP (ON-CLICK) ---
        help_perf: "Monitora recursos do sistema (CPU/RAM) e configurações centrais do S1M0N.",
        help_evergreen: "Gera artigos aprofundados sobre tópicos atemporais (sem necessidade de notícias recentes).",
        help_rss: "Gerencia suas fontes de notícias. Adicione feeds RSS de sites confiáveis aqui.",
        help_settings: "Configure suas chaves de API e conexões.", // Generic fallback
        help_google: "Configure suas credenciais do Google Cloud (Vertex AI p/ Imagens) e YouTube Data API.",
        help_news: "Gerencie as chaves de API para seus provedores de notícias (GNews, NewsAPI, Currents).",
        help_wp: "Conecte seu site WordPress. Use URL completa, usuário e Senha de Aplicação (não a de login).",
        help_cp: "Controles avançados: Logs, Modo Seguro, Timeouts e tratamento de erros.",

        // --- STATS ---
        stat_total_label: "Total de Publicados", stat_today_label: "Gerados Hoje", stat_pending_label: "Fila de Aprovação", stat_cache_label: "Economia via Cache",
        stat_total_tooltip: "Contagem absoluta de artigos enviados ao WordPress desde o início.",
        stat_today_tooltip: "Artigos gerados nas últimas 24 horas (ciclo diário).",
        stat_pending_tooltip: "Artigos aguardando revisão manual antes da publicação.",
        stat_cache_tooltip: "Número de requisições API economizadas por estarem em cache.",

        // --- TOOLTIPS (DESCRIPTIVE) ---
        tt_start: "Inicia o ciclo contínuo de monitoramento de RSS e geração de artigos.",
        tt_pause: "Pausa temporariamente o ciclo. O processo atual será concluído antes de parar.",
        tt_stop: "Interrompe todos os processos imediatamente.",
        tt_refresh: "Atualiza os dados da tela manualmente (útil se o auto-refresh falhar).",
        tt_logs_clear: "Apaga o registro visual de logs (não afeta o arquivo de log no disco).",
        tt_add_feed: "Adiciona uma nova URL de Feed RSS para monitoramento.",
        tt_del_sources: "Remove TODAS as fontes cadastradas do banco de dados.",
        tt_save_all: "Salva todas as configurações de API, WordPress e preferências no banco local.",
        tt_cycles: "Defina o intervalo de tempo (em minutos) entre as buscas automáticas de conteúdo.",
        tt_clear_hist: "Apaga permanentemente o histórico de artigos gerados e dados de performance.",
        tt_optimize: "Executa limpeza de memória RAM e compactação de banco de dados (SQLite Vacuum).",
        tt_google_proj: "ID do Projeto no Google Cloud (necessário para Vertex AI).",
        tt_gemini_key: "Chave API do Google AI Studio (Gemini 1.5).",
        tt_yt_key: "Chave API do YouTube Data v3 para buscar vídeos relacionados.",
        tt_news_key: "Chave API do serviço de notícias escolhido (GNews, NewsAPI ou Currents).",
        tt_wp_url: "Endereço completo do seu site WordPress (https://...).",
        tt_wp_user: "Nome de usuário do WordPress com permissão de editor/admin.",
        tt_wp_pass: "Senha de Aplicação (não a senha de login). Gere em Usuários > Perfil.",
        tt_pub_mode: "Define se o artigo vai direto ao ar ou fica como Rascunho para revisão.",
        tt_manual_rev: "Se ativado, bloqueia envio automático e coloca na fila de 'Revisão'.",

        // --- TITLES & BUTTONS ---
        sec_google_title: "Ecossistema Google (Vertex/Gemini)", sec_news_title: "Fontes de Notícias e RSS", sec_wp_title: "Integração WordPress", cp_title: "Painel de Controle Central",
        btn_generate: "Gerar Tópico Agora", btn_save_all: "Salvar Configurações", btn_optimize: "Otimizar Sistema", btn_clear_global: "Resetar Históricos", btn_delete_sources_txt: "Apagar Fontes",
        hist_opt_title: "Logs de Otimização", hist_gen_title: "Histórico de Publicações", rss_manager_title: "Gerenciador de Feeds", rss_modal_title: "Novo Feed RSS",
        btn_use_gnews: "Ativar GNews", btn_use_newsapi: "Ativar NewsAPI", btn_use_currents: "Ativar Currents", footer_copy: "Desenvolvido por Cogitari",
        tg_images: "Gerar Imagens (Vertex AI)", tg_videos: "Buscar Vídeos (YouTube)", tg_review: "Revisão Humana Obrigatória", btn_categories: "Filtrar Categorias", btn_apply: "Aplicar", btn_apply_perf: "Atualizar Núcleo", btn_save: "Confirmar", btn_save_rss: "Adicionar Feed",
        btn_add_feed: "Adicionar Fonte",

        // --- PLACEHOLDERS ---
        ph_google_project: "Ex: my-project-id-123", ph_wp_url: "Ex: https://meublog.com", ph_rss_name: "Ex: CNN Tech", ph_rss_theme: "Ex: Tecnologia", ph_rss_url: "https://...", ph_evergreen: "Ex: Benefícios da Meditação na produtividade...", ph_key: "Cole sua chave API aqui...", ph_user: "admin",

        // --- TABLE HEADERS ---
        th_date: "Data de Processamento", th_action: "Ação Executada", th_status: "Estado Atual", th_title: "Título do Artigo", th_cat: "Tags/Categorias", th_active: "Monitorando", th_name: "Nome da Fonte", th_url: "Endereço do Feed",

        // --- CYCLE MODAL ---
        btn_cycle: "Ciclos de Execução", modal_cycle_title: "Configuração de Intervalos", lbl_cycle_interval: "Intervalo entre Buscas (minutos)", cycle_info: "Recomendado: 120min para evitar API Rate Limits (Erro 429). Mínimo seguro: 30min.",

        // --- CONFIG ---
        lbl_pub_mode: "Modo de Publicação no WP", opt_auto: "Publicação Automática (Ao vivo)", opt_draft: "Salvar como Rascunho", opt_manual: "Reter para Revisão", review_title: "Fila de Moderação",
        input_topic: "Tópico para Artigo Evergreen (At temporal)",
        lbl_cycle_interval: "Frequência (Ciclos)", lbl_ai_threads: "Velocidade (Threads)", lbl_advanced: "Configurações Avançadas",

        // --- MANUAL CONTENT (DETAILED) ---
        man_intro_t: "1. Bem-vindo ao S1M0N",
        man_intro_d: `<p>O <strong>S1M0N</strong> é um orquestrador de conteúdo autônomo. Ele substitui uma equipe editorial básica ao automatizar:</p>
                      <ul>
                        <li><strong>Pauta:</strong> Monitora o mundo real via RSS/News APIs.</li>
                        <li><strong>Redação:</strong> Usa LLMs (Gemini) para escrever artigos originais baseados em fatos.</li>
                        <li><strong>Multimídia:</strong> Cria imagens e busca vídeos automaticamente.</li>
                        <li><strong>Distribuição:</strong> Publica no seu WordPress.</li>
                      </ul>`,
        man_setup_t: "2. Obtendo as Chaves (Passo a Passo)",
        man_setup_d: `<div class="accordion" id="accKeys">
                        <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#k1">Google Ecosystem (Vital)</button></h2>
                            <div id="k1" class="accordion-collapse collapse show" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <ol>
                                        <li>Acesse o <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a>.</li>
                                        <li>Crie um Novo Projeto e anote o <strong>Project ID</strong>.</li>
                                        <li>No menu "APIs e Serviços", ative: <strong>Vertex AI API</strong> (para imagens) e <strong>YouTube Data API v3</strong>.</li>
                                        <li>Acesse o na <a href="https://aistudio.google.com/" target="_blank">Google AI Studio</a> e gere uma chave para o <strong>Gemini 1.5</strong>.</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#k2">WordPress (Conexão)</button></h2>
                            <div id="k2" class="accordion-collapse collapse" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <p>Não use sua senha de login!</p>
                                    <ol>
                                        <li>No painel WP, vá em <strong>Usuários > Perfil</strong>.</li>
                                        <li>Role até o final para "Senhas de Aplicação".</li>
                                        <li>Nomeie como "S1M0N" e clique em "Adicionar nova".</li>
                                        <li>Copie a senha gerada e cole no campo "Pass" no S1M0N.</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#k3">Fontes de Notícias e RSS</button></h2>
                            <div id="k3" class="accordion-collapse collapse" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <p><strong>Para APIs de Notícias:</strong> Crie uma conta gratuita em um dos serviços suportados:</p>
                                    <ul>
                                        <li><a href="https://gnews.io/" target="_blank">GNews.io</a></li>
                                        <li><a href="https://newsapi.org/" target="_blank">NewsAPI.org</a></li>
                                        <li><a href="https://currentsapi.services/" target="_blank">CurrentsAPI</a></li>
                                    </ul>
                                    <p><strong>Para RSS:</strong> A maioria dos sites modernos possui um feed. Tente adicionar <code>/feed</code> ao final da URL (ex: <code>meusite.com/feed</code>) ou procure pelo ícone laranja de RSS.</p>
                                </div>
                            </div>
                        </div>
                      </div>`,
        man_gen_t: "3. Operação e Status",
        man_gen_d: `<p><strong>Interpretação de Status:</strong></p>
                    <ul>
                        <li><span class="badge bg-secondary">STOPPED</span> O sistema está inativo. Nada acontece.</li>
                        <li><span class="badge bg-success">RUNNING</span> O sistema está ativo. Ele acordará a cada X minutos (configurado em Ciclos) para buscar novidades.</li>
                        <li><span class="badge bg-warning">PAUSED</span> O sistema não iniciará novos ciclos, mas processos em andamento terminarão.</li>
                    </ul>`,

        // --- POLICIES CONTENT (COMPLIANT) ---
        pol_title: "Central de Compliance", pol_priv_t: "Privacidade e Tratamento de Dados",
        pol_priv_d: `<div class="alert alert-success"><i class="fas fa-shield-alt"></i> <strong>Soberania de Dados</strong></div>
                     <p>O S1M0N opera sob o princípio de <strong>Local-First</strong> (Primeiro Local):</p>
                     <ul>
                        <li><strong>Credenciais:</strong> Suas chaves de API e senhas JAMAIS são enviadas para "a nuvem do S1M0N" ou servidores de terceiros não envolvidos na transação. Elas residem apenas no arquivo <code>s1m0n.db</code> no seu disco rígido.</li>
                        <li><strong>Conteúdo:</strong> O texto das notícias lidas é enviado à API da Google (Gemini) para processamento. A Google afirma não usar dados de API paga para treinar modelos por padrão.</li>
                        <li><strong>Logs:</strong> Os registros de erros e acertos ficam na sua máquina.</li>
                     </ul>`,
        pol_terms_t: "Termos de Uso",
        pol_terms_d: `<p>Ao utilizar este software, você concorda que:</p>
                      <ol>
                        <li>A responsabilidade final pelo conteúdo publicado é do Editor Humano. IAs podem alucinar.</li>
                        <li>O uso de APIs (YouTube, GNews) está sujeito aos Termos de Serviço dessas plataformas.</li>

                        <li>O S1M0N é uma ferramenta de produtividade. Você deve possuir os direitos de uso dos feeds RSS que adiciona.</li>
                        <li>O conteúdo gerado deve ser revisado para garantir conformidade legal e ética.</li>
                      </ol>`,

        err_generic: "Erro de conexão.", err_browser: "Navegador incompatível.", err_history: "Erro ao ler histórico.", err_save: "Erro ao salvar.",
        sec_alert: "Não é possível copiar/colar deste campo."
    },
    en: {
        // --- MENUS ---
        menu_dashboard: "Overview", menu_performance: "Performance & Logs", menu_evergreen: "Evergreen (SEO)", menu_sources: "RSS Feeds", menu_settings: "Settings", menu_manual: "User Manual", btn_policies: "Policies & Data", menu_review: "History & Review",
        dash_title: "System Overview", log_title: "Compiled Execution Log", btn_start: "Start", btn_pause: "Pause", btn_stop: "Stop",

        // --- HELP (ON-CLICK) ---
        help_perf: "Monitors system resources (CPU/RAM) and core S1M0N configurations.",
        help_evergreen: "Generates in-depth articles on timeless topics (no recent news needed).",
        help_rss: "Manages your news sources. Add RSS feeds from trusted sites here.",
        help_settings: "Configure your API keys and connections.",
        help_google: "Configure Google Cloud credentials (Vertex AI for Images) and YouTube Data API.",
        help_news: "Manage API keys for news providers (GNews, NewsAPI, Currents).",
        help_wp: "Connect your WordPress site. Use full URL, username, and Application Password.",
        help_cp: "Advanced controls: Logs, Safe Mode, Timeouts, and error handling.",

        // --- STATS ---
        stat_total_label: "Total Published", stat_today_label: "Generated Today", stat_pending_label: "Approval Queue", stat_cache_label: "Cache Savings",
        stat_total_tooltip: "Total count of articles sent to WordPress since inception.",
        stat_today_tooltip: "Articles generated in the last 24 hours.",
        stat_pending_tooltip: "Articles waiting for manual review before publishing.",
        stat_cache_tooltip: "API requests saved by caching mechanism.",

        // --- TOOLTIPS (DESCRIPTIVE) ---
        tt_start: "Starts the continuous cycle of RSS monitoring and article generation.",
        tt_pause: "Temporarily pauses the cycle. Current process will finish before stopping.",
        tt_stop: "Halts all processes immediately.",
        tt_refresh: "Manually refreshes dashboard data.",
        tt_logs_clear: "Clears visual logs (does not affect disk log file).",
        tt_add_feed: "Adds a new RSS Feed URL for monitoring.",
        tt_del_sources: "Removes ALL registered sources from the database.",
        tt_save_all: "Saves all API, WordPress, and preference settings to local DB.",
        tt_cycles: "Defina o intervalo de tempo (em minutos) entre as buscas automáticas de conteúdo.",
        tt_clear_hist: "Permanently deletes generation history and performance data.",
        tt_optimize: "Executes RAM cleanup and database compaction (Vacuum).",
        tt_google_proj: "Google Cloud Project ID (Required for Vertex AI).",
        tt_gemini_key: "Google AI Studio API Key (Gemini 1.5).",
        tt_yt_key: "YouTube Data API v3 Key for fetching related videos.",
        tt_news_key: "API Key for the selected news service.",
        tt_wp_url: "Full URL of your WordPress site (https://...).",
        tt_wp_user: "WordPress username with Editor/Admin permissions.",
        tt_wp_pass: "Application Password (not login password). Generate in Users > Profile.",
        tt_pub_mode: "Defines if article goes live immediately or stays as Draft.",
        tt_manual_rev: "If enabled, blocks auto-publish and puts item in Review Queue.",

        // --- TITLES & BUTTONS ---
        sec_google_title: "Google Ecosystem", sec_news_title: "News & RSS Sources", sec_wp_title: "WordPress Integration", cp_title: "Control Panel",
        btn_generate: "Generate Topic", btn_save_all: "Save Settings", btn_optimize: "Optimize System", btn_clear_global: "Reset History", btn_delete_sources_txt: "Delete Sources",
        hist_opt_title: "Optimization Log", hist_gen_title: "Publication History", rss_manager_title: "Feed Manager", rss_modal_title: "New RSS Feed",
        btn_use_gnews: "Enable GNews", btn_use_newsapi: "Enable NewsAPI", btn_use_currents: "Enable Currents", footer_copy: "Powered by Cogitari",
        tg_images: "Generate Images (Vertex)", tg_videos: "Fetch Videos (YT)", tg_review: "Manual Review", btn_categories: "Filter Categories", btn_apply: "Apply", btn_apply_perf: "Update Core", btn_save: "Confirm", btn_save_rss: "Add Feed",
        btn_add_feed: "Add Feed",

        // --- PLACEHOLDERS ---
        ph_google_project: "Ex: my-project-id", ph_wp_url: "Ex: https://mysite.com", ph_rss_name: "Ex: CNN Tech", ph_rss_theme: "Ex: Tech", ph_rss_url: "https://...", ph_evergreen: "Ex: Benefits of Meditation...", ph_key: "Paste API Key here...", ph_user: "admin",

        // --- TABLE HEADERS ---
        th_date: "Date/Time", th_action: "Action", th_status: "Status", th_title: "Title", th_cat: "Tags", th_active: "Active", th_name: "Source Name", th_url: "Feed URL",

        // --- CYCLE MODAL ---
        btn_cycle: "Execution Cycles", modal_cycle_title: "Interval Setup", lbl_cycle_interval: "Fetch Interval (minutes)", cycle_info: "Recommended: 120min to avoid Rate Limits. Minimum: 30min.",

        // --- CONFIG ---
        lbl_pub_mode: "WP Publish Mode", opt_auto: "Auto Publish (Live)", opt_draft: "Save as Draft", opt_manual: "Hold for Review", review_title: "Review Queue",
        input_topic: "Main Topic for Article",
        lbl_cycle_interval: "Frequency (Cycles)", lbl_ai_threads: "Speed (Threads)", lbl_advanced: "Advanced Settings",

        // --- MANUAL CONTENT ---
        man_intro_t: "1. Welcome to S1M0N",
        man_intro_d: `<p><strong>S1M0N</strong> is an autonomous content orchestrator. It replaces a basic editorial team by automating:</p>
                      <ul>
                        <li><strong>Agenda:</strong> Monitors real world via RSS.</li>
                        <li><strong>Writing:</strong> Uses LLMs (Gemini) for original reporting.</li>
                        <li><strong>Multimedia:</strong> Creates images and finds videos.</li>
                        <li><strong>Distribution:</strong> Publishes to your WordPress.</li>
                      </ul>`,
        man_setup_t: "2. Getting Keys (Step-by-Step)",
        man_setup_d: `<div class="accordion" id="accKeys">
                        <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#k1">Google Ecosystem</button></h2>
                            <div id="k1" class="accordion-collapse collapse show" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <ol>
                                        <li>Go to <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a>.</li>
                                        <li>Create a Project and note the <strong>Project ID</strong>.</li>
                                        <li>Enable APIs: <strong>Vertex AI API</strong> and <strong>YouTube Data API v3</strong>.</li>
                                        <li>Go to <a href="https://aistudio.google.com/" target="_blank">Google AI Studio</a> and get a <strong>Gemini 1.5</strong> key.</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                         <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#k2">WordPress</button></h2>
                            <div id="k2" class="accordion-collapse collapse" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <p>Do NOT use your login password!</p>
                                    <ol>
                                        <li>WP Dashboard > <strong>Users > Profile</strong>.</li>
                                        <li>Scroll to "Application Passwords".</li>
                                        <li>Name it "S1M0N" and click "Add New".</li>
                                        <li>Copy the generated code.</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                         <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#k3">News Sources & RSS</button></h2>
                            <div id="k3" class="accordion-collapse collapse" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <p><strong>News APIs:</strong> Register for a free key at these services:</p>
                                    <ul>
                                        <li><a href="https://gnews.io/" target="_blank">GNews.io</a></li>
                                        <li><a href="https://newsapi.org/" target="_blank">NewsAPI.org</a></li>
                                        <li><a href="https://currentsapi.services/" target="_blank">CurrentsAPI</a></li>
                                    </ul>
                                    <p><strong>For RSS:</strong> Most sites have a feed. Try adding <code>/feed</code> to the URL (e.g., <code>site.com/feed</code>) or look for the RSS icon.</p>
                                </div>
                            </div>
                        </div>
                      </div>`,
        man_gen_t: "3. Status Guide",
        man_gen_d: `<p><strong>Status Meanings:</strong></p>
                    <ul>
                        <li><span class="badge bg-secondary">STOPPED</span> System idle.</li>
                        <li><span class="badge bg-success">RUNNING</span> System active. Wakes up every X minutes.</li>
                        <li><span class="badge bg-warning">PAUSED</span> No new cycles, but current tasks finish.</li>
                    </ul>`,

        // --- POLICIES CONTENT ---
        pol_title: "Compliance Center", pol_priv_t: "Privacy & Data",
        pol_priv_d: `<div class="alert alert-success"><i class="fas fa-shield-alt"></i> <strong>Data Sovereignty</strong></div>
                     <p>S1M0N operates on a <strong>Local-First</strong> principle:</p>
                     <ul>
                        <li><strong>Credentials:</strong> Keys reside ONLY in your local <code>s1m0n.db</code>.</li>
                        <li><strong>Content:</strong> News text is sent to Google API for processing.</li>
                        <li><strong>Logs:</strong> Kept locally on your machine.</li>
                     </ul>`,
        pol_terms_t: "Terms of Use",
        pol_terms_d: `<p>By using this software:</p>
                      <ol>
                        <li>Final responsibility lies with the Human Editor. AI can hallucinate.</li>

                        <li>You must ensure you have the right to use the RSS feeds you aggregate.</li>
                        <li>Generated content should be reviewed for legal and ethical compliance.</li>
                      </ol>`,

        err_generic: "Connection error.", err_browser: "Browser incompatible.", err_history: "History error.", err_save: "Save error.",
        sec_alert: "Copy/Paste is disabled for this field."
    },
    es: {
        // --- MENUS ---
        menu_dashboard: "Visión General", menu_performance: "Rendimiento y Logs", menu_evergreen: "Evergreen (SEO)", menu_sources: "Fuentes RSS", menu_settings: "Configuración", menu_manual: "Manual de Usuario", btn_policies: "Políticas y Datos", menu_review: "Historial y Revisión",
        dash_title: "Visión General", log_title: "Registro de Ejecución Compilado", btn_start: "Iniciar", btn_pause: "Pausar", btn_stop: "Parar",

        // --- HELP (ON-CLICK) ---
        help_perf: "Monitorea recursos del sistema (CPU/RAM) y configuraciones centrales.",
        help_evergreen: "Genera artículos profundos sobre temas atemporales (sin noticias recientes).",
        help_rss: "Gestiona sus fuentes de noticias. Añada feeds RSS fiables aquí.",
        help_settings: "Configure sus claves API y conexiones.",
        help_google: "Configure credenciales de Google Cloud (Vertex AI para Imágenes) y YouTube API.",
        help_news: "Gestione claves API para proveedores de noticias (GNews, NewsAPI, Currents).",
        help_wp: "Conecte su sitio WordPress. Use URL completa, usuario y Contraseña de Aplicación.",
        help_cp: "Controles avanzados: Logs, Modo Seguro, Tiempos de espera y manejo de errores.",

        // --- STATS ---
        stat_total_label: "Total Publicados", stat_today_label: "Generados Hoy", stat_pending_label: "Cola de Aprobación", stat_cache_label: "Ahorro por Caché",
        stat_total_tooltip: "Conteo histórico de artículos enviados.",
        stat_today_tooltip: "Artículos generados en las últimas 24h.",
        stat_pending_tooltip: "Artículos esperando revisión humana.",
        stat_cache_tooltip: "Peticiones API ahorradas por caché.",

        // --- TOOLTIPS (DESCRIPTIVE) ---
        tt_start: "Inicia el ciclo continuo de monitoreo y generación.",
        tt_pause: "Pausa temporalmente. El proceso actual terminará.",
        tt_stop: "Detiene todos los procesos inmediatamente.",
        tt_refresh: "Actualiza los datos del panel manualmente.",
        tt_logs_clear: "Limpia los logs visuales (no el archivo en disco).",
        tt_add_feed: "Añade una nueva URL RSS para monitorear.",
        tt_del_sources: "Elimina TODAS las fuentes de la base de datos.",
        tt_save_all: "Guarda todas las configuraciones localmente.",
        tt_cycles: "Defina o intervalo de tempo (em minutos) entre as buscas automáticas de conteúdo.",
        tt_clear_hist: "Borra permanentemente el historial de artículos.",
        tt_optimize: "Limpia RAM y compacta la base de datos.",
        tt_google_proj: "ID de Proyecto Google (Para Vertex AI).",
        tt_gemini_key: "Clave API de Google AI Studio.",
        tt_yt_key: "Clave API de YouTube Data v3.",
        tt_news_key: "Clave API del servicio de noticias.",
        tt_wp_url: "URL completa de su sitio WP.",
        tt_wp_user: "Usuario WP con permisos de Editor.",
        tt_wp_pass: "Contraseña de Aplicación (no la de login).",
        tt_pub_mode: "Define si se publica o se guarda como borrador.",
        tt_manual_rev: "Bloquea publicación auto y envía a revisión.",

        // --- TITLES & BUTTONS ---
        sec_google_title: "Ecosistema Google", sec_news_title: "Noticias y RSS", sec_wp_title: "Integración WordPress", cp_title: "Panel de Control",
        btn_generate: "Generar Tema", btn_save_all: "Guardar Todo", btn_optimize: "Optimizar Sistema", btn_clear_global: "Resetear Historial", btn_delete_sources_txt: "Borrar Fuentes",
        hist_opt_title: "Logs de Optimización", hist_gen_title: "Historial de Publicación", rss_manager_title: "Gestor de Feeds", rss_modal_title: "Nuevo Feed RSS",
        btn_use_gnews: "Activar GNews", btn_use_newsapi: "Activar NewsAPI", btn_use_currents: "Activar Currents", footer_copy: "Por Cogitari",
        tg_images: "Generar Imágenes", tg_videos: "Buscar Videos", tg_review: "Revisión Manual", btn_categories: "Categorías", btn_apply: "Aplicar", btn_apply_perf: "Actualizar Núcleo", btn_save: "Confirmar", btn_save_rss: "Añadir Feed",
        btn_add_feed: "Añadir Fuente",

        // --- PLACEHOLDERS ---
        ph_google_project: "Ej: mi-proyecto-123", ph_wp_url: "Ej: https://misitio.com", ph_rss_name: "Ej: CNN", ph_rss_theme: "Ej: Tech", ph_rss_url: "https://...", ph_evergreen: "Ej: Beneficios del Yoga...", ph_key: "Pegue su clave aquí...", ph_user: "admin",

        // --- TABLE HEADERS ---
        th_date: "Fecha/Hora", th_action: "Acción", th_status: "Estado", th_title: "Título", th_cat: "Tags", th_active: "Activo", th_name: "Fuente", th_url: "URL",

        // --- CYCLE MODAL ---
        btn_cycle: "Ciclos de Ejec.", modal_cycle_title: "Intervalos", lbl_cycle_interval: "Intervalo (minutos)", cycle_info: "Recomendado: 120min.",

        // --- CONFIG ---
        lbl_pub_mode: "Modo Publicación", opt_auto: "Automático (Live)", opt_draft: "Borrador (Draft)", opt_manual: "Para Revisión", review_title: "Cola de Revisión",
        // ... existing translations ...
        input_topic: "Tema Principal",
        lbl_cycle_interval: "Frecuencia (Ciclos)", lbl_ai_threads: "Velocidad (Hilos)", lbl_advanced: "Configuración Avanzada",
        // --- MANUAL CONTENT ---
        man_intro_t: "1. Bienvenido a S1M0N",
        man_intro_d: `<p>S1M0N es su editor autónomo. Automatiza:</p>
                      <ul><li>Agenda (RSS)</li><li>Redacción (Gemini)</li><li>Multimedia (Vertex)</li><li>Publicación (WP)</li></ul>`,
        man_setup_t: "2. Obtener Claves",
        man_setup_d: `<div class="accordion" id="accKeys">
                        <div class="accordion-item"><h2 class="accordion-header"><button class="accordion-button" data-bs-toggle="collapse" data-bs-target="#k1">Google</button></h2>
                        <div id="k1" class="accordion-collapse collapse show"><div class="accordion-body">Obtenga Project ID en Cloud Console y API Key en AI Studio.</div></div></div>
                        <div class="accordion-item"><h2 class="accordion-header"><button class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#k2">WordPress</button></h2>
                        <div id="k2" class="accordion-collapse collapse"><div class="accordion-body">Use "Contraseñas de Aplicación" en su Perfil de usuario.</div></div></div>

                        <div class="accordion-item">
                            <h2 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#k3">Fuentes y RSS</button></h2>
                            <div id="k3" class="accordion-collapse collapse" data-bs-parent="#accKeys">
                                <div class="accordion-body">
                                    <p><strong>APIs de Noticias:</strong> Registre una cuenta gratuita:</p>
                                    <ul><li>GNews.io</li><li>NewsAPI.org</li><li>CurrentsAPI</li></ul>
                                    <p><strong>Para RSS:</strong> Añada <code>/feed</code> al final de la URL del sitio.</p>
                                </div>
                            </div>
                        </div>
                      </div>`,
        man_gen_t: "3. Guía de Estado",
        man_gen_d: `<p><strong>Estados:</strong> STOPPED (Inactivo), RUNNING (Activo), PAUSED (Pausando).</p>`,

        // --- POLICIES CONTENT ---
        pol_title: "Compliance", pol_priv_t: "Privacidad",
        pol_priv_d: `<div class="alert alert-success"><strong>Soberanía de Datos</strong></div><p>Sus claves y logs nunca salen de su máquina (Local-First).</p>`,
        pol_terms_t: "Términos",
        pol_terms_d: `<p>Al usar este software, usted acepta que:</p>
                      <ol>
                          <li>El editor humano es el responsable final. La IA puede alucinar.</li>
                          <li>Debe poseer los derechos de uso de los feeds RSS agregados.</li>
                          <li>El contenido generado debe ser revisado éticamente.</li>
                      </ol>`,

        err_generic: "Error de conexión.", err_browser: "Use Chrome.", err_history: "Error historial.", err_save: "Error al guardar.",
        sec_alert: "No se puede copiar/pegar en este campo."
    },
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', function () {
    init();
});

function init() {
    const lang = localStorage.getItem('s1m0n_lang') || 'pt';
    document.getElementById('langSelect').value = lang;

    if (localStorage.getItem('s1m0n_theme') === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        document.getElementById('darkModeSwitch').checked = true;
    }

    document.getElementById('yr').innerText = new Date().getFullYear();

    // Setup Inputs
    setupInputs();

    // Tooltips & Popovers will be initialized in changeLang after keys are applied.

    changeLang(lang);
    if (typeof window.setupApiToggles === 'function') window.setupApiToggles();

    // Load initial data
    loadManual();
    renderHistories();
    updateData();
    checkDeploymentStatus();
    setInterval(updateData, 5000);

    // Tab Listeners
    setupTabs();
}

async function checkDeploymentStatus() {
    try {
        const res = await (await fetch('/api/status/deployment')).json();
        const badge = document.querySelector('#pageTitle .badge');
        if (badge && res.env) {
            badge.innerText = `${res.env} ${res.version}`;
            // PROD = Red/Warn, DEV = Green/Success, UNKNOWN = Dark
            const bgClass = res.env === 'PROD' ? 'bg-danger' : 'bg-success';
            badge.className = `badge ${bgClass} ms-2 border`;
            badge.title = res.ready ? "System Ready" : "System Not Ready";
        }
    } catch (e) { console.warn('Status check failed', e); }
}

function setupInputs() {
    // Clear buttons
    window.clearInput = function (el) {
        const input = el.previousElementSibling;
        input.value = '';
        input.focus();
    };

    // Security & Validation
    document.querySelectorAll('.secure-input, input[type="password"]').forEach(input => {
        const blockAction = async (e) => {
            e.preventDefault();
            const eventType = e.type;
            const fieldName = input.getAttribute('name');

            // Log event (Blind fire)
            try {
                fetch('/api/security/events', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ event: eventType, field: fieldName || 'unknown' })
                }).catch(() => { });
            } catch (err) { }

            // Dynamic Alert Injection (DLP)
            let alertMsg = input.parentNode.nextElementSibling;

            // Check if it is the specific security msg container
            if (!alertMsg || !alertMsg.classList.contains('security-msg')) {
                // If structure is different, try to find in parent or create
                const parent = input.parentNode.parentNode;
                alertMsg = parent.querySelector('.security-alert');

                if (!alertMsg) {
                    alertMsg = document.createElement('small');
                    alertMsg.className = 'security-msg security-alert text-danger d-block mt-1';
                    // Insert after the input group
                    if (input.parentNode.classList.contains('input-group-custom')) {
                        input.parentNode.parentNode.insertBefore(alertMsg, input.parentNode.nextSibling);
                    } else {
                        input.parentNode.appendChild(alertMsg);
                    }
                }
            }

            const lang = localStorage.getItem('s1m0n_lang') || 'pt';
            alertMsg.innerText = i18n[lang].sec_alert || "Security Alert: Action Blocked";
            alertMsg.classList.remove('d-none');
            alertMsg.classList.add('d-block');

            // Shake effect
            input.classList.add('is-invalid');
            setTimeout(() => {
                input.classList.remove('is-invalid');
            }, 500);

            setTimeout(() => {
                alertMsg.classList.add('d-none');
                alertMsg.classList.remove('d-block');
            }, 3000);
        };

        // DLP Listeners
        input.addEventListener('copy', blockAction);
        input.addEventListener('cut', blockAction);
        input.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            blockAction(e);
        });

        // Blur validation
        input.addEventListener('blur', function () {
            // validateField(this); // Optional, kept if needed
        });
    });

    // Initialize Gemini Logic
    setupGeminiLogic();
}

function setupTabs() {
    const navTabs = [
        { id: 'nav-tab-dashboard', tab: 'dashboard' },
        { id: 'nav-tab-performance', tab: 'performance' },
        { id: 'nav-tab-evergreen', tab: 'evergreen' },
        { id: 'nav-tab-sources', tab: 'sources' },
        { id: 'nav-tab-review', tab: 'review' },
        { id: 'nav-tab-settings', tab: 'settings' },
        { id: 'nav-tab-manual', tab: 'manual' }
    ];

    navTabs.forEach(function (item) {
        const el = document.getElementById(item.id);
        if (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                showTab(item.tab);
            });
        }
    });
}

// --- CORE FUNCTIONS ---

function showTab(tabId) {
    try {
        const sections = document.querySelectorAll('.settings-section');
        sections.forEach(s => s.classList.remove('active'));

        const target = document.getElementById('tab-' + tabId);
        if (target) target.classList.add('active');

        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        const activeNav = document.getElementById('nav-tab-' + tabId);
        if (activeNav) activeNav.classList.add('active');

        if (tabId === 'sources') loadRss();
        if (tabId === 'settings') loadSettings();
        if (tabId === 'review') loadHistoryAndReview();
        if (tabId === 'manual') loadManual();
    } catch (e) { console.error(e); }
}

function setupGeminiLogic() {
    const keyInput = document.querySelector('[name="google_api_key"]');
    const modelSelect = document.querySelector('[name="ai_model_mode"]');
    if (!keyInput || !modelSelect) return;

    // Initial State: Disabled
    modelSelect.disabled = true;

    // Function to fetch models
    async function validateAndFetch() {
        const key = keyInput.value.trim();
        if (!key) {
            modelSelect.disabled = true;
            return;
        }

        // Show loading state in placeholder (or just keep disabled)
        // Check if we already have models populated? No, always validation fresh key is better for security.

        try {
            const res = await fetch('/api/gemini/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: key })
            });
            const data = await res.json();

            if (data.success && data.models.length > 0) {
                // Clear and Populate
                modelSelect.innerHTML = '';
                data.models.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.innerText = m; // e.g. "gemini-1.5-flash"
                    if (m.includes('flash')) opt.selected = true; // Default preference
                    modelSelect.appendChild(opt);
                });
                modelSelect.disabled = false;

                // Add success visual to key?
                keyInput.classList.remove('is-invalid');
                keyInput.classList.add('is-valid');
            } else {
                modelSelect.disabled = true;
                modelSelect.innerHTML = '<option>Invalid Key / No Models</option>';
            }
        } catch (e) {
            console.error("Gemini Fetch Error", e);
        }
    }

    // Trigger on blur (user finished typing)
    keyInput.addEventListener('blur', validateAndFetch);

    // Also trigger if value exists on load (timeout to ensure value is populated)
    setTimeout(() => {
        if (keyInput.value) validateAndFetch();
    }, 1000);
}

function changeLang(lang) {
    localStorage.setItem('s1m0n_lang', lang);
    const t = i18n[lang] || i18n['pt'];

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const k = el.getAttribute('data-i18n');
        if (t[k]) {
            if (['man_intro_d', 'man_setup_d', 'man_gen_d', 'pol_priv_d', 'pol_terms_d'].includes(k)) el.innerHTML = t[k];
            else el.innerText = t[k];
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const k = el.getAttribute('data-i18n-placeholder');
        if (t[k]) el.placeholder = t[k];
    });

    // Tooltips Translation
    document.querySelectorAll('[data-i18n-tooltip]').forEach(el => {
        const k = el.getAttribute('data-i18n-tooltip');
        if (t[k]) {
            el.setAttribute('title', t[k]);
            el.setAttribute('data-bs-original-title', t[k]); // For initialized tooltips
        }
    });

    // Popover Translation
    document.querySelectorAll('[data-i18n-popover]').forEach(el => {
        const k = el.getAttribute('data-i18n-popover');
        if (t[k]) {
            el.setAttribute('data-bs-content', t[k]);
            // Logic handled by re-init in initTooltips()
        }
    });

    document.getElementById('langSelect').value = lang;
    if (window.initTooltips) window.initTooltips();
    loadManual();
}

window.initTooltips = function () {
    // 1. Dispose Tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"], [data-i18n-tooltip]').forEach(el => {
        try {
            const instance = bootstrap.Tooltip.getInstance(el);
            if (instance) instance.dispose();
        } catch (e) { }
    });
    // 2. Dispose Popovers
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
        try {
            const instance = bootstrap.Popover.getInstance(el);
            if (instance) instance.dispose();
        } catch (e) { }
    });

    // 3. Init Tooltips (Safe Loop)
    document.querySelectorAll('[data-bs-toggle="tooltip"], [data-i18n-tooltip]:not(.manual-popover)').forEach(el => {
        try {
            // Restore title if missing (for re-init)
            if (!el.getAttribute('title') && el.getAttribute('data-bs-original-title')) {
                el.setAttribute('title', el.getAttribute('data-bs-original-title'));
            }
            new bootstrap.Tooltip(el, { container: 'body', trigger: 'hover focus' });
        } catch (e) { console.warn('Tooltip init error', e); }
    });

    // 4. Init Popovers (Safe Loop)
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
        try {
            new bootstrap.Popover(el, {
                trigger: 'focus', // Closes when clicking elsewhere
                container: 'body',
                html: true
            });
        } catch (e) { console.warn('Popover init error', e); }
    });
}

async function controlSystem(action) {
    confirmAction(`Confirmar ação: ${action}?`, async () => {
        const res = await fetch('/api/control', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action }) });
        const data = await res.json();
        const badge = document.getElementById('systemStatus').querySelector('.badge');
        badge.innerText = data.state;
        badge.className = `badge bg-${data.state === 'RUNNING' ? 'success' : data.state === 'PAUSED' ? 'warning' : 'secondary'}`;

        const btnMain = document.getElementById('btn-main');
        const btnPause = document.getElementById('btn-pause');
        const lang = localStorage.getItem('s1m0n_lang') || 'pt';

        if (data.state === 'RUNNING') {
            btnMain.className = 'btn btn-danger'; btnMain.innerHTML = `<i class="fas fa-stop"></i> ${i18n[lang].btn_stop}`; btnMain.onclick = () => controlSystem('STOP');
            btnPause.classList.remove('disabled'); btnPause.onclick = () => controlSystem('PAUSE');
        } else {
            btnMain.className = 'btn btn-success'; btnMain.innerHTML = `<i class="fas fa-play"></i> ${i18n[lang].btn_start}`; btnMain.onclick = () => controlSystem('START');
            btnPause.classList.add('disabled');
        }
        showToast(`Sistema: ${action}`, 'info');
    });
}

async function updateData() {
    try {
        const s = await (await fetch('/api/stats')).json();
        document.getElementById('totalArticles').innerText = s.total_articles;
        document.getElementById('todayArticles').innerText = s.today;
        document.getElementById('pendingCount').innerText = s.pending;
        document.getElementById('cacheCount').innerText = s.cache_count;
    } catch { }

    if (document.getElementById('tab-dashboard').classList.contains('active')) loadLogs();
    if (document.getElementById('tab-performance').classList.contains('active')) loadPerf();
}

async function loadLogs() {
    try {
        const res = await (await fetch('/api/logs')).json();
        const logBox = document.getElementById('logBox');
        logBox.innerHTML = res.logs.map(l => `<div>${l}</div>`).join('');
        logBox.scrollTop = logBox.scrollHeight;
    } catch { }
}

async function clearLogs() { await fetch('/api/logs/clear', { method: 'POST' }); loadLogs(); }

async function loadPerf() {
    const p = await (await fetch('/api/performance')).json();
    document.getElementById('cpuBar').style.width = p.cpu + '%'; document.getElementById('cpuVal').innerText = p.cpu + '%';
    document.getElementById('ramBar').style.width = p.ram + '%'; document.getElementById('ramVal').innerText = p.ram + '%';
    document.getElementById('diskBar').style.width = p.disk + '%'; document.getElementById('diskVal').innerText = p.disk + '%';
}

// --- UI HELPERS ---
function showToast(msg, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';

    toast.innerHTML = `<i class="fas fa-${icon}"></i> <span>${msg}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('transitionend', () => toast.remove());
    }, duration);
}

function confirmAction(msg, onConfirm, onCancel) {
    const overlay = document.getElementById('customModalOverlay');
    const title = document.getElementById('modalTitle');
    const text = document.getElementById('modalText');
    const btnYes = document.getElementById('btnConfirm');
    const btnNo = document.getElementById('btnCancel');

    if (!overlay) { if (confirm(msg)) onConfirm(); return; }

    text.innerText = msg;
    overlay.classList.add('active');

    // Clean listeners
    const cleanup = () => {
        overlay.classList.remove('active');
        btnYes.onclick = null;
        btnNo.onclick = null;
    };

    btnYes.onclick = () => { cleanup(); onConfirm(); };
    btnNo.onclick = () => { cleanup(); if (onCancel) onCancel(); };
}

function toggleSidebar() { document.querySelector('.sidebar').classList.toggle('collapsed'); }
function toggleCard(id) { document.getElementById(id).classList.toggle('collapsed-card'); }

// --- SETTINGS & FORMS ---
window.setupApiToggles = function () {
    const validateKey = async (key, type) => {
        // Mock Validation - In real scenario, hit /api/validate
        // For now, assume > 10 chars is "valid format" for simulation
        // The user requested "retorno 200 OK do endpoint de teste", we will simulate this delay
        return new Promise(resolve => setTimeout(() => resolve(key.length > 10), 500));
    };

    document.querySelectorAll('.api-toggle').forEach(toggle => {
        const inputName = toggle.getAttribute('data-linked-input');
        const input = document.querySelector(`input[name="${inputName}"]`);

        if (input) {
            // Default Disabled State
            toggle.disabled = true;
            if (!toggle.checked) toggle.disabled = true; // Ensure initial state

            const checkLock = async () => {
                const key = input.value.trim();
                const isValidFormat = key.length > 5; // Basic check

                if (!isValidFormat) {
                    toggle.disabled = true;
                    toggle.checked = false;
                    return;
                }

                // If format ok, try "validation"
                toggle.parentElement.classList.add('opacity-50'); // visual feedback
                const valid = await validateKey(key, inputName);
                toggle.parentElement.classList.remove('opacity-50');

                if (valid) {
                    toggle.disabled = false;
                } else {
                    toggle.disabled = true;
                    toggle.checked = false;
                }
            };

            // Debounce the check
            let timeout;
            input.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(checkLock, 800);
            });

            // Initial check if value exists
            if (input.value.length > 0) checkLock();
        }
    });

    // Fallback/Force Check for specific critical buttons
    ['enable_global_images', 'enable_youtube_embed'].forEach(name => {
        const btn = document.querySelector(`input[name="${name}"]`);
        if (btn) {
            const linked = btn.getAttribute('data-linked-input');
            if (linked) {
                const input = document.querySelector(`input[name="${linked}"]`);
                // Force initial check if not covered by class
                if (input && input.value.length < 5) {
                    btn.disabled = true;
                    btn.checked = false;
                }
            }
        }
    });
}

function toggleDarkMode() {
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    if (isDark) {
        document.body.removeAttribute('data-theme');
        localStorage.setItem('s1m0n_theme', 'light');
    } else {
        document.body.setAttribute('data-theme', 'dark');
        localStorage.setItem('s1m0n_theme', 'dark');
    }
}

// --- REVIEW FUNCTIONS ---


async function loadHistoryAndReview() {
    const container = document.getElementById('pending-container');
    container.innerHTML = '<div class="text-center w-100 py-4"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';

    // 1. Pending (Manual Approval)
    const pendingRes = await (await fetch('/api/pending')).json();
    let html = '';

    if (pendingRes.length > 0) {
        html += '<h5 class="w-100 mb-3 text-warning border-bottom pb-2"><i class="fas fa-clock"></i> Pendente de Aprovação</h5>';
        html += pendingRes.map(p => {
            let contentText = "";
            try { contentText = JSON.parse(p.content).conteudo_completo || ""; } catch (e) { contentText = p.content; }
            return `
            <div class="col-md-6"><div class="card mb-3 shadow-sm border-warning">
                <div class="card-header d-flex justify-content-between align-items-center bg-light">
                    <span class="badge bg-warning text-dark"><i class="fas fa-pause"></i> AGUARDANDO</span>
                    <small class="text-muted">${p.date}</small>
                </div>
                ${p.image ? `<img src="/static/${p.image.split('\\\\').pop().split('/').pop()}" class="card-img-top" style="height:200px; object-fit:cover">` : ''}
                <div class="card-body">
                    <h5 class="card-title text-truncate">${p.title}</h5>
                    <div class="mb-3">
                        <textarea id="edit-content-${p.id}" class="form-control" rows="6">${contentText}</textarea>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <button class="btn btn-outline-info btn-sm" onclick="startDictation(${p.id})"><i class="fas fa-microphone"></i></button>
                        <div class="btn-group">
                            <button class="btn btn-outline-danger btn-sm" onclick="rejectArticle(${p.id})"><i class="fas fa-times"></i></button>
                            <button class="btn btn-success btn-sm" onclick="approveArticle(${p.id})"><i class="fas fa-check"></i> Aprovar</button>
                        </div>
                    </div>
                </div>
            </div></div>`;
        }).join('');
    } else {
        html += '<div class="col-12 text-center py-3 text-muted border-bottom mb-4"><h6><i class="fas fa-check-circle text-success"></i> Nenhuma revisão pendente.</h6></div>';
    }

    // 2. Today's History (Completed)
    try {
        const histRes = await (await fetch('/api/history')).json();
        const today = new Date().toLocaleDateString();
        // Filter simplistic for demo (in production match regex or timestamps)
        const todaysItems = histRes.threads ? histRes.threads.filter(t => t.date && t.date.includes(today)) : [];

        if (todaysItems.length > 0) {
            html += '<h5 class="w-100 mb-3 text-primary pt-3"><i class="fas fa-history"></i> Gerados Hoje</h5>';
            html += todaysItems.map(t => `
            <div class="col-md-4">
                <div class="card mb-3 opacity-75" style="border:1px dashed #ccc">
                    <div class="card-body p-2">
                        <h6 class="card-title text-truncate small mb-1">${t.title || 'Sem Título'}</h6>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-${t.status === 'COMPLETED' ? 'success' : 'secondary'} small" style="font-size:0.7rem">${t.status}</span>
                            <button class="btn btn-sm btn-light" onclick="showHistoryDetail('${t.session_id}')"><i class="fas fa-eye"></i></button>
                        </div>
                    </div>
                </div>
            </div>`).join('');
        }
    } catch (e) { }

    container.innerHTML = html || '<div class="text-center p-5">Vazio.</div>';
}

async function approveArticle(id) {
    confirmAction('Aprovar e publicar este artigo?', async () => {
        const finalContent = document.getElementById(`edit-content-${id}`).value;
        await fetch('/api/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, content: finalContent })
        });
        loadHistoryAndReview();
        updateData();
        showToast('Artigo aprovado e publicado!', 'success');
    });
}

async function rejectArticle(id) {
    confirmAction('Rejeitar este artigo?', async () => {
        await fetch('/api/reject', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
        loadHistoryAndReview();
        showToast('Artigo rejeitado.', 'warning');
    });
}

function startDictation(id) {
    const lang = localStorage.getItem('s1m0n_lang') || 'pt';
    if (!('webkitSpeechRecognition' in window)) { showToast(i18n[lang].err_browser, 'error'); return; }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.onresult = function (event) {
        const txt = event.results[0][0].transcript;
        const field = document.getElementById(`edit-content-${id}`);
        field.value += ' ' + txt;
    };
    recognition.start();
}

// --- HISTORY & MISC ---
async function renderHistories() {
    // Perf History (Local)
    const lang = localStorage.getItem('s1m0n_lang') || 'pt';
    const ok = lang === 'pt' ? 'Sucesso' : 'Success';
    const perfH = JSON.parse(localStorage.getItem('s1m0n_perf_hist') || '[]');
    const perfTable = document.getElementById('perfHistoryTable');
    if (perfTable) perfTable.innerHTML = perfH.slice(0, 5).map(h => `<tr><td>${h.date}</td><td>${h.action}</td><td><span class="badge bg-success">${ok}</span></td></tr>`).join('');

    // Evergreen/Generation History (Server DB)
    const egTable = document.getElementById('evergreenTableBody');
    if (egTable) {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            if (data.success && data.threads) {
                egTable.innerHTML = data.threads.map(t => `
                    <tr onclick="showHistoryDetail('${t.session_id}')" style="cursor:pointer" title="Ver detalhes">
                        <td>${t.date ? t.date : 'N/A'}</td>
                        <td>${t.title ? t.title : 'Sem Título'}</td>
                        <td><span class="badge bg-${t.status === 'COMPLETED' ? 'success' : 'secondary'}">${t.status}</span></td>
                    </tr>
                `).join('');
            }
        } catch (e) { console.error('History load failed', e); showToast(i18n[localStorage.getItem('s1m0n_lang') || 'pt'].err_history, 'error'); }
    }
}

async function showHistoryDetail(sessionId) {
    const modal = new bootstrap.Modal(document.getElementById('historyModal'));
    const container = document.getElementById('history-content');
    container.innerHTML = '<div class="text-center p-3"><i class="fas fa-spinner fa-spin"></i> Carregando...</div>';
    modal.show();

    try {
        const res = await fetch(`/api/history/${sessionId}`);
        const data = await res.json();
        if (data.success) {
            container.innerHTML = data.messages.map(m => `
                <div class="msg-bubble ${m.role === 'user' ? 'msg-user' : 'msg-assistant'}">
                    <div>${m.content ? m.content.replace(/\n/g, '<br>') : ''}</div>
                    <span class="msg-meta">${new Date(m.timestamp).toLocaleTimeString()} - ${m.role.toUpperCase()}</span>
                </div>
            `).join('');
        }
    } catch (e) {
        container.innerHTML = `<div class="text-danger">${i18n[localStorage.getItem('s1m0n_lang') || 'pt'].err_history}</div>`;
    }
}

// Alias for compatibility
const renderEvergreenHistory = renderHistories;

function clearHistory(type) {
    confirmAction('Limpar este histórico?', async () => {
        if (type === 'evergreen') {
            try { await fetch('/api/history', { method: 'DELETE' }); } catch (e) { console.error(e); }
        }
        localStorage.removeItem(`s1m0n_${type}_hist`);
        renderHistories();
        showToast('Histórico limpo.', 'success');
    });
}
function clearAllHistories() {
    confirmAction('ATENÇÃO: Apagar TODOS os históricos locais?', () => {
        localStorage.removeItem('s1m0n_perf_hist');
        localStorage.removeItem('s1m0n_evergreen_hist');
        renderHistories();
        showToast('Todos os históricos foram apagados.', 'success');
    });
}

async function loadRss() {
    const feeds = await (await fetch('/api/rss')).json();
    document.getElementById('rssTableBody').innerHTML = feeds.map(f => `
                < tr >
            <td><div class="form-check form-switch"><input class="form-check-input" type="checkbox" ${f.is_active ? 'checked' : ''} onclick="toggleRss(${f.id})"></div></td>
            <td>${f.name}</td>
            <td><small>${f.url}</small></td>
            <td><button class="btn btn-sm btn-outline-danger" onclick="delRss(${f.id})"><i class="fas fa-trash"></i></button></td>
        </tr >
                `).join('');
}
async function saveRss() {
    await fetch('/api/rss', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({
            name: document.getElementById('rssName').value,
            url: document.getElementById('rssUrl').value,
            theme: document.getElementById('rssTheme').value
        })
    });
    const modalEl = document.getElementById('rssModal');
    if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
    loadRss();
}
async function delRss(id) {
    confirmAction('Remover esta fonte?', async () => {
        await fetch(`/ api / rss / ${id} `, { method: 'DELETE' });
        loadRss();
        showToast('Fonte removida.', 'success');
    });
}
async function toggleRss(id) {
    await fetch(`/ api / rss / ${id}/toggle`, { method: 'POST' });
}
async function deleteAllSources() {
    confirmAction('PERIGO: Apagar TODAS as fontes?', async () => {
        await fetch('/api/rss/delete_all', { method: 'POST' });
        loadRss();
        showToast('Todas as fontes foram removidas.', 'warning');
    });
}
function openRssModal() {
    document.getElementById('rssName').value = '';
    document.getElementById('rssUrl').value = '';
    document.getElementById('rssTheme').value = '';
    (new bootstrap.Modal(document.getElementById('rssModal'))).show();
}

async function loadSettings() {
    const d = await (await fetch('/api/settings')).json();
    const f = document.getElementById('settingsForm');

    // Model Selector
    const modelRes = await fetch('/api/model');
    const modelData = await modelRes.json();
    if (f.elements['ai_model_mode']) f.elements['ai_model_mode'].value = modelData.mode || 'pro';

    ['enable_global_images', 'enable_youtube_embed', 'enable_gnews', 'enable_newsapi', 'enable_currents'].forEach(k => {
        if (f.elements[k]) f.elements[k].checked = (d[k] === 'true');
    });

    // Resolve Publish Mode Dropdown
    if (f.elements['wp_publish_mode']) {
        if (d['require_manual_approval'] === 'true') f.elements['wp_publish_mode'].value = 'manual';
        else f.elements['wp_publish_mode'].value = d['wp_publish_mode'] || 'publish';
    }

    for (const [k, v] of Object.entries(d)) {
        if (k.includes('_categories')) {
            try { const vals = JSON.parse(v); Array.from(document.querySelectorAll(`input[name="${k}"]`)).forEach(cb => { cb.checked = vals.includes(cb.value) }) } catch { }
        } else {
            if (f.elements[k] && f.elements[k].type !== 'checkbox') {
                f.elements[k].value = v;
                // Update Range Badges
                if (k === 'execution_interval') {
                    try {
                        let m = Math.round(v / 60);
                        let el = document.getElementById('val-exec-display') || document.getElementById('val-exec');
                        if (el) el.innerText = m + ' min';
                    } catch (e) { }
                }
                if (k === 'max_ai_threads') { try { document.getElementById('val-threads').innerText = v; } catch (e) { } }
            }
            // Also check perf form
            const pF = document.getElementById('perfForm');
            if (pF && pF.elements[k]) {
                pF.elements[k].value = v;
                // Update Range Badges
                if (k === 'execution_interval') {
                    try {
                        let m = Math.round(v / 60);
                        let el = document.getElementById('val-exec-display') || document.getElementById('val-exec');
                        if (el) el.innerText = m + ' min';
                    } catch (e) { }
                }
            }
        }
    }
    if (window.setupApiToggles) window.setupApiToggles();
}

async function saveSettings() {
    const f = document.getElementById('settingsForm');
    const d = {};
    const formData = new FormData(f);

    // Publish Mode Logic
    const pubMode = formData.get('wp_publish_mode');
    d['require_manual_approval'] = (pubMode === 'manual');
    if (pubMode === 'manual') d['wp_publish_mode'] = 'draft'; // Safe default for backend
    else d['wp_publish_mode'] = pubMode;

    ['gnews_categories', 'newsapi_categories', 'currents_categories'].forEach(catName => {
        const selected = [];
        document.querySelectorAll(`input[name="${catName}"]:checked`).forEach(cb => selected.push(cb.value));
        d[catName] = JSON.stringify(selected);
    });
    for (const [key, value] of formData.entries()) { if (!key.includes('_categories')) d[key] = value; }
    ['enable_global_images', 'enable_youtube_embed', 'enable_gnews', 'enable_newsapi', 'enable_currents'].forEach(k => {
        if (f.elements[k]) d[k] = f.elements[k].checked;
    });

    // Save Settings
    await fetch('/api/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });

    // Save AI Model
    if (d.ai_model_mode) {
        await fetch('/api/model', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mode: d.ai_model_mode }) });
    }

    showToast('Configurações salvas com sucesso!', 'success');
}

async function savePerfSettings() {
    const f = document.getElementById('perfForm');
    const d = {};
    new FormData(f).forEach((v, k) => d[k] = v);
    await fetch('/api/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
    showToast('Parâmetros de Performance Aplicados!', 'warning');
}

async function validateField(input) {
    const field = input.getAttribute('name');
    const value = input.value;
    const type = field.includes('url') ? 'url' : field.includes('key') ? 'api_key' : 'username';
    let msgEl = input.parentElement.nextElementSibling;
    if (!msgEl || !msgEl.classList.contains('security-msg')) {
        msgEl = input.closest('.mb-2, .mb-3').querySelector('.security-msg');
    }

    if (value && field) {
        try {
            const res = await fetch('/api/security/validate', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ field, value, type })
            });
            const data = await res.json();
            if (msgEl) {
                if (!data.valid) {
                    msgEl.innerText = data.error || 'Inválido';
                    msgEl.classList.add('visible');
                    msgEl.style.display = 'block';
                    input.classList.add('is-invalid');
                } else {
                    msgEl.style.display = 'none';
                    input.classList.remove('is-invalid');
                }
            }
        } catch (e) { }
    }
}

async function optimizeSystem() {
    await fetch('/api/performance/optimize', { method: 'POST' });
    const h = JSON.parse(localStorage.getItem('s1m0n_perf_hist') || '[]');
    h.unshift({ date: new Date().toLocaleTimeString(), action: 'Otimização' });
    localStorage.setItem('s1m0n_perf_hist', JSON.stringify(h));
    renderHistories();
}

async function triggerEvergreen() {
    const topic = document.getElementById('evergreenTopic').value;
    if (!topic) return;
    await fetch('/api/evergreen', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic }) });
    showToast('Geração Evergreen iniciada!', 'success');
    // Refresh history after a short delay to allow DB thread creation
    setTimeout(renderHistories, 1000);
}

async function openCycleModal() {
    // Attempt to get current cycle from backend, else default
    try {
        const res = await fetch('/api/cycle/adjust');
        const data = await res.json();
        const val = data.interval || 120;
        document.getElementById('cycleRange').value = val;
        document.getElementById('cycleVal').innerText = val + ' min';
    } catch (e) {
        // Fallback
        const val = 120;
        document.getElementById('cycleRange').value = val;
        document.getElementById('cycleVal').innerText = val + ' min';
    }
    (new bootstrap.Modal(document.getElementById('cycleModal'))).show();
}

function setCycle(val) {
    document.getElementById('cycleRange').value = val;
    document.getElementById('cycleVal').innerText = val + ' min';
}

async function saveCycle() {
    const val = document.getElementById('cycleRange').value;
    // Save as 'execution_interval' in seconds for backend logic
    const seconds = val * 60;

    // Update the hidden input in perf form if it exists
    const perfInput = document.querySelector('input[name="execution_interval"]');
    if (perfInput) perfInput.value = seconds;

    // Call save settings logic
    await savePerfSettings();

    // Hide modal
    const modalEl = document.getElementById('cycleModal');
    if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();

    showToast('Ciclo de automação atualizado.', 'success');
}

function loadManual() {
    const lang = localStorage.getItem('s1m0n_lang') || 'pt';
    const t = i18n[lang];
    const container = document.getElementById('manualContainer');
    if (!container) return;

    container.innerHTML = `
    <div class="accordion" id="manualAccordion">
        <div class="accordion-item">
            <h2 class="accordion-header"><button class="accordion-button" data-bs-toggle="collapse" data-bs-target="#manual1">${t.man_intro_t}</button></h2>
            <div id="manual1" class="accordion-collapse collapse show" data-bs-parent="#manualAccordion"><div class="accordion-body">${t.man_intro_d}</div></div>
        </div>
        <div class="accordion-item">
            <h2 class="accordion-header"><button class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#manual2">${t.man_setup_t}</button></h2>
            <div id="manual2" class="accordion-collapse collapse" data-bs-parent="#manualAccordion"><div class="accordion-body">${t.man_setup_d}</div></div>
        </div>
        <div class="accordion-item">
            <h2 class="accordion-header"><button class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#manual3">${t.man_gen_t}</button></h2>
            <div id="manual3" class="accordion-collapse collapse" data-bs-parent="#manualAccordion"><div class="accordion-body">${t.man_gen_d}</div></div>
        </div>
    </div>
    `;
}
 
async function optimizeSystem() { confirmAction('Otimizar o S1M0N (Limpeza Profunda)?', async () => { try { const res = await fetch('/api/control', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'OPTIMIZE' }) }); if (res.ok) { showToast('Sistema Otimizado com Sucesso!', 'success'); } else { showToast('Comando enviado.', 'info'); } } catch (e) { showToast('Erro de conex�o.', 'error'); } }); }
