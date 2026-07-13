# CS Archive

수업에서 작성한 Colab 노트북과 회고를 아카이빙하는 간단한 웹앱입니다.

## 실행 방법

```bash
python app.py
```

브라우저에서 http://127.0.0.1:8000 으로 접속하면 됩니다.

## 데이터 저장 형식

저장 데이터는 JSON 파일에 저장됩니다.

```json
[
  {
    "id": "week-1-20260713100000",
    "week": "1",
    "colab_link": "https://colab.research.google.com/drive/...",
    "reflection": "느낀점",
    "improvement": "개선할 점"
  }
]
```
