#!/usr/bin/env python3
"""
Servidor Web Simples para Dashboard AmFi
=========================================

Servidor HTTP que serve o dashboard e permite execução do monitoramento via API.
"""

import http.server
import socketserver
import json
import os
import subprocess
import sys
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import platform

# Importações para funcionalidade de concentração
try:
    from monitor.utils.concentration_analysis import (
        load_historical_monitoring_data,
        get_entity_historical_concentration,
        get_top_n_breakdown_for_date,
        get_entity_allocation_margins
    )
    CONCENTRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Funcionalidade de concentração não disponível: {e}")
    CONCENTRATION_AVAILABLE = False

# Importações para funcionalidade de PDD
try:
    from monitor.utils.pdd_analysis import (
        get_pdd_pool_historical_analysis,
        get_pdd_cedente_breakdown_for_date,
        get_pdd_methodology_comparison
    )
    PDD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Funcionalidade de PDD não disponível: {e}")
    PDD_AVAILABLE = False

class AmFiHandler(http.server.SimpleHTTPRequestHandler):
    """Handler customizado para o dashboard AmFi."""
    
    def do_OPTIONS(self):
        """Processa requisições OPTIONS para CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Processa requisições POST para API."""
        if self.path == '/api/run_monitoring':
            self.handle_monitoring_request()
        elif self.path == '/api/concentration_history':
            self.handle_concentration_history()
        elif self.path == '/api/topn_breakdown':
            self.handle_topn_breakdown()
        elif self.path == '/api/allocation_margins':
            self.handle_allocation_margins()
        elif self.path == '/api/pdd_history':
            self.handle_pdd_history()
        elif self.path == '/api/pdd_cedente_breakdown':
            self.handle_pdd_cedente_breakdown()
        elif self.path == '/api/pdd_methodology':
            self.handle_pdd_methodology()
        else:
            self.send_error(404, "Endpoint não encontrado")
    
    def do_GET(self):
        """Processa requisições GET."""
        # Definir caminhos baseados na plataforma
        project_root = Path(__file__).parent
        dashboard_dir = project_root / "data" / "output" / "monitoring_results" / "dashboard"
        
        if self.path == '/' or self.path == '/index.html':
            # Servir o dashboard principal
            dashboard_path = dashboard_dir / "table_dashboard.html"
            self.serve_dashboard(str(dashboard_path))
        elif self.path == '/logo.svg':
            # Servir o logo
            logo_path = dashboard_dir / "logo.svg"
            self.serve_file(str(logo_path), 'image/svg+xml')
        else:
            # Servir outros arquivos estáticos
            super().do_GET()
    
    def serve_dashboard(self, file_path):
        """Serve o dashboard HTML com modificações para API."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir o JavaScript de monitoramento por versão funcional
            js_replacement = """
        async function executeMonitoring(force = false) {
            disableButton(true);
            showStatus('🔄 Iniciando monitoramento...', 'warning');
            
            try {
                const response = await fetch('/api/run_monitoring', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'run_monitoring',
                        force: force
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.action_required === 'confirm_overwrite') {
                    showModal();
                    showStatus(`⚠️ Monitoramento já executado para a data base ${result.data_base}. Deseja sobrescrever?`, 'warning');
                } else if (result.success) {
                    let message = `✅ ${result.message}`;
                    if (result.pools_processados && result.pools_processados.length > 0) {
                        message += `<br>📊 Pools processados: ${result.pools_processados.length}`;
                    }
                    if (result.stats) {
                        message += `<br>📈 Taxa de sucesso: ${result.stats.taxa_sucesso || 0}%`;
                    }
                    
                    showStatus(message, 'success');
                    
                    // Recarregar página após 5 segundos se dashboard foi atualizado
                    if (result.dashboard_updated) {
                        showStatus(message + '<br>🔄 Recarregando dashboard em 5 segundos...', 'success');
                        setTimeout(() => {
                            location.reload();
                        }, 5000);
                    }
                } else {
                    showStatus(`❌ Erro: ${result.error || 'Erro desconhecido'}`, 'error');
                }
                
            } catch (error) {
                showStatus(`❌ Erro de conexão: ${error.message}<br><br>💡 <strong>Certifique-se de que está acessando via:</strong><br><code>python3 dashboard_server.py</code><br>e acesse <code>http://localhost:8080</code>`, 'error');
            } finally {
                disableButton(false);
            }
        }"""
            
            # Procurar e substituir a função executeMonitoring
            start_marker = "async function executeMonitoring(force = false) {"
            end_marker = "        }"
            
            start_pos = content.find(start_marker)
            if start_pos != -1:
                # Encontrar o final da função (considerando aninhamento)
                brace_count = 0
                pos = start_pos + len(start_marker)
                while pos < len(content):
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        if brace_count == 0:
                            break
                        brace_count -= 1
                    pos += 1
                
                # Substituir a função
                if pos < len(content):
                    content = content[:start_pos] + js_replacement + content[pos + 1:]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Content-length', len(content.encode('utf-8')))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, "Dashboard não encontrado")
        except Exception as e:
            self.send_error(500, f"Erro ao servir dashboard: {str(e)}")
    
    def serve_file(self, file_path, content_type):
        """Serve um arquivo específico."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', len(content))
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            self.send_error(404, "Arquivo não encontrado")
        except Exception as e:
            self.send_error(500, f"Erro ao servir arquivo: {str(e)}")
    
    def handle_monitoring_request(self):
        """Processa requisição de monitoramento."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            force = data.get('force', False)
            
            print(f"🔄 Recebida solicitação de monitoramento (force={force})")
            
            # Executar o script de monitoramento
            project_root = Path(__file__).parent
            monitoring_script = project_root / "run_monitoring_api.py"
            
            cmd = [sys.executable, str(monitoring_script)]
            if force:
                cmd.append('--force')
            
            print(f"▶️ Executando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=str(project_root),
                timeout=300  # 5 minutos timeout
            )
            
            print(f"✅ Comando executado com código: {result.returncode}")
            
            if result.returncode == 0:
                # Parse do JSON retornado pelo script
                try:
                    response_data = json.loads(result.stdout)
                    print(f"📊 Resposta parseada: sucesso={response_data.get('success', False)}")
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao fazer parse do JSON: {e}")
                    print(f"📝 Stdout: {result.stdout}")
                    # Se não conseguir fazer parse, criar resposta básica
                    response_data = {
                        "success": True,
                        "message": "Monitoramento executado (parsing error)",
                        "output": result.stdout,
                        "raw_output": result.stdout
                    }
            else:
                print(f"❌ Erro na execução: {result.stderr}")
                response_data = {
                    "success": False,
                    "error": result.stderr or "Erro desconhecido na execução",
                    "output": result.stdout,
                    "returncode": result.returncode
                }
            
            # Enviar resposta JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-length', len(response_json.encode('utf-8')))
            self.end_headers()
            self.wfile.write(response_json.encode('utf-8'))
            
        except subprocess.TimeoutExpired:
            error_response = json.dumps({
                "success": False,
                "error": "Timeout na execução do monitoramento (>5 minutos)"
            })
            
            self.send_response(408)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-length', len(error_response.encode('utf-8')))
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))
            
        except Exception as e:
            print(f"💥 Erro no servidor: {str(e)}")
            error_response = json.dumps({
                "success": False,
                "error": f"Erro no servidor: {str(e)}"
            }, ensure_ascii=False)
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-length', len(error_response.encode('utf-8')))
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))

    def handle_concentration_history(self):
        """Processa requisição de histórico de concentração."""
        if not CONCENTRATION_AVAILABLE:
            self.send_json_error(503, "Funcionalidade de concentração não disponível")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pool_name = data.get('pool_name')
            entity_type = data.get('entity_type')
            entity_name = data.get('entity_name')
            
            if not all([pool_name, entity_type, entity_name]):
                self.send_json_error(400, "Parâmetros obrigatórios: pool_name, entity_type, entity_name")
                return
            
            print(f"🔍 Buscando histórico: {entity_type} '{entity_name}' no {pool_name}")
            
            # Carregar dados históricos
            historical_data = load_historical_monitoring_data()
            
            # Obter histórico da entidade
            entity_history = get_entity_historical_concentration(
                pool_name, entity_type, entity_name, historical_data
            )
            
            print(f"📊 Encontrados {len(entity_history)} registros históricos")
            
            self.send_json_response(entity_history)
            
        except Exception as e:
            print(f"💥 Erro ao obter histórico de concentração: {e}")
            self.send_json_error(500, f"Erro interno: {str(e)}")

    def handle_topn_breakdown(self):
        """Processa requisição de breakdown Top N."""
        if not CONCENTRATION_AVAILABLE:
            self.send_json_error(503, "Funcionalidade de concentração não disponível")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pool_name = data.get('pool_name')
            entity_type = data.get('entity_type')
            date = data.get('date', 'latest')
            
            if not all([pool_name, entity_type]):
                self.send_json_error(400, "Parâmetros obrigatórios: pool_name, entity_type")
                return
            
            print(f"🏆 Buscando Top N: {entity_type} no {pool_name} (data: {date})")
            
            # Carregar dados históricos
            historical_data = load_historical_monitoring_data()
            
            # Se date é 'latest', usar a data mais recente disponível
            if date == 'latest' and historical_data:
                date = historical_data[0]['date']  # Primeira data (mais recente - ordem decrescente)
                print(f"📅 Usando data mais recente: {date}")
            
            # Obter breakdown Top N
            breakdown_data = get_top_n_breakdown_for_date(
                pool_name, entity_type, date, historical_data
            )
            
            print(f"📊 Encontradas {len(breakdown_data)} entidades no Top N")
            
            self.send_json_response(breakdown_data)
            
        except Exception as e:
            print(f"💥 Erro ao obter breakdown Top N: {e}")
            self.send_json_error(500, f"Erro interno: {str(e)}")

    def handle_allocation_margins(self):
        """Processa requisição de margens de alocação."""
        if not CONCENTRATION_AVAILABLE:
            self.send_json_error(503, "Funcionalidade de concentração não disponível")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pool_name = data.get('pool_name')
            entity_type = data.get('entity_type')
            entity_name = data.get('entity_name')
            date = data.get('date', 'latest')
            
            if not all([pool_name, entity_type, entity_name]):
                self.send_json_error(400, "Parâmetros obrigatórios: pool_name, entity_type, entity_name")
                return
            
            print(f"💰 Buscando margens: {entity_type} '{entity_name}' no {pool_name} (data: {date})")
            
            # Carregar dados históricos
            historical_data = load_historical_monitoring_data()
            
            # Se date é 'latest', usar a data mais recente disponível
            if date == 'latest' and historical_data:
                date = historical_data[0]['date']  # Primeira data (mais recente - ordem decrescente)
                print(f"📅 Usando data mais recente: {date}")
            
            # Obter margens de alocação
            allocation_data = get_entity_allocation_margins(
                pool_name, entity_type, entity_name, date, historical_data
            )
            
            if not allocation_data:
                self.send_json_error(404, "Nenhum dado de alocação encontrado")
                return
            
            print(f"📊 Margens encontradas: {len(allocation_data.get('top_n_limits', []))} Top N limits")
            
            self.send_json_response(allocation_data)
            
        except Exception as e:
            print(f"💥 Erro ao obter margens de alocação: {e}")
            self.send_json_error(500, f"Erro interno: {str(e)}")

    def handle_pdd_history(self):
        """Processa requisição de histórico de PDD."""
        if not PDD_AVAILABLE:
            self.send_json_error(503, "Funcionalidade de PDD não disponível")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pool_name = data.get('pool_name')
            entity_type = data.get('entity_type', 'pdd')  # PDD não usa entity_type específico
            entity_name = data.get('entity_name', '')     # PDD não usa entity_name específico
            
            if not pool_name:
                self.send_json_error(400, "Parâmetro obrigatório: pool_name")
                return
            
            print(f"📊 Buscando histórico PDD: {pool_name}")
            
            # Carregar dados históricos
            historical_data = load_historical_monitoring_data()
            
            # Obter histórico PDD do pool
            pdd_history = get_pdd_pool_historical_analysis(
                pool_name, entity_type, entity_name, historical_data
            )
            
            print(f"📈 Encontrados {len(pdd_history)} registros históricos PDD")
            
            self.send_json_response(pdd_history)
            
        except Exception as e:
            print(f"💥 Erro ao obter histórico PDD: {e}")
            self.send_json_error(500, f"Erro interno: {str(e)}")

    def handle_pdd_cedente_breakdown(self):
        """Processa requisição de breakdown de cedentes PDD."""
        if not PDD_AVAILABLE:
            self.send_json_error(503, "Funcionalidade de PDD não disponível")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pool_name = data.get('pool_name')
            date = data.get('date', 'latest')
            
            if not pool_name:
                self.send_json_error(400, "Parâmetro obrigatório: pool_name")
                return
            
            print(f"🏢 Buscando breakdown cedentes PDD: {pool_name} (data: {date})")
            
            # Carregar dados históricos
            historical_data = load_historical_monitoring_data()
            
            # Se date é 'latest', usar a data mais recente disponível
            if date == 'latest' and historical_data:
                date = historical_data[0]['date']  # Primeira data (mais recente)
                print(f"📅 Usando data mais recente: {date}")
            
            # Obter breakdown de cedentes
            cedente_breakdown = get_pdd_cedente_breakdown_for_date(
                pool_name, date, historical_data
            )
            
            print(f"🏢 Encontrados {len(cedente_breakdown)} cedentes com PDD")
            
            self.send_json_response(cedente_breakdown)
            
        except Exception as e:
            print(f"💥 Erro ao obter breakdown cedentes PDD: {e}")
            self.send_json_error(500, f"Erro interno: {str(e)}")

    def handle_pdd_methodology(self):
        """Processa requisição de comparação metodológica PDD."""
        if not PDD_AVAILABLE:
            self.send_json_error(503, "Funcionalidade de PDD não disponível")
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pool_name = data.get('pool_name')
            date = data.get('date', 'latest')
            
            if not pool_name:
                self.send_json_error(400, "Parâmetro obrigatório: pool_name")
                return
            
            print(f"⚖️ Buscando comparação metodológica PDD: {pool_name} (data: {date})")
            
            # Carregar dados históricos
            historical_data = load_historical_monitoring_data()
            
            # Se date é 'latest', usar a data mais recente disponível
            if date == 'latest' and historical_data:
                date = historical_data[0]['date']  # Primeira data (mais recente)
                print(f"📅 Usando data mais recente: {date}")
            
            # Obter comparação metodológica
            methodology_data = get_pdd_methodology_comparison(
                pool_name, date, historical_data
            )
            
            if not methodology_data:
                self.send_json_error(404, "Nenhum dado metodológico encontrado")
                return
            
            print(f"⚖️ Comparação metodológica carregada para {pool_name}")
            
            self.send_json_response(methodology_data)
            
        except Exception as e:
            print(f"💥 Erro ao obter comparação metodológica PDD: {e}")
            self.send_json_error(500, f"Erro interno: {str(e)}")

    def send_json_response(self, data):
        """Envia resposta JSON."""
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Content-length', len(response_json.encode('utf-8')))
        self.end_headers()
        self.wfile.write(response_json.encode('utf-8'))

    def send_json_error(self, status_code, message):
        """Envia resposta de erro JSON."""
        error_response = json.dumps({
            "success": False,
            "error": message
        }, ensure_ascii=False)
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-length', len(error_response.encode('utf-8')))
        self.end_headers()
        self.wfile.write(error_response.encode('utf-8'))

def main():
    """Inicia o servidor web."""
    port = 8080
    
    # Definir diretório do projeto baseado na localização do script
    project_root = Path(__file__).parent
    dashboard_dir = project_root / "data" / "output" / "monitoring_results" / "dashboard"
    
    # Criar diretório se não existir
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    # Mudar para o diretório do dashboard
    os.chdir(str(dashboard_dir))
    
    print(f"🚀 Iniciando servidor AmFi Dashboard na porta {port}")
    print(f"📁 Projeto: {project_root}")
    print(f"📂 Dashboard: {dashboard_dir}")
    print(f"🌐 Acesse: http://localhost:{port}")
    print("💡 Para parar o servidor, pressione Ctrl+C")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", port), AmFiHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro no servidor: {e}")

if __name__ == "__main__":
    main()