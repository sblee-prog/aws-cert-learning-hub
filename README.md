# AWS Certification Learning Hub 🎓

AI Tutor 기반 AWS 자격증 학습 플랫폼 — Bedrock RAG + Serverless Architecture

## 📌 Overview

AWS 자격증 취득을 돕는 웹 기반 학습 플랫폼.
문제 풀이 + AI Tutor 챗봇이 AWS 공식 문서를 근거로 개념을 설명해주는 구조.

## Architecture

```
                            ┌─────────────────────────────────────────────────────┐
                            │                   AWS Cloud (ap-northeast-2)         │
                            │                                                     │
┌──────────┐   HTTPS   ┌───┴──────────┐                                          │
│  Users   │──────────▶│  CloudFront  │                                          │
│(Browser) │◀──────────│  (CDN/SSL)   │                                          │
└──────────┘           └───┬──────────┘                                          │
                            │                                                     │
              ┌─────────────┼──────────────────────────┐                          │
              │             ▼                          ▼                          │
      ┌───────────────┐              ┌────────────────────────┐                  │
      │  S3 (Frontend) │              │     API Gateway        │                  │
      │cert-hub-frontend│              │      (REST API)        │                  │
      │   index.html   │              │                        │                  │
      └───────────────┘              └───────┬───────┬────────┘                  │
                                              │       │                           │
                              ┌───────────────┘       └──────────────┐            │
                              ▼                                      ▼            │
                 ┌────────────────────┐               ┌────────────────────┐      │
                 │  Lambda: Quiz API  │               │  Lambda: Chat API  │      │
                 │ GET /questions     │               │  POST /chat        │      │
                 │ POST /submit       │               │  (AI Tutor)        │      │
                 └─────────┬──────────┘               └──────┬─────────────┘      │
                           │                                  │                   │
                           ▼                                  ▼                   │
              ┌────────────────────┐          ┌───────────────────────────┐       │
              │     DynamoDB       │          │     Amazon Bedrock        │       │
              │ CertHub-Questions  │          │  ┌─────────────────────┐  │       │
              │    -SAA-C03        │          │  │  Claude (LLM)       │  │       │
              │  (534 questions)   │          │  │  + System Prompt    │  │       │
              └────────────────────┘          │  └─────────────────────┘  │       │
                                              │  ┌─────────────────────┐  │       │
                                              │  │  Knowledge Base     │  │       │
                                              │  │  (RAG Retrieval)    │  │       │
                                              │  │  + Metadata Filter  │  │       │
                                              │  └──────────┬──────────┘  │       │
                                              └─────────────┼─────────────┘       │
                                                            │                     │
                                              ┌─────────────▼─────────────┐       │
                                              │   S3: cert-hub-knowledge  │       │
                                              │  ┌─────────────────────┐  │       │
                                              │  │ official-docs/      │  │       │
                                              │  │  ├ saa-c03-exam-    │  │       │
                                              │  │  │   guide.pdf      │  │       │
                                              │  │  └ well-architected │  │       │
                                              │  │      -framework.pdf │  │       │
                                              │  ├─────────────────────┤  │       │
                                              │  │ questions/          │  │       │
                                              │  │  └ saa-questions-   │  │       │
                                              │  │      rag.txt (424Q) │  │       │
                                              │  ├─────────────────────┤  │       │
                                              │  │ S3 Vectors          │  │       │
                                              │  │ (Titan Embeddings)  │  │       │
                                              │  └─────────────────────┘  │       │
                                              └───────────────────────────┘       │
                                                                                  │
                            └─────────────────────────────────────────────────────┘

  ─── Deployment Pipeline ───────────────────────────────────────────────────────

  ┌──────────┐  push   ┌──────────┐  upload  ┌─────────────┐  invalidate  ┌────────────┐
  │  GitHub  │────────▶│CloudShell│─────────▶│ S3 (Frontend│─────────────▶│ CloudFront │
  │   Repo   │         │  / CLI   │          │  / Knowledge)│              │   Cache    │
  └──────────┘         └──────────┘          └─────────────┘              └────────────┘

  ─── Data Pipeline ────────────────────────────────────────────────────────────

  ┌──────────┐  parse  ┌──────────┐  upload  ┌──────────┐   sync   ┌─────────────┐
  │ Raw Data │────────▶│  Python  │─────────▶│ DynamoDB │          │  Knowledge  │
  │(PDF/TXT) │         │ Scripts  │─────────▶│    S3    │─────────▶│    Base     │
  └──────────┘         └──────────┘          └──────────┘          └─────────────┘
```

## ✅ Features

- [x] 퀴즈 엔진 (Quick Practice / Domain Practice / Mock Exam / Custom)
- [x] SAA-C03 문제 데이터 파이프라인 (535문제, 424 complete)
- [x] Serverless 백엔드 (Lambda + API Gateway + DynamoDB)
- [x] 정적 호스팅 (S3 + CloudFront)
- [x] Bedrock Knowledge Base (RAG) — S3 Vectors
- [ ] AI Tutor 챗봇 (Bedrock Claude + RAG)
- [ ] 한국어 UI 완성
- [ ] 학습 대시보드 (도메인별 정답률)
- [ ] CLF-C02 / AIF-C01 문제 데이터 추가
- [ ] Web Crawler 소스 추가 (AWS FAQ 페이지)

## 🛠️ Tech Stack

| Layer | Service |
|-------|---------|
| Frontend | HTML + CSS + JS (vanilla) |
| Hosting | S3 + CloudFront |
| Backend | AWS Lambda (Python 3.14) |
| API | API Gateway (REST) |
| Database | DynamoDB (on-demand) |
| AI/ML | Amazon Bedrock (Claude) + Knowledge Base |
| Vector Store | S3 Vectors |
| Embeddings | Titan Text Embeddings v2 |
| RAG Source | S3 (PDF + TXT) + Web Crawler (planned) |

## 📁 Project Structure

```
aws-cert-learning-hub/
├── frontend/
│   └── index.html                    # Main app (single HTML)
├── backend/
│   └── lambda/
│       ├── question_service.py       # Quiz API (GET /questions, POST /submit)
│       └── chat_service.py           # AI Tutor API (POST /chat) — TBD
├── data-pipeline/
│   ├── parse_saa_questions.py        # TXT solution parser
│   ├── parse_pdf_options.py          # PDF options extractor
│   └── export_questions.py           # DynamoDB → RAG text export
├── docs/
│   ├── ARCHITECTURE.md               # Detailed architecture doc
│   └── bedrock-rag-setup.md          # RAG setup guide
├── CHANGELOG.md                      # Development log
└── README.md
```

## 📊 Progress Log

| Date | Milestone |
|------|-----------|
| 2026-07-18 | 프론트엔드 완성 + S3/CloudFront 배포 |
| 2026-07-19 | Lambda + API Gateway 백엔드 완성 |
| 2026-07-20 | DynamoDB 데이터 파이프라인 완성 (534 items) |
| 2026-07-22 | AIF 배지 이미지 수정 + 재배포 |
| 2026-07-23 | Bedrock Knowledge Base 생성 (S3 Vectors) |
| 2026-07-23 | RAG 소스 업로드 (Exam Guide + WAF PDF + 424문제 텍스트) |
| 2026-07-24 | RAG 테스트 성공 (Claude 3.5 Sonnet) |

## 💰 Estimated Monthly Cost

| Service | Cost |
|---------|------|
| Bedrock (Claude) | ~$1-5 |
| S3 Vectors | ~$1-5 |
| DynamoDB (on-demand) | ~$0.5 |
| Lambda + API Gateway | ~$0.1 |
| S3 + CloudFront | ~$0.05 |
| **Total** | **~$3-12/month** |

## 🔑 Key Design Decisions

1. **S3 Vectors over OpenSearch Serverless** — 비용 최적화 ($5/월 vs $172/월), 소규모 프로젝트에 충분한 성능
2. **Metadata filtering** — 향후 다른 자격증(CLF, AIF) 추가 시 `exam` 필드로 필터링, KB 재생성 불필요
3. **Vanilla HTML (no React)** — Node.js 설치 불가 환경 대응, S3 정적 호스팅에 최적
4. **Serverless only** — EC2 없이 완전 서버리스, 트래픽 없으면 비용 $0에 수렴

## 🚀 Deployment

- **Frontend**: CloudFront Distribution `EZ9XCA2AHSV5C`
- **Backend**: API Gateway `https://2ctiq7wune.execute-api.ap-northeast-2.amazonaws.com/prod`
- **Region**: ap-northeast-2 (Seoul)

## 📝 License

MIT
