import time
import asyncio
import aiohttp
from flask import Flask, request, jsonify
from urllib.parse import urlparse

app = Flask(__name__)

def httpscheme(url: str) -> str:
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return f'http://{url}'
    return url

async def captcha(website_url: str, website_key: str, method: str) -> str:
    headers = {
        'x-rapidapi-key': "5f686175d1msh16b1de8a1c15abap11cc20jsneccd22c01138",
        'x-rapidapi-host': "fast-multisolver.p.rapidapi.com"
    }
    
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            params = {
                'sitekey': website_key,
                'pageurl': website_url,
                'method': method,
                'json': '1'
            }
            
            async with session.get(
                "https://fast-multisolver.p.rapidapi.com/in.php",
                headers=headers,
                params=params,
                timeout=5
            ) as response:
                result = await response.json()
                
                if result.get('status') != 1:
                    print("Failed to generate")
                
                request_id = result.get('request')
                
                for _ in range(50):
                    async with session.get(
                        f"https://fast-multisolver.p.rapidapi.com/res.php",
                        headers=headers,
                        params={'id': request_id, 'json': '1'}
                    ) as poll_resp:
                        poll_result = await poll_resp.json()
                        
                        if poll_result.get('status') == 1:
                            return poll_result.get('request', '')
                        
                        if poll_result.get('status') != 0:
                            print("Captcha failed")
                        
                        await asyncio.sleep(5)
                
                print("maximum polling rate exceeded")
                
        except Exception as e:
            print(f"Solving error: {str(e)}")

@app.route('/solve', methods=['POST'])
def solve_captcha():
    data = request.get_json()
    if not data or 'sitekey' not in data or 'siteurl' not in data or 'method' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    sitekey = data['sitekey']
    siteurl = data['siteurl']
    method = data['method']
    
    siteurl = httpscheme(siteurl)
    
    try:
        result = asyncio.run(captcha(siteurl, sitekey, method)) 
        if method == "hcaptcha":
            method = "Hcaptcha"
        elif method == "turnstile":
            method = "Cloudflare turnstile"
        elif method == "userrecaptcha":
            method = "Recaptcha V2"
        elif method == "recaptchaV3":
            method = "Recaptcha V3"

        return jsonify({'status': 'success', 'service': method,  'message': 'dc: @._uno3117 and t.me/zynnkys is here', 'result': result})
    except Exception as e:
        return jsonify({'status': 'Failed / Error', 'service': method, 'message': 'dc: @._uno3117 and t.me/zynnkys is here', 'Response': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
