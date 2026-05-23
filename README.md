# File Upload Wargame

파일 업로드 취약점 관련 워게임입니다. 현재 배포본에는 `ThemeDock` 문제만 포함되어 있습니다.

## 실행

Docker Desktop 실행 후, `compose.yaml`이 있는 위치에서 실행합니다.

```bash
docker compose up --build
```

- `ThemeDock`: <http://127.0.0.1:10003>

포트 변경은 `.env.example` 참고

## 문제

- `ThemeDock`: Flask, ZIP 테마팩 업로드 및 게시 서비스

## 목표

`storage` 컨테이너 내부의 `/flag.txt` 읽기

## 종료

```bash
docker compose down
```
