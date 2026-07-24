# AWS Certification Learning Hub 🎓

🔗 **Live Demo:** [https://d4yq42aqslas7.cloudfront.net](https://d4yq42aqslas7.cloudfront.net/)

AI Tutor-powered AWS certification study platform using Bedrock RAG + Serverless architecture


## 📌 Overview

비개발 직군(DGR, AM, BDM 등)의 AWS 자격증 취득을 돕는 웹 기반 학습 플랫폼.
문제 풀이 + AI Tutor 챗봇이 AWS 공식 문서를 근거로 개념을 설명해주는 구조.

**Key Features:**
- 📝 500+ SAA-C03 Practice Questions with explanations
- 🤖 AI Tutor chatbot (Bedrock RAG + Claude) — answers based on official AWS docs
- 📚 RAG sources: Exam Guide + Well-Architected Framework + 10 AWS Service FAQs
- 🌙 Dark / Light mode
- 🌐 Korean / English bilingual support
- 📊 Multiple study modes (Quick Practice, Domain Practice, Mock Exam, Custom)

## 🏗️ Architecture

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
              │    -SAA-C03        │          │  │  Claude 3.5 Sonnet  │  │       │
              │  (534 questions)   │          │  │  (Inference Profile)│  │       │
              └────────────────────┘          │  └─────────────────────┘  │       │
                                              │  ┌─────────────────────┐  │       │
                                              │  │  Knowledge Base     │  │       │
                                              │  │  (RAG + Metadata    │  │       │
                                              │  │   Filter by exam)   │  │       │
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
                                              │  │ faqs/               │  │       │
                                              │  │  └ 10 AWS Service   │  │       │
                                              │  │    FAQs (S3,EC2,..) │  │       │
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

- [x] Quiz engine (Quick Practice / Domain Practice / Mock Exam / Custom)
- [x] SAA-C03 data pipeline (535 questions parsed, 424 complete with explanations)
- [x] Serverless backend (Lambda + API Gateway + DynamoDB)
- [x] Static hosting (S3 + CloudFront)
- [x] Bedrock Knowledge Base (RAG) — S3 Vectors + metadata filtering
- [x] AI Tutor chatbot (Bedrock Claude + RAG) — floating panel UI
- [x] Bilingual support (Korean / English toggle)
- [x] Dark / Light mode
- [x] Top navigation bar with settings
- [x] Resizable chatbot panel (drag to resize)
- [ ] Learning dashboard (domain-wise accuracy tracking)
- [x] AWS Service FAQ data (10 services — scraped & uploaded to S3)
- [ ] CLF-C02 / AIF-C01 question data
- [ ] Streaming responses for AI Tutor

## 🛠️ Tech Stack

| Layer | Service |
|-------|---------|
| Frontend | HTML + CSS + JS (vanilla, single-page) |
| Hosting | S3 + CloudFront (CDN + SSL) |
| Backend | AWS Lambda (Python 3.14) × 2 functions |
| API | API Gateway (REST) |
| Database | DynamoDB (on-demand) |
| AI/ML | Amazon Bedrock (Claude 3.5 Sonnet via Inference Profile) |
| RAG | Bedrock Knowledge Base + S3 Vectors |
| Embeddings | Titan Text Embeddings v2 |
| Vector Store | S3 Vectors (cost-optimized, upgradable to OpenSearch Serverless) |
| RAG Source | S3 (PDF + TXT + FAQ) + Metadata filtering by exam type |

## 📁 Project Structure

```
aws-cert-learning-hub/
├── frontend/
│   └── index.html                    # Main app (single HTML, 46KB)
├── backend/
│   └── lambda/
│       ├── question_service.py       # Quiz API (GET /questions, POST /submit)
│       └── chat_service.py           # AI Tutor API (POST /chat)
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

## 🔌 API Endpoints

| Method | Path | Lambda | Description |
|--------|------|--------|-------------|
| GET | `/questions` | CertHub-QuestionService | Fetch random questions (params: count, domain, mode) |
| POST | `/submit` | CertHub-QuestionService | Grade answers, return score + explanations |
| POST | `/chat` | CertHub-ChatService | AI Tutor — RAG-based Q&A (params: message, exam, lang) |

**Base URL:** `https://2ctiq7wune.execute-api.ap-northeast-2.amazonaws.com/prod`

## 📊 Progress Log

| Date | Milestone |
|------|-----------|
| 2026-07-18 | Frontend complete + S3/CloudFront deployment |
| 2026-07-19 | Lambda + API Gateway backend complete |
| 2026-07-20 | DynamoDB data pipeline complete (534 items) |
| 2026-07-22 | AIF badge image fix + redeployment |
| 2026-07-23 | AI Tutor project started — S3 knowledge bucket + RAG source upload |
| 2026-07-24 | Bedrock Knowledge Base (S3 Vectors) created + synced |
| 2026-07-24 | CertHub-ChatService Lambda created + IAM (Bedrock + Inference Profile) |
| 2026-07-24 | API Gateway `/chat` endpoint deployed |
| 2026-07-24 | AI Tutor API test successful (Claude 3.5 Sonnet via RAG) |
| 2026-07-24 | Frontend: Floating chatbot UI added |
| 2026-07-24 | Frontend: Korean/English bilingual toggle (i18n) |
| 2026-07-24 | Frontend: Dark/Light mode + Top navigation bar |
| 2026-07-24 | Lambda: Multi-language system prompt (ko/en) |
| 2026-07-24 | RAG source expanded: 10 AWS Service FAQs (S3, EC2, VPC, Lambda, RDS, ELB, CloudFront, IAM, SQS, DynamoDB) |
| 2026-07-24 | Frontend: Resizable chatbot panel (drag corner to resize) |

## 💰 Estimated Monthly Cost

| Service | Cost |
|---------|------|
| Bedrock (Claude 3.5 Sonnet) | ~$1-5 |
| S3 Vectors (vector store) | ~$1-5 |
| DynamoDB (on-demand) | ~$0.5 |
| Lambda + API Gateway | ~$0.1 |
| S3 + CloudFront | ~$0.05 |
| **Total** | **~$3-12/month** |

## 🔑 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **S3 Vectors over OpenSearch Serverless** | Cost optimization ($5/mo vs $172/mo), sufficient for small-scale project |
| **Metadata filtering** | Future-proof — add CLF/AIF exams without recreating KB, filter by `exam` field |
| **Vanilla HTML (no React)** | Node.js install blocked on work laptop, single HTML is S3-deploy friendly |
| **Serverless only** | No EC2 — cost approaches $0 with zero traffic |
| **Inference Profile** | Required for Claude 3.5 Sonnet v2 in ap-northeast-2, APAC prefix `apac.*` |
| **Separate Lambda functions** | Quiz vs Chat have different timeout (3s vs 30s) and IAM needs |
| **i18n with data attributes** | Clean separation of content from logic, easy to add more languages |

## 🚀 Deployment

| Component | Resource |
|-----------|----------|
| Frontend | CloudFront Distribution `EZ9XCA2AHSV5C` — [https://d4yq42aqslas7.cloudfront.net](https://d4yq42aqslas7.cloudfront.net/) |
| Backend API | `https://2ctiq7wune.execute-api.ap-northeast-2.amazonaws.com/prod` |
| Knowledge Base | `L2I29PW3Z9` (S3 Vectors) |
| Region | ap-northeast-2 (Seoul) |
| Account | 797240615245 |

## 🔜 Next Steps

1. **Learning Dashboard** — Track domain-wise accuracy per user
2. **Streaming Responses** — Real-time token streaming for better UX
3. **CLF-C02 / AIF-C01** — Add question data for other certifications
4. **GitHub Actions CI/CD** — Automate S3 deployment on push

## 📝 License

MIT
