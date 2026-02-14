-- ===================================================
-- MINE Load Test - 샘플 데이터 생성 스크립트
-- ===================================================
-- 목적: first_learning.py 시나리오를 위한 테스트 데이터 생성
-- 포함: 카테고리, 키워드, 카드, Attempt, 피드백
-- ===================================================

BEGIN;

-- ===================================================
-- 1. 카테고리 생성 (Categories)
-- ===================================================
INSERT INTO categories (id, name, description, is_active, display_order, created_at, updated_at)
VALUES
(1, '비즈니스 영어', '업무에서 사용하는 영어 표현', true, 1, NOW(), NOW()),
(2, '일상 회화', '일상적인 대화 표현', true, 2, NOW(), NOW()),
(3, '면접 영어', '취업 면접에서 사용하는 영어', true, 3, NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET is_active = true, updated_at = NOW();

-- ===================================================
-- 2. 키워드 생성 (Keywords)
-- ===================================================
-- 비즈니스 영어 키워드
INSERT INTO keywords (id, category_id, name, description, is_active, display_order, created_at, updated_at)
VALUES
(1, 1, '회의', '비즈니스 미팅 관련 표현', true, 1, NOW(), NOW()),
(2, 1, '이메일', '업무 이메일 작성 표현', true, 2, NOW(), NOW()),
(3, 1, '프레젠테이션', '발표 관련 표현', true, 3, NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET is_active = true, updated_at = NOW();

-- 일상 회화 키워드
INSERT INTO keywords (id, category_id, name, description, is_active, display_order, created_at, updated_at)
VALUES
(4, 2, '인사', '일상 인사 표현', true, 1, NOW(), NOW()),
(5, 2, '쇼핑', '쇼핑 관련 표현', true, 2, NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET is_active = true, updated_at = NOW();

-- 면접 영어 키워드
INSERT INTO keywords (id, category_id, name, description, is_active, display_order, created_at, updated_at)
VALUES
(6, 3, '자기소개', '면접 자기소개 표현', true, 1, NOW(), NOW()),
(7, 3, '경력', '경력 설명 표현', true, 2, NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET is_active = true, updated_at = NOW();

-- ===================================================
-- 3. 샘플 카드 생성 (Cards) - User 1~10용
-- ===================================================
-- User 1: 비즈니스 영어 - 회의
INSERT INTO cards (id, user_id, category_id, keyword_id, title, study_count, created_at, updated_at, last_studied_at, state)
VALUES
(1, 1, 1, 1, '회의 일정 조율하기', 0, NOW(), NOW(), NULL, 'ACTIVE')
ON CONFLICT (id) DO UPDATE
SET state = 'ACTIVE', updated_at = NOW();

-- User 2: 일상 회화 - 인사
INSERT INTO cards (id, user_id, category_id, keyword_id, title, study_count, created_at, updated_at, last_studied_at, state)
VALUES
(2, 2, 2, 4, '처음 만난 사람에게 인사하기', 0, NOW(), NOW(), NULL, 'ACTIVE')
ON CONFLICT (id) DO UPDATE
SET state = 'ACTIVE', updated_at = NOW();

-- User 3: 면접 영어 - 자기소개
INSERT INTO cards (id, user_id, category_id, keyword_id, title, study_count, created_at, updated_at, last_studied_at, state)
VALUES
(3, 3, 3, 6, '영어 면접 자기소개', 1, NOW(), NOW(), NOW(), 'ACTIVE')
ON CONFLICT (id) DO UPDATE
SET state = 'ACTIVE', updated_at = NOW();

-- User 4: 비즈니스 영어 - 이메일
INSERT INTO cards (id, user_id, category_id, keyword_id, title, study_count, created_at, updated_at, last_studied_at, state)
VALUES
(4, 4, 1, 2, '업무 요청 이메일 작성', 0, NOW(), NOW(), NULL, 'ACTIVE')
ON CONFLICT (id) DO UPDATE
SET state = 'ACTIVE', updated_at = NOW();

-- User 5: 일상 회화 - 쇼핑
INSERT INTO cards (id, user_id, category_id, keyword_id, title, study_count, created_at, updated_at, last_studied_at, state)
VALUES
(5, 5, 2, 5, '옷 가게에서 물건 구매하기', 2, NOW(), NOW(), NOW(), 'ACTIVE')
ON CONFLICT (id) DO UPDATE
SET state = 'ACTIVE', updated_at = NOW();

-- ===================================================
-- 4. 샘플 Attempt 생성 (Attempts) - 피드백 포함
-- ===================================================
-- Card 3 (User 3) - 완료된 피드백
INSERT INTO attempts (id, card_id, audio_url, duration_seconds, status, created_at, updated_at, feedback_generated_at)
VALUES
(1, 3, 'https://mine-audio-bucket.s3.ap-northeast-2.amazonaws.com/test/sample_1.mp3', 45, 'COMPLETED', NOW() - INTERVAL '1 hour', NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET status = 'COMPLETED', updated_at = NOW();

-- Card 5 (User 5) - 완료된 피드백 1
INSERT INTO attempts (id, card_id, audio_url, duration_seconds, status, created_at, updated_at, feedback_generated_at)
VALUES
(2, 5, 'https://mine-audio-bucket.s3.ap-northeast-2.amazonaws.com/test/sample_2.mp3', 60, 'COMPLETED', NOW() - INTERVAL '2 hours', NOW(), NOW() - INTERVAL '1 hour')
ON CONFLICT (id) DO UPDATE
SET status = 'COMPLETED', updated_at = NOW();

-- Card 5 (User 5) - 완료된 피드백 2
INSERT INTO attempts (id, card_id, audio_url, duration_seconds, status, created_at, updated_at, feedback_generated_at)
VALUES
(3, 5, 'https://mine-audio-bucket.s3.ap-northeast-2.amazonaws.com/test/sample_3.mp3', 55, 'COMPLETED', NOW() - INTERVAL '30 minutes', NOW(), NOW() - INTERVAL '10 minutes')
ON CONFLICT (id) DO UPDATE
SET status = 'COMPLETED', updated_at = NOW();

-- ===================================================
-- 5. 샘플 피드백 생성 (Feedbacks)
-- ===================================================
-- Attempt 1 피드백 (Card 3)
INSERT INTO feedbacks (id, attempt_id, transcription, overall_score, pronunciation_score, fluency_score, grammar_score, vocabulary_score, overall_comment, pronunciation_details, fluency_details, grammar_details, vocabulary_details, created_at, updated_at)
VALUES
(1, 1,
'Hello, my name is John. I have five years of experience in software development.',
85, 80, 85, 90, 85,
'전반적으로 우수한 발표입니다. 발음이 명확하고 문법도 정확합니다.',
'대부분의 단어를 정확하게 발음했습니다. "experience" 단어의 강세에 주의하세요.',
'말하는 속도가 적절하고 자연스럽습니다. 약간의 긴장감이 느껴지지만 전달력이 좋습니다.',
'문법적으로 오류가 없습니다. 시제와 구조가 정확합니다.',
'적절한 어휘를 사용했습니다. "years of experience"는 면접에서 자주 쓰이는 좋은 표현입니다.',
NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET overall_score = 85, updated_at = NOW();

-- Attempt 2 피드백 (Card 5 - 첫 번째 시도)
INSERT INTO feedbacks (id, attempt_id, transcription, overall_score, pronunciation_score, fluency_score, grammar_score, vocabulary_score, overall_comment, pronunciation_details, fluency_details, grammar_details, vocabulary_details, created_at, updated_at)
VALUES
(2, 2,
'Excuse me, can I try this on? What size do you have?',
75, 70, 75, 80, 75,
'쇼핑 상황에서 사용할 수 있는 기본적인 표현을 잘 사용했습니다.',
'"excuse"의 발음이 약간 불명확합니다. /ɪkˈskjuːz/로 발음하세요.',
'전반적으로 자연스러우나 문장 사이에 긴 쉼이 있었습니다. 좀 더 자신감 있게 말해보세요.',
'문법은 정확합니다. 의문문 구조를 올바르게 사용했습니다.',
'"try this on"은 옷을 입어본다는 의미로 자연스러운 표현입니다.',
NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET overall_score = 75, updated_at = NOW();

-- Attempt 3 피드백 (Card 5 - 두 번째 시도)
INSERT INTO feedbacks (id, attempt_id, transcription, overall_score, pronunciation_score, fluency_score, grammar_score, vocabulary_score, overall_comment, pronunciation_details, fluency_details, grammar_details, vocabulary_details, created_at, updated_at)
VALUES
(3, 3,
'Excuse me, can I try this on? What sizes do you have available?',
82, 78, 82, 85, 85,
'이전 시도보다 많이 개선되었습니다! 발음과 유창성이 향상되었습니다.',
'"excuse"의 발음이 개선되었습니다. 좀 더 명확하게 들립니다.',
'훨씬 자연스럽고 자신감 있게 말했습니다. 쉼도 줄어들었습니다.',
'문법이 완벽합니다. "sizes"를 복수형으로 사용하고 "available"을 추가한 것이 좋습니다.',
'"available"을 추가하여 더 정중하고 자연스러운 표현이 되었습니다.',
NOW(), NOW())
ON CONFLICT (id) DO UPDATE
SET overall_score = 82, updated_at = NOW();

-- ===================================================
-- 6. Sequence 업데이트 (다음 ID를 위해)
-- ===================================================
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('keywords_id_seq', (SELECT MAX(id) FROM keywords));
SELECT setval('cards_id_seq', (SELECT MAX(id) FROM cards));
SELECT setval('attempts_id_seq', (SELECT MAX(id) FROM attempts));
SELECT setval('feedbacks_id_seq', (SELECT MAX(id) FROM feedbacks));

COMMIT;

-- ===================================================
-- 7. 검증 쿼리
-- ===================================================
SELECT '=== 카테고리 생성 확인 ===' AS info;
SELECT id, name, is_active FROM categories ORDER BY id;

SELECT '=== 키워드 생성 확인 ===' AS info;
SELECT k.id, k.name, c.name AS category FROM keywords k JOIN categories c ON k.category_id = c.id ORDER BY k.id;

SELECT '=== 카드 생성 확인 ===' AS info;
SELECT c.id, c.user_id, c.title, cat.name AS category, k.name AS keyword FROM cards c
JOIN categories cat ON c.category_id = cat.id
JOIN keywords k ON c.keyword_id = k.id
ORDER BY c.id;

SELECT '=== Attempt 및 피드백 확인 ===' AS info;
SELECT a.id AS attempt_id, a.card_id, a.status, f.overall_score, f.transcription
FROM attempts a
LEFT JOIN feedbacks f ON a.id = f.attempt_id
ORDER BY a.id;
