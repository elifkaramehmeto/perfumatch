-- PerfuMatch Veritabanı Şeması
-- Veritabanı ve kullanıcı oluşturma (Docker tarafından yapılacak)

-- Uzantıları etkinleştir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Markalar tablosu
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(20) CHECK (type IN ('luxury', 'alternative')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parfüm aileleri tablosu
CREATE TABLE IF NOT EXISTS perfume_families (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notalar tablosu
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) UNIQUE NOT NULL,
    type VARCHAR(20) CHECK (type IN ('top', 'middle', 'base')) NOT NULL,
    category VARCHAR(50), -- floral, woody, citrus, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parfümler tablosu
CREATE TABLE IF NOT EXISTS perfumes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    brand_id INTEGER REFERENCES brands(id),
    family_id INTEGER REFERENCES perfume_families(id),
    gender VARCHAR(20) CHECK (gender IN ('men', 'women', 'unisex')) NOT NULL,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'TRY',
    volume INTEGER, -- ml cinsinden
    concentration VARCHAR(20), -- EDP, EDT, Parfum, etc.
    description TEXT,
    image_url TEXT,
    product_url TEXT,
    stock_status BOOLEAN DEFAULT true,
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    perfumer VARCHAR(100),
    release_year INTEGER,
    longevity_rating DECIMAL(3,2),
    sillage_rating DECIMAL(3,2),
    bottle_rating DECIMAL(3,2),
    value_rating DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parfüm-nota ilişki tablosu
CREATE TABLE IF NOT EXISTS perfume_notes (
    id SERIAL PRIMARY KEY,
    perfume_id INTEGER REFERENCES perfumes(id) ON DELETE CASCADE,
    note_id INTEGER REFERENCES notes(id),
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10) DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(perfume_id, note_id)
);

-- Parfüm benzerlik tablosu
CREATE TABLE IF NOT EXISTS perfume_similarities (
    id SERIAL PRIMARY KEY,
    luxury_perfume_id INTEGER REFERENCES perfumes(id),
    alternative_perfume_id INTEGER REFERENCES perfumes(id),
    similarity_score DECIMAL(5,2) CHECK (similarity_score >= 0 AND similarity_score <= 100),
    note_similarity DECIMAL(5,2),
    family_similarity DECIMAL(5,2),
    gender_match BOOLEAN,
    price_difference DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(luxury_perfume_id, alternative_perfume_id)
);

-- Kullanıcı değerlendirmeleri tablosu
CREATE TABLE IF NOT EXISTS user_ratings (
    id SERIAL PRIMARY KEY,
    perfume_id INTEGER REFERENCES perfumes(id),
    similarity_id INTEGER REFERENCES perfume_similarities(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    helpful_count INTEGER DEFAULT 0,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Arama geçmişi tablosu
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    search_term VARCHAR(200),
    search_type VARCHAR(20) CHECK (search_type IN ('name', 'notes', 'family')),
    results_count INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_perfumes_brand ON perfumes(brand_id);
CREATE INDEX IF NOT EXISTS idx_perfumes_family ON perfumes(family_id);
CREATE INDEX IF NOT EXISTS idx_perfumes_gender ON perfumes(gender);
CREATE INDEX IF NOT EXISTS idx_perfumes_name ON perfumes USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_perfume_notes_perfume ON perfume_notes(perfume_id);
CREATE INDEX IF NOT EXISTS idx_perfume_notes_note ON perfume_notes(note_id);
CREATE INDEX IF NOT EXISTS idx_similarities_luxury ON perfume_similarities(luxury_perfume_id);
CREATE INDEX IF NOT EXISTS idx_similarities_alternative ON perfume_similarities(alternative_perfume_id);
CREATE INDEX IF NOT EXISTS idx_similarities_score ON perfume_similarities(similarity_score DESC);

-- Trigger fonksiyonu - updated_at otomatik güncelleme
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger'ları oluştur
CREATE TRIGGER update_perfumes_updated_at BEFORE UPDATE ON perfumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_similarities_updated_at BEFORE UPDATE ON perfume_similarities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Temel veri ekleme
INSERT INTO brands (name, type) VALUES 
    ('Chanel', 'luxury'),
    ('Dior', 'luxury'),
    ('Tom Ford', 'luxury'),
    ('Yves Saint Laurent', 'luxury'),
    ('Giorgio Armani', 'luxury'),
    ('Versace', 'luxury'),
    ('Gucci', 'luxury'),
    ('Prada', 'luxury'),
    ('Hermès', 'luxury'),
    ('Creed', 'luxury'),
    ('Bargello', 'alternative'),
    ('Muscent', 'alternative'),
    ('Zara', 'alternative'),
    ('Golden Scent', 'alternative'),
    ('Farmasi', 'alternative')
ON CONFLICT (name) DO NOTHING;

INSERT INTO perfume_families (name, description) VALUES 
    ('Floral', 'Çiçeksi kokular - gül, yasemin, lavanta'),
    ('Woody', 'Odunsu kokular - sedir, sandal ağacı, vetiver'),
    ('Oriental', 'Oriental kokular - amber, vanilya, baharat'),
    ('Fresh', 'Taze kokular - turunçgiller, deniz notaları'),
    ('Fruity', 'Meyveli kokular - elma, şeftali, mango'),
    ('Chypre', 'Chipre ailesi - meşe yosunu, paçuli'),
    ('Fougere', 'Fougere ailesi - lavanta, kumarin'),
    ('Gourmand', 'Gurme kokular - vanilya, çikolata, karamel')
ON CONFLICT (name) DO NOTHING;

INSERT INTO notes (name, type, category) VALUES 
    ('Bergamot', 'top', 'citrus'),
    ('Limon', 'top', 'citrus'),
    ('Portakal', 'top', 'citrus'),
    ('Greyfurt', 'top', 'citrus'),
    ('Mandalina', 'top', 'citrus'),
    ('Elma', 'top', 'fruity'),
    ('Şeftali', 'top', 'fruity'),
    ('Armut', 'top', 'fruity'),
    ('Siyah Frenk Üzümü', 'top', 'fruity'),
    ('Pembe Biber', 'top', 'spicy'),
    ('Karabiber', 'top', 'spicy'),
    ('Zencefil', 'top', 'spicy'),
    ('Kakule', 'top', 'spicy'),
    ('Yasemin', 'middle', 'floral'),
    ('Gül', 'middle', 'floral'),
    ('Lavanta', 'middle', 'floral'),
    ('Süsen', 'middle', 'floral'),
    ('Portakal Çiçeği', 'middle', 'floral'),
    ('Neroli', 'middle', 'floral'),
    ('Gardenya', 'middle', 'floral'),
    ('Tarçın', 'middle', 'spicy'),
    ('Karanfil', 'middle', 'spicy'),
    ('Safran', 'middle', 'spicy'),
    ('Sedir', 'base', 'woody'),
    ('Sandal Ağacı', 'base', 'woody'),
    ('Vetiver', 'base', 'woody'),
    ('Paçuli', 'base', 'woody'),
    ('Amber', 'base', 'amber'),
    ('Misk', 'base', 'musk'),
    ('Vanilya', 'base', 'sweet'),
    ('Tonka Fasulyesi', 'base', 'sweet'),
    ('Kahve', 'base', 'gourmand'),
    ('Çikolata', 'base', 'gourmand'),
    ('Karamel', 'base', 'gourmand'),
    ('Deri', 'base', 'leather'),
    ('Tütün', 'base', 'tobacco'),
    ('Oud', 'base', 'woody')
ON CONFLICT (name) DO NOTHING; 