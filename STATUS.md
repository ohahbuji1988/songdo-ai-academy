# 🧭 송도 국제 AI 아카데미 (Songdo AI Academy) 프로젝트 상황판

> **최종 갱신일시**: 2026-10-27 (새벽)
> **공식 라이브 웹 주소**: [https://songdo-ai.pages.dev](https://songdo-ai.pages.dev)
> **로컬 개발 서버**: `http://127.0.0.1:3000` (실행: `시작하기.bat`)

---

## 📂 핵심 화면 및 파일 가이드 (이 폴더에 들어있는 것)

| 화면 / 파일명 | 용도 및 설명 | 라이브 링크 |
|---|---|---|
| **`index.html`** | **통합 대시보드 (대문)**: 모든 6개 화면을 카드로 보여주는 포털 | [열기](https://songdo-ai.pages.dev/) |
| **`landing.html`** | **수강생 모집 랜딩페이지**: 30분 성공 루프, 37초 스토리 영상, 1초 신청 팝업 | [열기](https://songdo-ai.pages.dev/landing.html) |
| **`courseware/lessons.html`** | **6주 실전 강의실**: 30분 마이크로 루프 교안, 복붙 프롬프트, 3초 복구 실습 | [열기](https://songdo-ai.pages.dev/courseware/lessons.html) |
| **`process.html`** | **공정 로드맵 & 의사결정 계통도**: 기획부터 배포까지의 모든 연결 흐름 | [열기](https://songdo-ai.pages.dev/process.html) |
| **`diagnostic.html`** | **12문항 AI 정밀 진단**: 수강 전 실전자립도 측정 및 즉시 인증서 발급 | [열기](https://songdo-ai.pages.dev/diagnostic.html) |
| **`presentation.html`** | **12슬라이드 발표용 Web PPT**: 설명회/기관 제안용 올인원 프레젠테이션 | [열기](https://songdo-ai.pages.dev/presentation.html) |
| **`server.py`** | **로컬 풀스택 서버**: Python 내장 서버 (포트 3000, 신청서 저장 & 보안 가드) | `python server.py` |
| **`applications.json`** | **수강 신청자 접수 DB**: 신청자 정보(성함, 연락처, 트랙, 문의) 영구 보관 파일 | - |
| **`시작하기.bat`** | **원클릭 실행기**: 더블클릭 시 로컬 서버 구동 + 통합 대시보드 자동 오픈 | 더블클릭 |

---

## 🚀 최근 완료된 핵심 작업 (2026-10-26 완료)
1. **OpenAI Codex CLI 정밀 검수 완료**: P0(신청서 미저장, 파일 보안) & P1(스크립트 문법, 가독성, 뒤로가기) 전면 결함 완치
2. **신청 접수 시스템 완성**: 로컬 서버(`server.py`) 및 Cloudflare Edge Worker(`_worker.js`) 양쪽 모두 실시간 JSON 저장 연동
3. **Cloudflare Pages 글로벌 배포**: 37초 스토리 영상 최적화(32.5MB -> 11.5MB) 및 전 세계 무료 SSL 배포 완료
4. **폴더 구조 다이어트**: 구버전 잔재(`_legacy_archive/`) 분리 및 `songdo-ai-academy`로 공식 개명

---

## 🎯 오늘 바로 진행할 작업 (Next Steps)
- [ ] **실전 강의실(`courseware/lessons.html`) 구체화**:
  - 초보 수강생/학부모가 보고 그대로 따라 할 수 있는 구체적인 행동 액션 시트
  - 1주차~6주차 과제별 "어디를 클릭하고, 무엇을 입력하는지" 직관적 캡처/가이드 추가
  - 과제 완료 셀프 판별 기준표 보강
