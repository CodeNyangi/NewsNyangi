import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import g4f
import jwt
from datetime import datetime as date
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()

# 환경 변수에서 API 키와 URL 가져오기
CONTENT_API_KEY = os.getenv('CONTENT_API_KEY')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')
API_URL = os.getenv('API_URL')

def get_topic_urls(sitemap_url):
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)
    urls = []
    for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        urls.append(loc)
    return urls[:10]  # 최근 10개의 토픽만 가져옵니다

def scrape_topic(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.select_one('.topictitle.link').text.strip()
    content = soup.select_one('.topic_contents').text.strip()
    
    return {
        'title': title,
        'content': content,
        'url': url
    }

def summarize_trends(topics):
    prompt = """최근 기술 뉴스 토픽 요약:

{topics}

요청 사항:
1. 위의 토픽들을 바탕으로 최근 기술 트렌드를 분석해주세요.
2. 주요 트렌드를 3-5개로 정리해주세요.
3. 각 트렌드에 대해 간단한 설명을 덧붙여주세요.
4. 전체 요약은 300자 내외로 작성해주세요.
5. 가능하다면 이러한 트렌드가 향후 기술 발전이나 산업에 미칠 영향에 대해 간단히 언급해주세요.

출력 형식:
최근 기술 트렌드 요약:
1. [트렌드 1]: [설명]
2. [트렌드 2]: [설명]
3. [트렌드 3]: [설명]
...

결론: [전반적인 트렌드와 향후 영향에 대한 간단한 설명]
"""

    topics_text = ""
    for i, topic in enumerate(topics, 1):
        topics_text += f"{i}. 제목: {topic['title']}\n   요약: {topic['content'][:100]}...\n\n"
    
    formatted_prompt = prompt.format(topics=topics_text)
    
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": formatted_prompt}]
    )
    return response


def clean_content(content):
    # 특수 문자 및 오타 정리
    cleaned = re.sub(r'[^\w\s\.\,\:\;\(\)\-]', '', content)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def create_ghost_token(key):
    id, secret = key.split(':')
    iat = int(date.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/admin/'
    }
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
    return token

def post_to_ghost(url, token, title, content):
    headers = {'Authorization': f'Ghost {token}'}

    # Clean 
    content = clean_content(content)
    
    # Lexical 형식에 맞게 콘텐츠 구조화
    lexical_content = {
        "root": {
            "children": [
                {
                    "children": [
                        {
                            "detail": 0,
                            "format": 0,
                            "mode": "normal",
                            "style": "",
                            "text": content,
                            "type": "text",
                            "version": 1
                        }
                    ],
                    "direction": "ltr",
                    "format": "",
                    "indent": 0,
                    "type": "paragraph",
                    "version": 1
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "type": "root",
            "version": 1
        }
    }

    body = {
        'posts': [{
            'title': title,
            'lexical': json.dumps(lexical_content),  # JSON 문자열로 변환
            'status': 'published'
        }]
    }
    response = requests.post(url, json=body, headers=headers)
    return response

def main():
    sitemap_url = "https://news.hada.io/sitemap/2024.xml"
    ghost_url = API_URL  # Ghost 사이트 URL
    ghost_key = ADMIN_API_KEY  # Ghost Admin API 키

    topic_urls = get_topic_urls(sitemap_url)
    topics = [scrape_topic(url) for url in topic_urls]
    
    summary = summarize_trends(topics)

    token = create_ghost_token(ghost_key)

    # 포스트 제목 날짜와 함께 작성
    title = f"{date.now().strftime('%Y년 %m월 %d일')} 최근 기술 트렌드 요약"
    response = post_to_ghost(f"{ghost_url}/ghost/api/admin/posts/", token, title, summary)

    if response.status_code == 201:
        print("포스트가 성공적으로 작성되었습니다.")
    else:
        print(f"포스트 작성 실패. 상태 코드: {response.status_code}")
        print(f"에러 메시지: {response.text}")

if __name__ == "__main__":
    main()