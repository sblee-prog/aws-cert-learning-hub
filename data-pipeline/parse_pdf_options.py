"""
AWS SAA-C03 PDF 파싱 스크립트 — 선택지(A/B/C/D) 추출 + JSON 매칭
================================================================
기존 saa_c03_questions.json에 선택지를 추가하고,
answer_letter가 없는 문제에 알파벳을 매칭합니다.

사전 설치:
  pip install pdfplumber

사용법:
1. 같은 폴더에 아래 파일 준비:
   - AWS Certified Solutions Architect Associate SAA-C03.pdf
   - saa_c03_questions.json (이전 스크립트 실행 결과)
2. 실행: python parse_pdf_options.py
3. 결과: saa_c03_questions_complete.json 생성
"""

import re
import json
import pdfplumber


def extract_questions_from_pdf(pdf_path: str) -> list:
    """PDF에서 문제 + 선택지 추출"""
    
    print(f"📄 PDF 텍스트 추출 중: {pdf_path}")
    
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += text + "\n"
            if (i + 1) % 50 == 0:
                print(f"   {i+1}/{total_pages} 페이지 처리 완료...")
    
    print(f"   ✅ 총 {total_pages} 페이지 추출 완료")
    
    # 문제별 분리: "Question #N" 또는 "Question#N" 패턴
    # 또는 번호만 있는 경우 대비
    question_blocks = re.split(r'(?:Question\s*#?\s*(\d+))', full_text)
    
    pdf_questions = []
    
    # question_blocks: ['', '1', '문제내용', '2', '문제내용', ...]
    i = 1
    while i < len(question_blocks) - 1:
        try:
            q_num = int(question_blocks[i])
            q_content = question_blocks[i + 1]
        except (ValueError, IndexError):
            i += 1
            continue
        
        # 선택지 추출
        options = extract_options(q_content)
        
        # 문제 텍스트 (선택지 이전까지)
        question_text = q_content
        if options:
            first_option_pos = q_content.find("A.")
            if first_option_pos == -1:
                first_option_pos = q_content.find("A)")
            if first_option_pos > 0:
                question_text = q_content[:first_option_pos].strip()
        
        pdf_questions.append({
            "question_number": q_num,
            "question_text": question_text.strip(),
            "options": options
        })
        
        i += 2
    
    # 위 패턴으로 안 잡히면 대안 패턴 시도
    if len(pdf_questions) < 100:
        print(f"   ⚠️ 패턴1로 {len(pdf_questions)}문제만 추출. 대안 패턴 시도...")
        pdf_questions = extract_with_alternative_pattern(full_text)
    
    print(f"   📊 PDF에서 추출된 문제: {len(pdf_questions)}개")
    return pdf_questions


def extract_with_alternative_pattern(full_text: str) -> list:
    """대안 패턴: 선택지 A~D 기반으로 문제 분리"""
    
    # 모든 "A." 이전의 텍스트 블록을 문제로 간주
    # 패턴: 문장 끝(?) + 줄바꿈 + A.
    blocks = re.split(r'\n(?=A\.\s)', full_text)
    
    pdf_questions = []
    q_num = 0
    
    for block in blocks:
        # 선택지가 있는 블록만 처리
        options = extract_options(block)
        if not options or len(options) < 4:
            continue
        
        q_num += 1
        
        # 문제 텍스트 (A. 이전)
        a_pos = block.find("A.")
        question_text = block[:a_pos].strip() if a_pos > 0 else ""
        
        # 문제 번호 추출 시도
        num_match = re.search(r'(\d+)\s*$', question_text.split('\n')[0]) if question_text else None
        actual_num = int(num_match.group(1)) if num_match else q_num
        
        pdf_questions.append({
            "question_number": actual_num,
            "question_text": question_text,
            "options": options
        })
    
    return pdf_questions


def extract_options(text: str) -> dict:
    """텍스트에서 A/B/C/D 선택지 추출"""
    
    options = {}
    
    # 패턴: "A. ..." / "B. ..." / "C. ..." / "D. ..."
    # 각 선택지는 다음 선택지 시작 또는 텍스트 끝까지
    patterns = [
        # A. ~ B. 사이
        (r'A\.\s*(.+?)(?=\nB\.|\n[B-D]\))', 'A'),
        (r'B\.\s*(.+?)(?=\nC\.|\n[C-D]\))', 'B'),
        (r'C\.\s*(.+?)(?=\nD\.|\n[D]\))', 'C'),
        (r'D\.\s*(.+?)(?=\n[A-Z]\.|\n\n|\Z)', 'D'),
    ]
    
    # 더 유연한 방식: 한 번에 모든 선택지 찾기
    option_matches = re.findall(
        r'([A-D])\.\s*(.+?)(?=(?:\n[A-D]\.\s)|\n\n|\Z)',
        text, re.DOTALL
    )
    
    for letter, content in option_matches:
        options[letter] = content.strip().replace('\n', ' ')
    
    # 4개 미만이면 다른 패턴 시도
    if len(options) < 4:
        # 패턴 2: "A)" 형태
        option_matches2 = re.findall(
            r'([A-D])\)\s*(.+?)(?=(?:\n[A-D]\)\s)|\n\n|\Z)',
            text, re.DOTALL
        )
        for letter, content in option_matches2:
            if letter not in options:
                options[letter] = content.strip().replace('\n', ' ')
    
    return options


def match_answer_letter(answer_text: str, options: dict) -> str:
    """answer_text와 선택지를 비교해서 알파벳 매칭"""
    
    if not answer_text or not options:
        return ""
    
    answer_clean = answer_text.lower().strip()
    # 앞에 알파벳 접두사 제거
    answer_clean = re.sub(r'^[a-d]\.?\s*', '', answer_clean)
    
    best_match = ""
    best_score = 0
    
    for letter, option_text in options.items():
        option_clean = option_text.lower().strip()
        
        # 방법 1: 정확히 일치
        if answer_clean == option_clean:
            return letter
        
        # 방법 2: answer_text가 option에 포함
        if answer_clean in option_clean or option_clean in answer_clean:
            score = len(set(answer_clean.split()) & set(option_clean.split()))
            if score > best_score:
                best_score = score
                best_match = letter
        
        # 방법 3: 처음 30자 비교
        if answer_clean[:30] == option_clean[:30]:
            return letter
        
        # 방법 4: 단어 겹침 비율
        answer_words = set(answer_clean.split())
        option_words = set(option_clean.split())
        if answer_words and option_words:
            overlap = len(answer_words & option_words) / max(len(answer_words), len(option_words))
            if overlap > 0.6 and overlap > best_score:
                best_score = overlap
                best_match = letter
    
    return best_match


def merge_pdf_with_json(pdf_questions: list, json_path: str, output_path: str):
    """PDF 선택지 데이터를 기존 JSON에 병합"""
    
    print(f"\n🔗 JSON과 PDF 데이터 병합 중...")
    
    # 기존 JSON 로드
    with open(json_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # PDF 데이터를 문제번호로 인덱싱
    pdf_by_num = {q['question_number']: q for q in pdf_questions}
    
    matched_options = 0
    matched_letters = 0
    letter_improved = 0
    
    for q in questions:
        q_num = q['question_number']
        
        if q_num in pdf_by_num:
            pdf_q = pdf_by_num[q_num]
            options = pdf_q['options']
            
            # 선택지 추가
            if options and len(options) >= 2:
                q['options_en'] = options
                matched_options += 1
                
                # answer_letter가 없으면 텍스트 매칭으로 추출
                if not q.get('answer_letter') or q['answer_letter'] == '':
                    matched_letter = match_answer_letter(q.get('answer_text', ''), options)
                    if matched_letter:
                        q['answer_letter'] = matched_letter
                        letter_improved += 1
            
            if q.get('answer_letter'):
                matched_letters += 1
    
    # 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*50}")
    print(f"✅ 병합 완료!")
    print(f"{'='*50}")
    print(f"총 문제: {len(questions)}")
    print(f"선택지 추가: {matched_options}/{len(questions)} ({matched_options/len(questions)*100:.1f}%)")
    print(f"정답 알파벳 보유: {matched_letters}/{len(questions)} ({matched_letters/len(questions)*100:.1f}%)")
    print(f"새로 매칭된 알파벳: +{letter_improved}문제")
    print(f"출력 파일: {output_path}")
    
    # 완성도 통계
    complete = sum(1 for q in questions 
                   if q.get('answer_letter') and q.get('options_en') and len(q.get('options_en', {})) >= 4)
    print(f"\n🏆 완전한 문제 (문제+선택지+정답알파벳+해설): {complete}/{len(questions)} ({complete/len(questions)*100:.1f}%)")
    
    return questions


# === 실행 ===
if __name__ == "__main__":
    # ⬇️ 파일 경로 설정
    PDF_FILE = "AWS Certified Solutions Architect Associate SAA-C03.pdf"
    JSON_FILE = "saa_c03_questions.json"  # 이전 스크립트 결과
    OUTPUT_FILE = "saa_c03_questions_complete.json"
    
    print("🔄 PDF 선택지 추출 + JSON 병합 시작...")
    print(f"   PDF: {PDF_FILE}")
    print(f"   JSON: {JSON_FILE}")
    print(f"   출력: {OUTPUT_FILE}")
    print()
    
    # Step 1: PDF에서 문제 + 선택지 추출
    pdf_questions = extract_questions_from_pdf(PDF_FILE)
    
    # Step 2: 기존 JSON과 병합
    if pdf_questions:
        questions = merge_pdf_with_json(pdf_questions, JSON_FILE, OUTPUT_FILE)
    else:
        print("❌ PDF에서 문제를 추출하지 못했습니다.")
        print("   PDF 파일명이 정확한지 확인하세요.")
