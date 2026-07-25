# AWS Certification Learning Hub 🎓

🔗 **Live Demo:** [https://d4yq42aqslas7.cloudfront.net](https://d4yq42aqslas7.cloudfront.net/)

AI Tutor-powered AWS certification study platform using Bedrock RAG + Serverless architecture

## 📌 Overview

비개발 직군(DGR, AM, BDM 등)의 AWS 자격증 취득을 돕는 웹 기반 학습 플랫폼. 문제 풀이 + AI Tutor 챗봇이 AWS 공식 문서를 근거로 개념을 설명해주는 구조.

**Key Features:**

-   📝 500+ SAA-C03 Practice Questions with explanations
    
-   🤖 AI Tutor chatbot (Bedrock RAG + Claude) — answers based on official AWS docs
    
-   📚 RAG sources: Exam Guide + Well-Architected Framework + 10 AWS Service FAQs
    
-   🌙 Dark / Light mode
    
-   🌐 Korean / English bilingual support
    
-   📊 Multiple study modes (Quick Practice, Domain Practice, Mock Exam, Custom)
    

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

-   Quiz engine (Quick Practice / Domain Practice / Mock Exam / Custom)
    
-   SAA-C03 data pipeline (535 questions parsed, 424 complete with explanations)
    
-   Serverless backend (Lambda + API Gateway + DynamoDB)
    
-   Static hosting (S3 + CloudFront)
    
-   Bedrock Knowledge Base (RAG) — S3 Vectors + metadata filtering
    
-   AI Tutor chatbot (Bedrock Claude + RAG) — floating panel UI
    
-   Bilingual support (Korean / English toggle)
    
-   Dark / Light mode
    
-   Top navigation bar with settings
    
-   Resizable chatbot panel (drag to resize)
    
-   Learning dashboard (domain-wise accuracy tracking)
    
-   AWS Service FAQ data (10 services — scraped & uploaded to S3)
    
-   CLF-C02 / AIF-C01 question data
    
-   Streaming responses (WebSocket + Bedrock invoke\_model\_with\_response\_stream)
    

## 🛠️ Tech Stack

<table style="min-width: 50px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Layer</p></th><th colspan="1" rowspan="1"><p>Service</p></th></tr><tr><td colspan="1" rowspan="1"><p>Frontend</p></td><td colspan="1" rowspan="1"><p>HTML + CSS + JS (vanilla, single-page)</p></td></tr><tr><td colspan="1" rowspan="1"><p>Hosting</p></td><td colspan="1" rowspan="1"><p>S3 + CloudFront (CDN + SSL)</p></td></tr><tr><td colspan="1" rowspan="1"><p>Backend</p></td><td colspan="1" rowspan="1"><p>AWS Lambda (Python 3.14) × 2 functions</p></td></tr><tr><td colspan="1" rowspan="1"><p>API</p></td><td colspan="1" rowspan="1"><p>API Gateway (REST + WebSocket)</p></td></tr><tr><td colspan="1" rowspan="1"><p>Database</p></td><td colspan="1" rowspan="1"><p>DynamoDB (on-demand)</p></td></tr><tr><td colspan="1" rowspan="1"><p>AI/ML</p></td><td colspan="1" rowspan="1"><p>Amazon Bedrock (Claude 3.5 Sonnet via Inference Profile)</p></td></tr><tr><td colspan="1" rowspan="1"><p>RAG</p></td><td colspan="1" rowspan="1"><p>Bedrock Knowledge Base + S3 Vectors</p></td></tr><tr><td colspan="1" rowspan="1"><p>Embeddings</p></td><td colspan="1" rowspan="1"><p>Titan Text Embeddings v2</p></td></tr><tr><td colspan="1" rowspan="1"><p>Vector Store</p></td><td colspan="1" rowspan="1"><p>S3 Vectors (cost-optimized, upgradable to OpenSearch Serverless)</p></td></tr><tr><td colspan="1" rowspan="1"><p>RAG Source</p></td><td colspan="1" rowspan="1"><p>S3 (PDF + TXT + FAQ) + Metadata filtering by exam type</p></td></tr></tbody></table>

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

### REST API

<table style="min-width: 100px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Method</p></th><th colspan="1" rowspan="1"><p>Path</p></th><th colspan="1" rowspan="1"><p>Lambda</p></th><th colspan="1" rowspan="1"><p>Description</p></th></tr><tr><td colspan="1" rowspan="1"><p>GET</p></td><td colspan="1" rowspan="1"><p><code>/questions</code></p></td><td colspan="1" rowspan="1"><p>CertHub-QuestionService</p></td><td colspan="1" rowspan="1"><p>Fetch random questions (params: count, domain, mode)</p></td></tr><tr><td colspan="1" rowspan="1"><p>POST</p></td><td colspan="1" rowspan="1"><p><code>/submit</code></p></td><td colspan="1" rowspan="1"><p>CertHub-QuestionService</p></td><td colspan="1" rowspan="1"><p>Grade answers, return score + explanations</p></td></tr><tr><td colspan="1" rowspan="1"><p>POST</p></td><td colspan="1" rowspan="1"><p><code>/chat</code></p></td><td colspan="1" rowspan="1"><p>CertHub-ChatService</p></td><td colspan="1" rowspan="1"><p>AI Tutor — RAG-based Q&amp;A (fallback)</p></td></tr></tbody></table>

**Base URL:** `https://2ctiq7wune.execute-api.ap-northeast-2.amazonaws.com/prod`

### WebSocket API (Streaming)

<table style="min-width: 75px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Route</p></th><th colspan="1" rowspan="1"><p>Lambda</p></th><th colspan="1" rowspan="1"><p>Description</p></th></tr><tr><td colspan="1" rowspan="1"><p><code>$connect</code></p></td><td colspan="1" rowspan="1"><p>CertHub-WS-Connect</p></td><td colspan="1" rowspan="1"><p>Store connection ID in DynamoDB</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>$disconnect</code></p></td><td colspan="1" rowspan="1"><p>CertHub-WS-Disconnect</p></td><td colspan="1" rowspan="1"><p>Remove connection ID from DynamoDB</p></td></tr><tr><td colspan="1" rowspan="1"><p><code>sendMessage</code></p></td><td colspan="1" rowspan="1"><p>CertHub-WS-SendMessage</p></td><td colspan="1" rowspan="1"><p>RAG retrieve + Claude streaming → token-by-token response</p></td></tr></tbody></table>

**WebSocket URL:** `wss://1zt8c94hdi.execute-api.ap-northeast-2.amazonaws.com/production/`

## 📊 Progress Log

<table style="min-width: 50px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Date</p></th><th colspan="1" rowspan="1"><p>Milestone</p></th></tr><tr><td colspan="1" rowspan="1"><p>2026-07-18</p></td><td colspan="1" rowspan="1"><p>Frontend complete + S3/CloudFront deployment</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-19</p></td><td colspan="1" rowspan="1"><p>Lambda + API Gateway backend complete</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-20</p></td><td colspan="1" rowspan="1"><p>DynamoDB data pipeline complete (534 items)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-22</p></td><td colspan="1" rowspan="1"><p>AIF badge image fix + redeployment</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-23</p></td><td colspan="1" rowspan="1"><p>AI Tutor project started — S3 knowledge bucket + RAG source upload</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>Bedrock Knowledge Base (S3 Vectors) created + synced</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>CertHub-ChatService Lambda created + IAM (Bedrock + Inference Profile)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>API Gateway <code>/chat</code> endpoint deployed</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>AI Tutor API test successful (Claude 3.5 Sonnet via RAG)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>Frontend: Floating chatbot UI added</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>Frontend: Korean/English bilingual toggle (i18n)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>Frontend: Dark/Light mode + Top navigation bar</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>Lambda: Multi-language system prompt (ko/en)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>RAG source expanded: 10 AWS Service FAQs (S3, EC2, VPC, Lambda, RDS, ELB, CloudFront, IAM, SQS, DynamoDB)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-24</p></td><td colspan="1" rowspan="1"><p>Frontend: Resizable chatbot panel (drag corner to resize)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-25</p></td><td colspan="1" rowspan="1"><p>WebSocket Streaming: DynamoDB connection table + API Gateway WebSocket API</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-25</p></td><td colspan="1" rowspan="1"><p>Lambda × 3 (WS-Connect, WS-Disconnect, WS-SendMessage)</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-25</p></td><td colspan="1" rowspan="1"><p>Bedrock invoke_model_with_response_stream — token-level streaming</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-25</p></td><td colspan="1" rowspan="1"><p>Frontend: WebSocket integration + REST fallback</p></td></tr><tr><td colspan="1" rowspan="1"><p>2026-07-25</p></td><td colspan="1" rowspan="1"><p>Live deployment + streaming test successful 🎉</p></td></tr></tbody></table>

## 💰 Estimated Monthly Cost

<table style="min-width: 50px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Service</p></th><th colspan="1" rowspan="1"><p>Cost</p></th></tr><tr><td colspan="1" rowspan="1"><p>Bedrock (Claude 3.5 Sonnet)</p></td><td colspan="1" rowspan="1"><p>~$1-5</p></td></tr><tr><td colspan="1" rowspan="1"><p>API Gateway WebSocket</p></td><td colspan="1" rowspan="1"><p>~$0.01</p></td></tr><tr><td colspan="1" rowspan="1"><p>DynamoDB (Connections table)</p></td><td colspan="1" rowspan="1"><p>~$0.01</p></td></tr><tr><td colspan="1" rowspan="1"><p>S3 Vectors (vector store)</p></td><td colspan="1" rowspan="1"><p>~$1-5</p></td></tr><tr><td colspan="1" rowspan="1"><p>DynamoDB (on-demand)</p></td><td colspan="1" rowspan="1"><p>~$0.5</p></td></tr><tr><td colspan="1" rowspan="1"><p>Lambda + API Gateway</p></td><td colspan="1" rowspan="1"><p>~$0.1</p></td></tr><tr><td colspan="1" rowspan="1"><p>S3 + CloudFront</p></td><td colspan="1" rowspan="1"><p>~$0.05</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Total</strong></p></td><td colspan="1" rowspan="1"><p><strong>~$3-12/month</strong></p></td></tr></tbody></table>

## 🔑 Key Design Decisions

<table style="min-width: 50px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Decision</p></th><th colspan="1" rowspan="1"><p>Rationale</p></th></tr><tr><td colspan="1" rowspan="1"><p><strong>S3 Vectors over OpenSearch Serverless</strong></p></td><td colspan="1" rowspan="1"><p>Cost optimization ($5/mo vs $172/mo), sufficient for small-scale project</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Metadata filtering</strong></p></td><td colspan="1" rowspan="1"><p>Future-proof — add CLF/AIF exams without recreating KB, filter by <code>exam</code> field</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Vanilla HTML (no React)</strong></p></td><td colspan="1" rowspan="1"><p>Node.js install blocked on work laptop, single HTML is S3-deploy friendly</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Serverless only</strong></p></td><td colspan="1" rowspan="1"><p>No EC2 — cost approaches $0 with zero traffic</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Inference Profile</strong></p></td><td colspan="1" rowspan="1"><p>Required for Claude 3.5 Sonnet v2 in ap-northeast-2, APAC prefix <code>apac.*</code></p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Separate Lambda functions</strong></p></td><td colspan="1" rowspan="1"><p>Quiz vs Chat have different timeout (3s vs 30s) and IAM needs</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>i18n with data attributes</strong></p></td><td colspan="1" rowspan="1"><p>Clean separation of content from logic, easy to add more languages</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>WebSocket + REST fallback</strong></p></td><td colspan="1" rowspan="1"><p>WebSocket for streaming UX, REST as fallback if WS connection fails</p></td></tr><tr><td colspan="1" rowspan="1"><p><strong>Separate retrieve + stream</strong></p></td><td colspan="1" rowspan="1"><p><code>retrieve_and_generate</code> doesn't support streaming; split into <code>retrieve</code> + <code>invoke_model_with_response_stream</code></p></td></tr></tbody></table>

## 🚀 Deployment

<table style="min-width: 50px;"><colgroup><col style="min-width: 25px;"><col style="min-width: 25px;"></colgroup><tbody><tr><th colspan="1" rowspan="1"><p>Component</p></th><th colspan="1" rowspan="1"><p>Resource</p></th></tr><tr><td colspan="1" rowspan="1"><p>Frontend</p></td><td colspan="1" rowspan="1"><p>CloudFront Distribution <code>EZ9XCA2AHSV5C</code> — <a target="_blank" rel="noopener noreferrer nofollow" href="https://d4yq42aqslas7.cloudfront.net/">https://d4yq42aqslas7.cloudfront.net</a></p></td></tr><tr><td colspan="1" rowspan="1"><p>Backend API</p></td><td colspan="1" rowspan="1"><p><code>https://2ctiq7wune.execute-api.ap-northeast-2.amazonaws.com/prod</code></p></td></tr><tr><td colspan="1" rowspan="1"><p>Knowledge Base</p></td><td colspan="1" rowspan="1"><p><code>L2I29PW3Z9</code> (S3 Vectors)</p></td></tr><tr><td colspan="1" rowspan="1"><p>WebSocket API</p></td><td colspan="1" rowspan="1"><p><code>wss://1zt8c94hdi.execute-api.ap-northeast-2.amazonaws.com/production/</code></p></td></tr><tr><td colspan="1" rowspan="1"><p>Region</p></td><td colspan="1" rowspan="1"><p>ap-northeast-2 (Seoul)</p></td></tr><tr><td colspan="1" rowspan="1"><p>Account</p></td><td colspan="1" rowspan="1"><p>797240615245</p></td></tr></tbody></table>

## 🔜 Next Steps

1.  **Learning Dashboard** — Track domain-wise accuracy per user
    
2.  **CLF-C02 / AIF-C01** — Add question data for other certifications
    
3.  **GitHub Actions CI/CD** — Automate S3 deployment on push
    
4.  **Custom domain** — Route53 + ACM for branded URL
    

## 📝 License

MIT
