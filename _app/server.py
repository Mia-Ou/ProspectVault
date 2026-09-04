#!/usr/bin/env python3
"""秋招工作台本地服务器 - 数据持久化方案
启动后访问 http://localhost:8765 即可使用
数据直接保存在 jobs.json，重启浏览器/清缓存都不丢
"""
import http.server
import json
import os
import sys
import threading
import webbrowser
from datetime import datetime
from urllib.parse import urlparse

PORT = 8765
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_FILE = os.path.join(BASE_DIR, 'jobs.json')
HTML_FILE = os.path.join(BASE_DIR, '秋招工作台.html')

# 文件锁（防止并发写冲突）
file_lock = threading.Lock()

def get_local_ip():
    """获取本机局域网 IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

class WorkbenchHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def log_message(self, format, *args):
        if '/api/' in str(args[0]):
            super().log_message(format, *args)
    
    def _add_cors(self):
        """添加 CORS 头，允许跨域访问"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._add_cors()
        self.end_headers()
    
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/data':
            self._handle_read()
        elif path == '/' or path == '':
            self._serve_html()
        else:
            super().do_GET()
    
    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/data':
            self._handle_write()
        else:
            self.send_error(404)
    
    def _serve_html(self):
        try:
            with open(HTML_FILE, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def _handle_read(self):
        try:
            with file_lock:
                with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self._add_cors()
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))
    
    def _handle_write(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            
            # 更新时间戳
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['updatedAt'] = datetime.now().astimezone().isoformat()
            data['metadata']['savedVia'] = 'local-server'
            
            with file_lock:
                # 备份旧文件
                if os.path.exists(JOBS_FILE):
                    backup = JOBS_FILE + '.bak'
                    with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                        old = f.read()
                    with open(backup, 'w', encoding='utf-8') as f:
                        f.write(old)
                
                with open(JOBS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._add_cors()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as e:
            self.send_error(500, str(e))


def main():
    # 检查必要文件
    if not os.path.exists(JOBS_FILE):
        print(f"错误：找不到 {JOBS_FILE}")
        sys.exit(1)
    if not os.path.exists(HTML_FILE):
        print(f"错误：找不到 {HTML_FILE}")
        print("请先运行：python _app/build.py")
        sys.exit(1)
    
    server = http.server.HTTPServer(('0.0.0.0', PORT), WorkbenchHandler)
    local_ip = get_local_ip()
    local_url = f'http://localhost:{PORT}'
    lan_url = f'http://{local_ip}:{PORT}'
    
    print(f'''
╔══════════════════════════════════════════════════════╗
║            秋招工作台 · 本地服务器                    ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  本机访问：{local_url:<35}  ║
║  局域网访问：{lan_url:<33}  ║
║                                                      ║
║  数据文件：jobs.json（自动保存）                      ║
║                                                      ║
║  使用方法：                                          ║
║  1. 电脑浏览器打开上面的地址                          ║
║  2. 手机连同一个 Wi-Fi，打开局域网地址                ║
║  3. 所有改动实时保存到磁盘                            ║
║  4. 按 Ctrl+C 停止服务                               ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
''')
    
    # 自动打开浏览器
    threading.Timer(0.5, lambda: webbrowser.open(local_url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
        server.server_close()


if __name__ == '__main__':
    main()
