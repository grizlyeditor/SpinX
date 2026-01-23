import json
import requests
import time
import logging
import random
import base64
import binascii
import asyncio
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
from datetime import datetime
import google.protobuf
import freefire_response_pb2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import MajorLoginRes_pb2
except ImportError as e:
    print(f"Import error: {e}")

# Setup minimal logging for Vercel
logging.basicConfig(level=logging.ERROR)

class FreeFireAPI:
    def __init__(self):
        self.key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        self.iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        
        self.regions = {
            'IND': {
                'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
                'major_login_url': 'https://loginbp.ggpolarbear.com/MajorLogin',
                'get_login_data_url': 'https://clientbp.ggpolarbear.com/GetLoginData',
                'gacha_url': 'https://clientbp.ggpolarbear.com/PurchaseGacha',
                'client_host': 'clientbp.ggpolarbear.com'
            }
        }
        
        self.session = requests.Session()
        
    def generate_headers(self):
        return {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36'
            ]),
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    
    def encrypt_api(self, plain_text):
        try:
            plain_text = bytes.fromhex(plain_text)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
            return cipher_text.hex()
        except Exception as e:
            return None
    
    def parse_my_message(self, serialized_data):
        try:
            MajorLogRes = MajorLoginRes_pb2.MajorLoginRes()
            MajorLogRes.ParseFromString(serialized_data)
            jwt_token = MajorLogRes.token
            key = MajorLogRes.ak
            iv = MajorLogRes.aiv
            key_hex = key.hex() if key else None
            iv_hex = iv.hex() if iv else None
            return jwt_token, key_hex, iv_hex
        except Exception as e:
            return None, None, None
    
    def guest_token(self, uid, password, region='IND'):
        try:
            region_config = self.regions.get(region, self.regions['IND'])
            url = region_config['guest_url']
            
            data = {
                "uid": f"{uid}",
                "password": f"{password}",
                "response_type": "token",
                "client_type": "2",
                "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                "client_id": "100067",
            }
            
            headers = self.generate_headers()
            response = self.session.post(url, data=data, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                data_json = response.json()
                return data_json.get('access_token'), data_json.get('open_id')
            else:
                return None, None
        except:
            return None, None
    
    def major_login(self, access_token, open_id, region='IND'):
        try:
            region_config = self.regions.get(region, self.regions['IND'])
            url = region_config['major_login_url']
            
            headers = {
                'X-Unity-Version': '2018.4.11f1',
                'ReleaseVersion': 'OB52',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-GA': 'v1 1',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
                'Host': 'loginbp.ggblueshark.com',
                'Connection': 'Keep-Alive',
            }
            
            payload_template = bytes.fromhex(
                '1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134'
            )
            
            OLD_OPEN_ID = b"996a629dbcdb3964be6b6978f5d814db"
            OLD_ACCESS_TOKEN = b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a"
            
            payload = payload_template.replace(OLD_OPEN_ID, open_id.encode())
            payload = payload.replace(OLD_ACCESS_TOKEN, access_token.encode())
            
            encrypted_payload = self.encrypt_api(payload.hex())
            if not encrypted_payload:
                return None
            
            final_payload = bytes.fromhex(encrypted_payload)
            
            response = self.session.post(
                url,
                headers=headers,
                data=final_payload,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200 and len(response.content) > 0:
                return response.content
            else:
                return None
        except:
            return None
    
    def GET_PAYLOAD_BY_DATA(self, JWT_TOKEN, NEW_ACCESS_TOKEN, region='IND'):
        try:
            token_payload_base64 = JWT_TOKEN.split('.')[1]
            token_payload_base64 += '=' * ((4 - len(token_payload_base64) % 4) % 4)
            decoded_payload = base64.urlsafe_b64decode(token_payload_base64).decode('utf-8')
            decoded_payload = json.loads(decoded_payload)
            NEW_EXTERNAL_ID = decoded_payload['external_id']
            SIGNATURE_MD5 = decoded_payload['signature_md5']
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            payload = bytes.fromhex("1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134")
            
            payload = payload.replace(b"2025-07-30 11:02:51", now.encode())
            payload = payload.replace(b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a", NEW_ACCESS_TOKEN.encode("UTF-8"))
            payload = payload.replace(b"996a629dbcdb3964be6b6978f5d814db", NEW_EXTERNAL_ID.encode("UTF-8"))
            payload = payload.replace(b"7428b253defc164018c604a1ebbfebdf", SIGNATURE_MD5.encode("UTF-8"))
            
            PAYLOAD = payload.hex()
            PAYLOAD = self.encrypt_api(PAYLOAD)
            
            if PAYLOAD:
                return bytes.fromhex(PAYLOAD)
            else:
                return None
        except:
            return None
    
    def GET_LOGIN_DATA(self, JWT_TOKEN, PAYLOAD, region='IND'):
        try:
            region_config = self.regions.get(region, self.regions['IND'])
            url = region_config['get_login_data_url']
            client_host = region_config['client_host']
            
            headers = {
                'Expect': '100-continue',
                'Authorization': f'Bearer {JWT_TOKEN}',
                'X-Unity-Version': '2018.4.11f1',
                'X-GA': 'v1 1',
                'ReleaseVersion': 'OB52',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
                'Host': client_host,
                'Connection': 'close',
            }
            
            response = self.session.post(url, headers=headers, data=PAYLOAD, verify=False, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False
    
    async def perform_spin(self, jwt_token, spin_payload_hex):
        try:
            if not spin_payload_hex:
                return None, False
            
            encrypted_payload = binascii.unhexlify(spin_payload_hex.replace(" ", ""))
            
            headers = {
                'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
                'Connection': "Keep-Alive",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/octet-stream",
                'Authorization': f"Bearer {jwt_token}",
                'X-Unity-Version': "2018.4.11f1",
                'X-GA': "v1 1",
                'ReleaseVersion': "OB52"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.regions['IND']['gacha_url'],
                    headers=headers,
                    data=encrypted_payload,
                    ssl=False,
                    timeout=10
                ) as res:
                    
                    if res.status == 200:
                        response_bytes = await res.read()
                        
                        # Parse response
                        try:
                            response_obj = freefire_response_pb2.FreeFireResponse()
                            response_obj.ParseFromString(response_bytes)
                            
                            item_id = None
                            # Try to extract item ID from different fields
                            if hasattr(response_obj, 'field_22') and response_obj.field_22:
                                import re
                                match = re.search(r'\d{9}', response_obj.field_22)
                                if match:
                                    item_id = match.group(0)
                            
                            return item_id, True
                        except:
                            return None, True
                    else:
                        return None, False
        except:
            return None, False

# Vercel API Handler
from flask import Flask, request, jsonify

app = Flask(__name__)
ff_api = FreeFireAPI()

@app.route('/')
def home():
    return jsonify({
        "error": "Use API: /method?spin=PAYLOAD_HEX&u=UID&p=PASSWORD&rg=REGION",
        "example": "/method?spin=A31F3A86EC5EC81AF12D164DBA364919&u=123456&p=password&rg=IND"
    }), 400

@app.route('/method')
def method():
    try:
        # Get parameters
        spin_payload = request.args.get('spin', '').strip()
        uid = request.args.get('u', '').strip()
        password = request.args.get('p', '').strip()
        region = request.args.get('rg', 'IND').strip().upper()
        
        # Validate parameters
        if not uid or not password:
            return jsonify({
                "error": "Missing parameters",
                "required": "u (UID), p (PASSWORD)",
                "optional": "spin (payload hex), rg (region)"
            }), 400
        
        # Step 1: Get guest token
        access_token, open_id = ff_api.guest_token(uid, password, region)
        if not access_token:
            return jsonify({
                "status": "failed",
                "uid": uid,
                "password": password,
                "error": "Guest token failed"
            }), 200
        
        # Step 2: Major login
        major_response = ff_api.major_login(access_token, open_id, region)
        if not major_response:
            return jsonify({
                "status": "failed",
                "uid": uid,
                "password": password,
                "error": "Major login failed"
            }), 200
        
        # Step 3: Parse JWT token
        jwt_token, key, iv = ff_api.parse_my_message(major_response)
        if not jwt_token:
            return jsonify({
                "status": "failed",
                "uid": uid,
                "password": password,
                "error": "JWT parse failed"
            }), 200
        
        # Step 4: Get login data payload
        payload = ff_api.GET_PAYLOAD_BY_DATA(jwt_token, access_token, region)
        if not payload:
            return jsonify({
                "status": "failed",
                "uid": uid,
                "password": password,
                "error": "Payload creation failed"
            }), 200
        
        # Step 5: Activate account
        activation_success = ff_api.GET_LOGIN_DATA(jwt_token, payload, region)
        
        item_id = None
        spin_success = False
        
        # Step 6: Perform spin if payload provided
        if spin_payload and activation_success:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            item_id, spin_success = loop.run_until_complete(
                ff_api.perform_spin(jwt_token, spin_payload)
            )
            loop.close()
        
        # Prepare response
        response_data = {
            "status": "success" if activation_success else "failed",
            "uid": uid,
            "password": password,
            "region": region,
            "activation": activation_success,
            "spin_performed": bool(spin_payload),
            "spin_success": spin_success,
            "item_id": item_id if item_id else "N/A"
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Internal server error"
        }), 500

# For Vercel
def vercel_handler(request):
    with app.app_context():
        if request.path == '/':
            return home()
        elif request.path.startswith('/method'):
            return method()
        else:
            return jsonify({"error": "Not found"}), 404

# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=5000)