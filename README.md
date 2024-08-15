# NewsNyangi
![프로젝트 스크린샷](./image.png)

# Hada News Scraper and Ghost Poster

이 프로젝트는 [Hada News](https://news.hada.io/)에서 최신 기술 뉴스를 스크래핑하고, OpenAI의 GPT 모델을 사용하여 트렌드를 요약한 후, Ghost CMS에 자동으로 포스팅하는 파이썬 스크립트입니다.

## 기능

- Hada News의 sitemap에서 최신 뉴스 토픽 URL 추출
- 각 토픽 페이지에서 제목과 내용 스크래핑
- g4f를 사용하여 기술 트렌드 요약 생성
- Ghost CMS API를 사용하여 요약된 내용을 새 포스트로 발행

## 설치 방법

1. 이 저장소를 클론합니다:
   ```
   git clone https://github.com/your-username/hada-news-scraper.git
   cd hada-news-scraper
   ```

2. 필요한 파이썬 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

3. `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다:
   ```
   CONTENT_API_KEY=your_ghost_content_api_key
   ADMIN_API_KEY=your_ghost_admin_api_key
   API_URL=your_ghost_api_url
   ```

## 사용 방법

스크립트를 실행하려면 다음 명령어를 사용합니다:

```
python app.py
```

이 명령어는 다음 작업을 수행합니다:
1. Hada News에서 최신 뉴스를 스크래핑합니다.
2. 수집된 뉴스를 바탕으로 기술 트렌드를 요약합니다.
3. 요약된 내용을 Ghost CMS에 새 포스트로 발행합니다.

## 주의사항

- 이 스크립트를 정기적으로 실행하려면 cron job이나 다른 스케줄링 도구를 사용하세요.
- 웹 스크래핑 시 해당 웹사이트의 robots.txt 파일을 준수하고, 과도한 요청을 보내지 않도록 주의하세요.