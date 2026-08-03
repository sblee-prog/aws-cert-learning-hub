"""
AWS SAA-C03 Solution.txt 파싱 스크립트 (v2 - 개선판)
====================================================
개선사항:
- 정답 추출 패턴 강화 (ans-, A., Correct answer 등 다양한 패턴 대응)
- "General" 도메인 줄이기 (키워드 목록 대폭 보강)
- answer_letter 추출 정확도 향상

사용법:
1. "AWS SAA-03 Solution.txt" 파일을 이 스크립트와 같은 폴더에 놓기
2. 터미널에서 실행: python parse_saa_questions.py
3. 결과: saa_c03_questions.json 파일 생성
"""

import re
import json


def parse_saa_solutions(txt_file_path: str, output_json_path: str = "saa_c03_questions.json"):
    """
    AWS SAA-03 Solution.txt 파일을 파싱하여 JSON으로 변환
    """
    
    # 파일 읽기
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 문제별 분리 (구분선 패턴: 최소 10개 이상의 대시)
    blocks = re.split(r'-{10,}', content)
    
    questions = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # 문제 번호 추출: "N]" 패턴
        num_match = re.match(r'(\d+)\]\s*', block)
        if not num_match:
            continue
        
        q_num = int(num_match.group(1))
        remaining = block[num_match.end():]
        
        # 정답 및 해설 추출
        answer_text = ""
        answer_letter = ""
        explanation = ""
        question_text = ""
        
        # === 정답 추출 패턴 (우선순위 순) ===
        
        # 패턴 1: "ans-" 또는 "ans -" 또는 "ans:" 뒤의 텍스트
        ans_match = re.search(
            r'ans\s*[-–:]\s*\.?\s*(.+?)(?:\n\n|\n(?=[A-Z][a-z])|\n(?=General\s)|\n(?=Keywords?)|\n(?=Correct\s))',
            remaining, re.DOTALL
        )
        
        # 패턴 2: "Correct answer X:" 형태
        correct_match = re.search(
            r'Correct\s+answer\s+([A-D])[\s:]+(.+?)(?:\n\n|\n(?=-))',
            remaining, re.DOTALL
        )
        
        # 패턴 3: 선택지 단독 표시 "A. ..." (문제 텍스트 이후 단일 선택지만 있는 경우)
        # 질문 패턴 찾기 (Which/What/How로 끝나는 문장)
        question_end_match = re.search(
            r'(Which|What|How|Where|When).+?\?\s*\n',
            remaining, re.DOTALL
        )
        
        single_option_match = None
        if question_end_match:
            after_question = remaining[question_end_match.end():]
            single_option_match = re.match(r'\s*([A-D])\.\s*(.+?)(?:\n\n|\n(?=[A-Z][a-z])|\n(?=Keywords?))', after_question, re.DOTALL)
        
        # 패턴 적용 (우선순위)
        if ans_match:
            answer_text = ans_match.group(1).strip()
            question_text = remaining[:ans_match.start()].strip()
            explanation = remaining[ans_match.end():].strip()
        elif correct_match:
            answer_letter = correct_match.group(1)
            answer_text = correct_match.group(2).strip()
            question_text = remaining[:correct_match.start()].strip()
            explanation = remaining[correct_match.end():].strip()
        elif single_option_match and question_end_match:
            answer_letter = single_option_match.group(1)
            answer_text = single_option_match.group(2).strip()
            question_text = remaining[:question_end_match.end()].strip()
            explanation = after_question[single_option_match.end():].strip()
        else:
            # 패턴 4: 전체에서 "A." ~ "D." 패턴 찾아서 하나만 있으면 그게 정답
            all_options = re.findall(r'\n([A-D])\.\s*(.+?)(?=\n[A-D]\.|\n\n|$)', remaining, re.DOTALL)
            if len(all_options) == 1:
                answer_letter = all_options[0][0]
                answer_text = all_options[0][1].strip()
                option_pos = remaining.find(f"\n{answer_letter}.")
                question_text = remaining[:option_pos].strip()
                explanation = remaining[option_pos + len(all_options[0][1]) + 3:].strip()
            else:
                # 마지막 시도: "ans" 없이 줄바꿈 2개로 분리된 경우
                parts = remaining.split('\n\n', 1)
                question_text = parts[0].strip()
                if len(parts) > 1:
                    explanation = parts[1].strip()
        
        # === answer_letter 추출 강화 ===
        if not answer_letter and answer_text:
            # 방법 1: 텍스트 시작이 "A." / "B." 등
            letter_match = re.match(r'([A-D])\.?\s', answer_text)
            if letter_match:
                answer_letter = letter_match.group(1)
            else:
                # 방법 2: "Correct answer A:" 패턴이 explanation에 있는 경우
                exp_letter = re.search(r'Correct\s+answer\s+([A-D])', explanation)
                if exp_letter:
                    answer_letter = exp_letter.group(1)
                else:
                    # 방법 3: explanation에서 "Option A is correct" 패턴
                    opt_correct = re.search(r'Option\s+([A-D])\s+is\s+correct', explanation, re.IGNORECASE)
                    if opt_correct:
                        answer_letter = opt_correct.group(1)
                    else:
                        # 방법 4: explanation 첫 줄에 알파벳 있는 경우
                        first_line = explanation.split('\n')[0] if explanation else ""
                        fl_match = re.match(r'([A-D])[\.\):\s]', first_line)
                        if fl_match:
                            answer_letter = fl_match.group(1)
        
        # Keywords 추출
        keywords = []
        kw_match = re.search(r'Keywords?:\s*\n((?:[-•]\s*.+\n?)+)', explanation)
        if kw_match:
            kw_text = kw_match.group(1)
            keywords = [k.strip().lstrip('-•').strip() for k in kw_text.split('\n') if k.strip()]
        
        # 추가: question_text에서 Keywords 제거 (question에 섞여들어간 경우)
        question_text = re.sub(r'Keywords?:\s*\n((?:[-•]\s*.+\n?)+)', '', question_text).strip()
        
        # AWS 서비스 자동 태깅
        all_text = question_text + " " + answer_text + " " + explanation
        services = extract_aws_services(all_text)
        
        # 도메인 자동 분류
        domain = classify_domain(all_text)
        
        # JSON 객체 생성
        question_obj = {
            "question_id": f"SAA-{str(q_num).zfill(3)}",
            "question_number": q_num,
            "certification": "SAA-C03",
            "domain": domain,
            "difficulty": "medium",
            "question_en": question_text,
            "question_ko": "",
            "answer_text": answer_text,
            "answer_letter": answer_letter,
            "explanation_en": explanation,
            "explanation_ko": "",
            "keywords": keywords,
            "related_services": services,
        }
        
        questions.append(question_obj)
    
    # JSON 저장
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*50}")
    print(f"✅ 파싱 완료! (v2 개선판)")
    print(f"{'='*50}")
    print(f"총 문제 수: {len(questions)}문제")
    print(f"출력 파일: {output_json_path}")
    print(f"\n📊 도메인별 분포:")
    
    domain_counts = {}
    for q in questions:
        d = q['domain']
        domain_counts[d] = domain_counts.get(d, 0) + 1
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"   {d}: {c}문제")
    
    # 정답 추출 통계
    with_answer_text = sum(1 for q in questions if q['answer_text'])
    with_answer_letter = sum(1 for q in questions if q['answer_letter'])
    print(f"\n🎯 정답 추출 통계:")
    print(f"   정답 텍스트 추출: {with_answer_text}/{len(questions)} ({with_answer_text/len(questions)*100:.1f}%)")
    print(f"   정답 알파벳 추출: {with_answer_letter}/{len(questions)} ({with_answer_letter/len(questions)*100:.1f}%)")
    
    # General 도메인 상세
    general_count = domain_counts.get("General", 0)
    if general_count > 0:
        print(f"\n⚠️ 미분류(General): {general_count}문제 — 추후 수동 분류 또는 키워드 추가로 개선 가능")
    
    # 처음 3문제 미리보기
    print(f"\n📝 미리보기 (처음 3문제):")
    for q in questions[:3]:
        letter_display = q['answer_letter'] if q['answer_letter'] else '?'
        print(f"\n  [{q['question_id']}] {q['domain']}")
        print(f"  문제: {q['question_en'][:80]}...")
        print(f"  정답: {letter_display} - {q['answer_text'][:60]}...")
        print(f"  서비스: {', '.join(q['related_services'][:5])}")
    
    return questions


def extract_aws_services(text: str) -> list:
    """텍스트에서 AWS 서비스 이름 추출"""
    services_patterns = [
        "S3", "EC2", "Lambda", "DynamoDB", "RDS", "Aurora",
        "CloudFront", "Route 53", "ELB", "ALB", "NLB",
        "VPC", "NAT Gateway", "NAT Instance", "Transit Gateway", "Direct Connect",
        "SQS", "SNS", "Kinesis", "EventBridge", "MQ",
        "ECS", "EKS", "Fargate", "App Runner",
        "CloudWatch", "CloudTrail", "X-Ray", "Config",
        "IAM", "KMS", "Secrets Manager", "WAF", "Shield", "GuardDuty",
        "Athena", "Redshift", "Glue", "EMR", "QuickSight",
        "API Gateway", "Step Functions", "AppSync",
        "EBS", "EFS", "FSx", "Storage Gateway", "Backup",
        "Snowball", "Snowball Edge", "DataSync",
        "Auto Scaling", "Elastic Beanstalk",
        "CloudFormation", "CDK", "SAM", "OpsWorks",
        "Cognito", "STS", "SSO", "Directory Service",
        "ElastiCache", "MemoryDB", "DAX",
        "Bedrock", "SageMaker", "Rekognition", "Comprehend",
        "Organizations", "Control Tower", "Service Catalog",
        "Transfer Acceleration", "Multipart Upload",
        "Global Accelerator", "PrivateLink",
        "CodePipeline", "CodeBuild", "CodeDeploy", "CodeCommit",
        "Macie", "Inspector", "SecurityHub",
        "Systems Manager", "Parameter Store",
        "Elastic IP", "Internet Gateway", "VPN",
        "Snow Family", "Outposts", "Wavelength", "Local Zones"
    ]
    
    found = []
    for service in services_patterns:
        # 대소문자 무시 + 단어 경계 확인 (짧은 서비스명 오탐 방지)
        if len(service) <= 3:
            # S3, EC2, SQS 등 짧은 건 정확히 매칭
            if re.search(r'\b' + re.escape(service) + r'\b', text):
                found.append(service)
        else:
            if service.lower() in text.lower():
                found.append(service)
    
    return list(set(found))


def classify_domain(text: str) -> str:
    """문제 텍스트로 도메인 자동 분류 (SAA-C03 4개 도메인) - 키워드 대폭 보강"""
    text_lower = text.lower()
    
    # Domain 1: Design Secure Architectures (30%)
    security_keywords = [
        "iam", "encryption", "encrypt", "kms", "security group", "waf",
        "shield", "ssl", "tls", "https", "access control", "policy",
        "secret", "credential", "authentication", "authorization",
        "compliance", "audit", "cloudtrail", "guardduty", "macie",
        "principalorgid", "scp", "permission", "role", "trust",
        "private subnet", "bastion", "vpn", "privatelink",
        "acl", "network acl", "nacl", "firewall",
        "certificate", "acm", "inspector", "securityhub",
        "cross-account", "assume role", "federation",
        "bucket policy", "object lock", "mfa delete",
        "data protection", "confidential", "sensitive",
        "key rotation", "envelope encryption",
        "vpc endpoint", "interface endpoint", "gateway endpoint",
        "security", "secure", "protect", "restrict access"
    ]
    
    # Domain 2: Design Resilient Architectures (26%)
    resilient_keywords = [
        "high availability", "highly available", "fault tolerance", "fault-tolerant",
        "multi-az", "multi az", "multiple availability zones",
        "disaster recovery", "dr strategy", "backup", "restore",
        "failover", "redundancy", "redundant", "resilient",
        "auto scaling", "autoscaling", "scaling policy",
        "load balancer", "elb", "alb", "nlb",
        "health check", "unhealthy",
        "replication", "cross-region replication", "replica",
        "recovery point", "recovery time", "rpo", "rto",
        "availability zone", "region", "decouple", "decoupling",
        "sqs", "queue", "message queue", "dead letter",
        "pilot light", "warm standby", "active-active", "active-passive",
        "stateless", "immutable", "blue-green", "canary",
        "graceful", "self-healing", "survive", "outage",
        "continue to operate", "minimal downtime", "no downtime"
    ]
    
    # Domain 3: Design High-Performing Architectures (24%)
    performance_keywords = [
        "performance", "performant", "high-performing",
        "latency", "low latency", "ultra-low latency", "millisecond",
        "throughput", "bandwidth", "speed",
        "caching", "cache", "cloudfront", "elasticache", "dax",
        "read replica", "read-heavy", "write-heavy",
        "provisioned iops", "io1", "io2", "gp3",
        "accelerat", "transfer acceleration",
        "edge location", "edge computing",
        "global accelerator", "content delivery", "cdn",
        "concurrency", "parallel", "batch processing",
        "real-time", "streaming", "kinesis",
        "instance type", "compute optimized", "memory optimized",
        "placement group", "cluster placement", "enhanced networking",
        "efa", "elastic fabric adapter",
        "iops", "throughput optimized",
        "quickly", "fastest", "maximum speed", "as quickly as possible"
    ]
    
    # Domain 4: Design Cost-Optimized Architectures (20%)
    cost_keywords = [
        "cost", "costs", "expensive", "inexpensive", "cheap",
        "budget", "billing", "pricing", "price",
        "savings plan", "reserved instance", "reserved capacity",
        "spot instance", "spot fleet", "spot block",
        "on-demand", "pay-as-you-go",
        "optimize", "optimization", "efficient",
        "lifecycle", "lifecycle policy", "transition",
        "storage class", "infrequent access", "ia",
        "glacier", "deep archive", "intelligent-tiering",
        "right-sizing", "right sizing", "compute optimizer",
        "consolidat", "minimize cost", "reduce cost",
        "cost-effective", "most economical", "least expensive",
        "free tier", "data transfer cost",
        "serverless", "pay per request",
        "unused", "idle", "underutilized",
        "savings", "discount", "commitment"
    ]
    
    # 점수 계산
    scores = {
        "Design Secure Architectures": sum(1 for kw in security_keywords if kw in text_lower),
        "Design Resilient Architectures": sum(1 for kw in resilient_keywords if kw in text_lower),
        "Design High-Performing Architectures": sum(1 for kw in performance_keywords if kw in text_lower),
        "Design Cost-Optimized Architectures": sum(1 for kw in cost_keywords if kw in text_lower),
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        return "General"
    
    return max(scores, key=scores.get)


# === 실행 ===
if __name__ == "__main__":
    # ⬇️ 파일 경로 설정 (본인 환경에 맞게 수정)
    TXT_FILE = "AWS SAA-03 Solution.txt"
    OUTPUT_FILE = "saa_c03_questions.json"
    
    print("🔄 AWS SAA-C03 문제 파싱 시작... (v2 개선판)")
    print(f"   입력: {TXT_FILE}")
    print(f"   출력: {OUTPUT_FILE}")
    
    questions = parse_saa_solutions(TXT_FILE, OUTPUT_FILE)
