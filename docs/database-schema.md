# Dating App - Схема базы данных

## Общие сведения

- **СУБД:** PostgreSQL 15+
- **Архитектура:** Database-per-service (каждый сервис имеет свою БД)

---

## 1. Auth Service Database

```sql
CREATE DATABASE auth_db;

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. User Service Database

```sql
CREATE DATABASE user_db;

CREATE TABLE users (
    id UUID PRIMARY KEY,  
    username VARCHAR(50) UNIQUE,
    referral_code VARCHAR(10) UNIQUE NOT NULL,
    referred_by UUID REFERENCES users(id),
    referral_count INTEGER DEFAULT 0,
    premium_until TIMESTAMPTZ,
    settings JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',  
    banned_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE referral_bonuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    referred_user_id UUID NOT NULL REFERENCES users(id),
    bonus_type VARCHAR(50) NOT NULL, 
    bonus_value INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blocker_id UUID NOT NULL REFERENCES users(id),
    blocked_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(blocker_id, blocked_id)
);

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID NOT NULL REFERENCES users(id),
    reported_id UUID NOT NULL REFERENCES users(id),
    reason VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'reviewed', 'resolved'
    reviewed_by UUID,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Profile Service Database

```sql
CREATE DATABASE profile_db;


-- Профили
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    birthdate DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,  -- 'male', 'female', 'non_binary'
    bio TEXT,
    location VARCHAR,
    city VARCHAR(100),
    country VARCHAR(100),

    -- Дополнительные поля
    height INTEGER,  -- в см
    occupation VARCHAR(100),
    company VARCHAR(100),
    education VARCHAR(100),

    -- Статусы
    is_verified BOOLEAN DEFAULT FALSE,
    verification_photo_url VARCHAR(500),
    completion_score INTEGER DEFAULT 0,

    -- Метаданные
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- Справочник интересов
CREATE TABLE interests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50),  -- 'music', 'sports', 'movies', etc.
    popularity INTEGER DEFAULT 0
);

-- Связь профилей и интересов
CREATE TABLE profile_interests (
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    interest_id INTEGER NOT NULL REFERENCES interests(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (profile_id, interest_id)
);

-- Фотографии
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    position INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- Предпочтения поиска
CREATE TABLE search_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID UNIQUE NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    min_age INTEGER DEFAULT 18,
    max_age INTEGER DEFAULT 99,
    gender_preference VARCHAR(20)[] DEFAULT ARRAY['male', 'female'],
    max_distance INTEGER DEFAULT 100,  -- в км
    show_verified_only BOOLEAN DEFAULT FALSE,
    show_with_bio_only BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. Matching Service Database

```sql
CREATE DATABASE matching_db;

-- Свайпы
CREATE TABLE swipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    swiper_id UUID NOT NULL,
    swiped_id UUID NOT NULL,
    action VARCHAR(15) NOT NULL,  -- 'like', 'dislike', 'super_like'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(swiper_id, swiped_id)
);

-- Мэтчи
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user1_id UUID NOT NULL,
    user2_id UUID NOT NULL,
    matched_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    unmatched_by UUID,
    unmatched_at TIMESTAMPTZ,

    -- Статистика диалога
    chat_initiated BOOLEAN DEFAULT FALSE,
    chat_initiated_by UUID,
    chat_initiated_at TIMESTAMPTZ,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMPTZ,

    UNIQUE(user1_id, user2_id),
);

-- Лайки, которые пользователь ещё не видел (для показа "Кто вас лайкнул")
CREATE TABLE pending_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    liker_id UUID NOT NULL,
    liked_id UUID NOT NULL,
    is_super BOOLEAN DEFAULT FALSE,
    seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(liker_id, liked_id)
);

-- Daily limits (для super likes и т.д.)
CREATE TABLE daily_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    super_likes_used INTEGER DEFAULT 0,
    rewinds_used INTEGER DEFAULT 0,
    boosts_used INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);
```

---

## 5. Rating Service Database

```sql
CREATE DATABASE rating_db;

-- Основная таблица рейтингов
CREATE TABLE user_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL,

    -- Уровень 1: Первичный рейтинг
    profile_score DECIMAL(5,2) DEFAULT 0,      -- полнота анкеты (0-100)
    photo_score DECIMAL(5,2) DEFAULT 0,        -- качество/количество фото (0-100)
    primary_rating DECIMAL(5,2) DEFAULT 0,     -- итоговый первичный (0-100)

    -- Уровень 2: Поведенческий рейтинг
    likes_received INTEGER DEFAULT 0,
    dislikes_received INTEGER DEFAULT 0,
    super_likes_received INTEGER DEFAULT 0,
    matches_count INTEGER DEFAULT 0,
    chats_initiated INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,

    -- Расчётные метрики
    like_ratio DECIMAL(5,4) DEFAULT 0,         -- likes / (likes + dislikes)
    match_rate DECIMAL(5,4) DEFAULT 0,         -- matches / likes_given
    chat_initiation_rate DECIMAL(5,4) DEFAULT 0,
    response_rate DECIMAL(5,4) DEFAULT 0,
    behavioral_rating DECIMAL(5,2) DEFAULT 0,

    -- Уровень 3: Комбинированный рейтинг
    referral_bonus DECIMAL(5,2) DEFAULT 0,
    premium_bonus DECIMAL(5,2) DEFAULT 0,
    combined_rating DECIMAL(5,2) DEFAULT 0,

    elo_score INTEGER DEFAULT 1000, -- мб убрать 

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- История изменений рейтинга
CREATE TABLE rating_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    rating_type VARCHAR(30) NOT NULL,  -- 'primary', 'behavioral', 'combined'
    old_value DECIMAL(5,2),
    new_value DECIMAL(5,2),
    change_reason VARCHAR(100),  -- 'new_like', 'new_match', 'profile_update', 'scheduled_recalc'
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Агрегированная статистика (для быстрых отчётов)
CREATE TABLE rating_stats_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,

    impressions INTEGER DEFAULT 0,  -- сколько раз показали
    likes_received INTEGER DEFAULT 0,
    dislikes_received INTEGER DEFAULT 0,
    matches INTEGER DEFAULT 0,

    avg_rating DECIMAL(5,2),

    UNIQUE(user_id, date)
);
```

---

## 6. Chat Service Database

```sql
CREATE DATABASE chat_db;

-- Комнаты чата (привязаны к мэтчу)
CREATE TABLE chat_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID UNIQUE NOT NULL,
    user1_id UUID NOT NULL,
    user2_id UUID NOT NULL,

    -- Статусы
    is_active BOOLEAN DEFAULT TRUE,

    -- Метаданные
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMPTZ,
    last_message_preview TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Сообщения
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL,

    -- Контент
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',  -- 'text', 'image', 'gif', 'voice'
    media_url VARCHAR(500),

    -- Статусы
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Typing indicators (можно держать в Redis, но для истории)
CREATE TABLE typing_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL,
    user_id UUID NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

-- Read receipts (для групповых чатов в будущем)
CREATE TABLE read_receipts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    read_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(message_id, user_id)
);
```

---

## 7. AI Service Database

```sql
CREATE DATABASE ai_db;

CREATE TABLE profile_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,

    overall_score INTEGER,  -- 0-100
    photo_quality_score INTEGER, - под большим вопросом 
    bio_quality_score INTEGER,
    interests_score INTEGER,

    photo_analysis JSONB,  -- {has_smile: true, lighting: "good", face_visible: true, ...}
    bio_analysis JSONB,    -- {length: 150, tone: "friendly", uniqueness: 0.8, ...}

    status VARCHAR(20) DEFAULT 'completed',  -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,

    model_used VARCHAR(50),  -- 'gpt-4', 'gpt-4-vision', etc.
    tokens_used INTEGER,
    processing_time_ms INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- Рекомендации по улучшению профиля
CREATE TABLE profile_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    analysis_id UUID REFERENCES profile_analyses(id),

    type VARCHAR(50) NOT NULL,  -- 'photo', 'bio', 'interests', 'activity', 'strategy'
    priority VARCHAR(10) NOT NULL,  -- 'high', 'medium', 'low'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    action_type VARCHAR(50),  -- 'upload_photo', 'edit_bio', 'add_interests', etc.
    action_data JSONB,  -- дополнительные данные для действия

    -- Статус
    is_dismissed BOOLEAN DEFAULT FALSE,
    dismissed_at TIMESTAMPTZ,
    is_applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMPTZ,

    -- Эффективность (если применено)
    rating_before DECIMAL(5,2),
    rating_after DECIMAL(5,2),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ  -- рекомендации могут устаревать
);


-- Conversation starters (идеи для начала разговора)
CREATE TABLE conversation_starters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    match_id UUID NOT NULL,
    target_user_id UUID NOT NULL,

    -- Сгенерированные фразы
    starters JSONB NOT NULL,  -- [{text: "...", style: "funny"}, {text: "...", style: "thoughtful"}]
    context_used JSONB,  -- какие данные использовались для генерации

    -- Использование
    selected_index INTEGER,  -- какой вариант выбрал пользователь
    was_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,

    -- Результат (для обучения)
    got_response BOOLEAN,
    response_time_minutes INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ПРИМЕЧАНИЕ: Embeddings хранятся в Qdrant (Vector DB), не в PostgreSQL

-- AI запросы (для аудита и дебага)
CREATE TABLE ai_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,

    -- Запрос
    request_type VARCHAR(50) NOT NULL,  -- 'analyze_profile', 'generate_starters', 'suggest_bio'
    model VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,

    -- Ответ
    response_status VARCHAR(20),  -- 'success', 'error', 'timeout'
    latency_ms INTEGER,
    error_message TEXT,

    -- Стоимость
    cost_usd DECIMAL(10,6),

    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- Feedback на AI рекомендации (для улучшения модели)
CREATE TABLE ai_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    recommendation_id UUID REFERENCES profile_recommendations(id),

    -- Feedback
    rating INTEGER,  -- 1-5 stars
    feedback_type VARCHAR(20),  -- 'helpful', 'not_helpful', 'irrelevant', 'offensive'
    comment TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_feedback_recommendation ON ai_feedback(recommendation_id);
```

---

## 8. Qdrant (Vector Database)

Qdrant используется для хранения и поиска векторных embeddings профилей.

### Collections

```yaml
# profiles_embeddings collection
collection_name: "profiles"
vector_size: 1536  # OpenAI text-embedding-3-small
distance: Cosine

# Payload schema
payload:
  user_id: uuid
  bio_text: string
  interests: string[]
  gender: string
  age: integer
  city: string
  updated_at: datetime

# Indexes для фильтрации
payload_indexes:
  - field: gender
    type: keyword
  - field: age
    type: integer
  - field: city
    type: keyword
```

