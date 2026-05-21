# File Upload Wargame

파일 업로드 취약점 관련 워게임

## 실행

아래 명령은 `compose.yaml`이 있는 폴더에서 실행한다.
Docker Desktop이 켜져 있어야 한다.

```bash
docker compose up --build
```

기본 접속 주소:

- Challenge 1 `PicDrop`: <http://127.0.0.1:10001>
- Challenge 2 `Profile Studio`: <http://127.0.0.1:10002>
- Challenge 3 `ThemeDock`: <http://127.0.0.1:10003>

포트를 바꾸고 싶으면 `.env.example`을 참고해서 `.env`에 `CH1_PORT`, `CH2_PORT`, `CH3_PORT` 값을 설정한다.

## 구성

- `challenge1-php-upload`: PHP/Apache + Docker
- `challenge2-profile-banner`: Flask + Docker
- `challenge3-theme-pack/web, storage`: Flask + Docker

## 시나리오

- Challenge 1 `PicDrop`: 사용자가 이미지를 업로드하면 미리보기 페이지를 만들어주는 서비스
- Challenge 2 `Profile Studio`: 사용자가 배너 이미지와 소개 문구로 프로필 카드를 만드는 서비스
- Challenge 3 `ThemeDock`: ZIP 형태의 테마팩을 업로드하고 미리보기/게시 페이지를 만드는 서비스

## 목표

컨테이너 내부의 `/flag.txt` 읽기

## 종료

```bash
docker compose down
```
