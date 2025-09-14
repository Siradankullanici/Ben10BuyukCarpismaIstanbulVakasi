# server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import re

class Handler(BaseHTTPRequestHandler):
    def log_request_details(self, method):
        """Gelen istekleri detaylı şekilde logla"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*60}")
        print(f"[{timestamp}] {method} İsteği Geldi")
        print(f"{'='*60}")
        print(f"URL Path: {self.path}")
        print(f"Client IP: {self.client_address[0]}:{self.client_address[1]}")
        print(f"User-Agent: {self.headers.get('User-Agent', 'Bilinmiyor')}")
        
        # Headers'ları göster
        print(f"\nHeaders:")
        for header, value in self.headers.items():
            print(f"  {header}: {value}")
        
        # Query parametrelerini parse et
        if '?' in self.path:
            url_parts = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(url_parts.query)
            if query_params:
                print(f"\nQuery Parameters:")
                for key, values in query_params.items():
                    print(f"  {key}: {values}")
        
        print(f"{'='*60}\n")
    
    def extract_multipart_field(self, post_data, field_name):
        """Multipart data'dan belirli field'ı çıkar"""
        try:
            data_str = post_data.decode('utf-8')
            pattern = f'name="{field_name}"\\r\\n\\r\\n([^\\r\\n-]+)'
            match = re.search(pattern, data_str)
            if match:
                return match.group(1).strip()
        except:
            pass
        return None
    
    def do_GET(self):
        self.log_request_details("GET")
        
        # Ben10 oyun dosyaları
        if self.path.endswith('/readme.txt'):
            print(f"✅ readme.txt dosyası istendi: {self.path}")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'Ben10 Game Ready')
        
        elif self.path.endswith('/list.xml'):
            print(f"📄 list.xml dosyası istendi: {self.path}")
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            list_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<files>
    <file>
        <name>ben10game.exe</name>
        <size>1024000</size>
        <md5>abcd1234ef567890</md5>
    </file>
    <file>
        <name>readme.txt</name>
        <size>512</size>
        <md5>1234abcd5678ef90</md5>
    </file>
</files>'''
            self.wfile.write(list_xml.encode('utf-8'))
        
        # Güncelleme kontrolü
        elif self.path.startswith('/update') or 'update' in self.path.lower():
            print("🔄 Güncelleme kontrolü")
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            update_xml = '''<?xml version="1.0"?>
<update>
    <status>no_update</status>
    <version>1.0.0</version>
    <message>Oyun güncel</message>
</update>'''
            self.wfile.write(update_xml.encode())
        
        # Server status
        elif self.path in ['/status', '/ping']:
            print("📡 Server status kontrolü")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            status = {
                "status": "online",
                "server": "ben10_game_server",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(status).encode())
        
        else:
            print("❓ Bilinmeyen GET isteği")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'OK')
    
    def do_POST(self):
        self.log_request_details("POST")
        
        # POST verisini oku
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        print(f"POST Data Length: {content_length} bytes")
        
        try:
            data_str = post_data.decode('utf-8')
            print(f"POST Data (Raw):\n{data_str}")
        except:
            print(f"POST Data (Binary): {post_data}")
        
        # Ana authentication endpoint
        if self.path == '/serverside/newCode.php':
            self.handle_auth_request(post_data)
        
        # Diğer serverside istekleri
        elif self.path.startswith('/serverside/'):
            print(f"🔧 Serverside dosyası istendi: {self.path}")
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            xml_response = '''<?xml version="1.0"?>
<response>
    <status>success</status>
    <message>İşlem başarılı</message>
</response>'''
            self.wfile.write(xml_response.encode())
        
        # Game data endpoint
        elif 'gamedata' in self.path.lower() or 'data' in self.path:
            print("💾 Oyun verisi isteği")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            game_data = {
                "status": "success",
                "player_data": {
                    "level": 1,
                    "score": 0,
                    "unlocked_levels": [1]
                }
            }
            self.wfile.write(json.dumps(game_data).encode())
        
        else:
            print("❓ Bilinmeyen POST isteği")
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'<?xml version="1.0"?><response><status>success</status></response>')
    
    def handle_auth_request(self, post_data):
        """Authentication isteğini her zaman valid yap"""
        username = self.extract_multipart_field(post_data, 'username')
        password = self.extract_multipart_field(post_data, 'password') 
        hardware = self.extract_multipart_field(post_data, 'hardware')
        code = self.extract_multipart_field(post_data, 'code')
        
        print(f"\n📋 Authentication Bilgileri:")
        print(f"  👤 Username: {username}")
        print(f"  🔐 Password: {password}")
        print(f"  💻 Hardware: {hardware}")
        print(f"  🎮 Code: {code}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
<response>
    <status>success</status>
    <auth>true</auth>
    <user>ben10player</user>
    <code_verified>true</code_verified>
    <game_access>granted</game_access>
    <session_id>ben10_session_123</session_id>
    <server_time>{}</server_time>
    <message>Hoşgeldin! Oyun başlayabilir.</message>
</response>'''.format(datetime.now().isoformat())
        
        self.wfile.write(xml_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """CORS preflight istekleri için"""
        self.log_request_details("OPTIONS")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_HEAD(self):
        """HEAD istekleri için"""
        self.log_request_details("HEAD")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()


if __name__ == "__main__":
    print("🚀 Ben10 Kapsamlı Debug Server başlatılıyor...")
    print("📍 Adres: http://localhost:80")
    print("🔍 Tüm istekler debug modunda loglanacak")
    print("🎮 Auth, dosya, güncelleme ve data endpoint'leri hazır")
    print("⏹️  Durdurmak için Ctrl+C")
    print("\n" + "="*60 + "\n")
    
    try:
        HTTPServer(('localhost', 80), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server durduruldu")
    except PermissionError:
        print("❌ Port 80'i kullanmak için admin yetkisi gerekli! Alternatif: 8080 kullanılıyor...")
        try:
            HTTPServer(('localhost', 8080), Handler).serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server durduruldu")
