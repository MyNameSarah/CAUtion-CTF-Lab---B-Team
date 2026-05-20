# IDOR Wargame Lab

Flask + Docker 기반 IDOR 워게임 환경.

## Included Challenges

1. Basic Query IDOR
2. REST API IDOR
3. POST Body IDOR
4. File Download IDOR
5. Vertical Privilege Escalation
6. Encoded Object Reference
7. Blind IDOR

---

## Run with Docker

docker build -t idor-lab .  
docker run -p 80:80 idor-lab

---

## Default Account

guest / guest123