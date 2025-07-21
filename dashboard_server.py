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