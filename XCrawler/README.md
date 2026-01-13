# X Tweet Monitor

실시간으로 특정 Twitter/X 사용자의 새 포스트를 모니터링하고 수집하는 프로그램입니다.

## 기능

- ✅ X API V2를 사용한 실시간 트윗 모니터링
- ✅ 여러 사용자 동시 모니터링
- ✅ 자동으로 새 트윗 감지 및 저장
- ✅ 답글(replies) 및 리트윗(retweets) 필터링 옵션
- ✅ JSON 형식으로 트윗 데이터 저장
- ✅ 중복 방지 및 상태 관리
- ✅ 커스터마이징 가능한 콜백 함수

## 설치

### 1. 의존성 설치

```bash
cd XCrawler
pip install -r requirements.txt
```

### 2. X API 자격증명 설정

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)에서 API 키를 발급받습니다.
2. `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

3. `.env` 파일을 편집하여 API 자격증명을 입력합니다:

```env
X_BEARER_TOKEN=your_actual_bearer_token_here
POLL_INTERVAL_SECONDS=60
```

**필수:** `X_BEARER_TOKEN`은 반드시 설정해야 합니다.

## 사용 방법

### 기본 실행

```bash
python main.py
```

프로그램을 실행하면 모니터링할 사용자를 입력하라는 메시지가 나타납니다.

### 사용자 입력 예시

```
Enter Twitter usernames to monitor (comma-separated):
> elonmusk, OpenAI, AnthropicAI
```

### 프로그램 구조

```
XCrawler/
├── config.py           # API 설정 및 환경변수 관리
├── x_client.py         # X API V2 클라이언트 래퍼
├── tweet_storage.py    # 트윗 저장 및 상태 관리
├── tweet_monitor.py    # 모니터링 서비스 핵심 로직
├── main.py             # 메인 실행 스크립트
├── requirements.txt    # Python 의존성
├── .env.example        # 환경변수 예시 파일
└── README.md           # 이 파일
```

## 커스터마이징

### 모니터링할 사용자 코드로 지정

`main.py` 파일에서 `users_to_monitor` 리스트를 수정:

```python
users_to_monitor = [
    "elonmusk",
    "OpenAI",
    "AnthropicAI",
    # 여기에 더 추가
]
```

### 폴링 간격 조정

`.env` 파일에서 `POLL_INTERVAL_SECONDS` 값을 변경:

```env
POLL_INTERVAL_SECONDS=60  # 60초마다 체크
```

### 커스텀 콜백 함수 추가

새 트윗이 발견되었을 때 실행할 함수를 추가할 수 있습니다:

```python
def my_custom_callback(username: str, tweets: List[Dict]) -> None:
    # 여기에 원하는 로직 추가 (슬랙 알림, 데이터베이스 저장 등)
    for tweet in tweets:
        print(f"New tweet from @{username}: {tweet['text']}")

monitor.add_callback(my_custom_callback)
```

## 프로그래밍 방식으로 사용

```python
from tweet_monitor import TweetMonitor

# 모니터 초기화
monitor = TweetMonitor(storage_dir="data/tweets")

# 사용자 추가
monitor.add_user("elonmusk", exclude_replies=True, exclude_retweets=True)
monitor.add_user("OpenAI", exclude_replies=True, exclude_retweets=True)

# 한 번만 체크
new_tweets = monitor.run_once()

# 또는 지속적으로 모니터링
monitor.start()  # Ctrl+C로 중지
```

## 데이터 저장

트윗은 `../data/tweets/` 디렉토리에 저장됩니다:

- `{username}_tweets.json` - 각 사용자의 트윗 데이터
- `monitoring_state.json` - 모니터링 상태 (마지막 처리된 트윗 ID 등)

### 트윗 데이터 형식

```json
{
  "username": "elonmusk",
  "last_updated": "2024-01-12T10:30:00",
  "total_tweets": 42,
  "tweets": [
    {
      "id": "1234567890",
      "text": "Tweet text here",
      "created_at": "2024-01-12T10:00:00.000Z",
      "author_id": "44196397",
      "url": "https://twitter.com/i/web/status/1234567890",
      "metrics": {
        "like_count": 1000,
        "retweet_count": 200,
        "reply_count": 50
      },
      "is_reply": false,
      "is_retweet": false
    }
  ]
}
```

## API 사용량 참고사항

X API V2의 무료 티어는 다음 제한이 있습니다:

- **Basic**: 월 10,000 트윗 읽기
- **폴링 간격**: API 호출을 줄이기 위해 최소 60초 이상 권장

자세한 내용은 [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)을 참조하세요.

## 문제 해결

### "Bearer token is required" 오류

- `.env` 파일에 `X_BEARER_TOKEN`이 올바르게 설정되어 있는지 확인하세요.

### "Failed to get user ID" 오류

- 사용자 이름이 올바른지 확인하세요 (@ 기호 제외).
- API 키가 유효한지 확인하세요.

### API Rate Limit 오류

- 폴링 간격을 늘리세요 (`POLL_INTERVAL_SECONDS` 증가).
- 모니터링하는 사용자 수를 줄이세요.

## 라이선스

MIT License
