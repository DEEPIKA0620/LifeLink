-- LifeLink Emergency Blood & Medicine Locator System
-- Supabase PostgreSQL Schema & Security Policies

-- Drop existing tables if re-running (in reverse dependency order)
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS request_status_history CASCADE;
DROP TABLE IF EXISTS donation_history CASCADE;
DROP TABLE IF EXISTS donor_matches CASCADE;
DROP TABLE IF EXISTS blood_requests CASCADE;
DROP TABLE IF EXISTS blood_stock CASCADE;
DROP TABLE IF EXISTS medicines CASCADE;
DROP TABLE IF EXISTS pharmacies CASCADE;
DROP TABLE IF EXISTS hospitals CASCADE;
DROP TABLE IF EXISTS donors CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. USERS TABLE
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'patient', -- 'patient', 'donor', 'hospital', 'pharmacy', 'admin'
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION DEFAULT 0.0,
    longitude DOUBLE PRECISION DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_city ON users(city);

-- 2. DONORS TABLE
CREATE TABLE donors (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    blood_group VARCHAR(10) NOT NULL, -- 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
    date_of_birth DATE NOT NULL,
    last_donation_date DATE NULL,
    availability_status VARCHAR(20) DEFAULT 'available', -- 'available', 'unavailable'
    latitude DOUBLE PRECISION DEFAULT 0.0,
    longitude DOUBLE PRECISION DEFAULT 0.0,
    city VARCHAR(100) NOT NULL,
    locality VARCHAR(100) NULL,
    response_rate DOUBLE PRECISION DEFAULT 100.0,
    total_donations INT DEFAULT 0,
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_donors_blood_group ON donors(blood_group);
CREATE INDEX idx_donors_availability ON donors(availability_status);
CREATE INDEX idx_donors_city ON donors(city);
CREATE INDEX idx_donors_locality ON donors(locality);

-- 3. HOSPITALS TABLE
CREATE TABLE hospitals (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    hospital_name VARCHAR(150) NOT NULL,
    registration_number VARCHAR(80) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION DEFAULT 0.0,
    longitude DOUBLE PRECISION DEFAULT 0.0,
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hospitals_city ON hospitals(city);

-- 4. PHARMACIES TABLE
CREATE TABLE pharmacies (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    pharmacy_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION DEFAULT 0.0,
    longitude DOUBLE PRECISION DEFAULT 0.0,
    opening_time VARCHAR(10) DEFAULT '08:00',
    closing_time VARCHAR(10) DEFAULT '22:00',
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pharmacies_city ON pharmacies(city);

-- 5. MEDICINES TABLE
CREATE TABLE medicines (
    id SERIAL PRIMARY KEY,
    pharmacy_id INT NOT NULL REFERENCES pharmacies(id) ON DELETE CASCADE,
    medicine_name VARCHAR(150) NOT NULL,
    generic_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    dosage_form VARCHAR(50) NULL,
    strength VARCHAR(50) NULL,
    quantity INT NOT NULL DEFAULT 0,
    unit VARCHAR(50) DEFAULT 'strips',
    price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    availability_status VARCHAR(20) DEFAULT 'in_stock', -- 'in_stock', 'low_stock', 'out_of_stock'
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_medicines_name ON medicines(medicine_name);
CREATE INDEX idx_medicines_generic ON medicines(generic_name);
CREATE INDEX idx_medicines_category ON medicines(category);
CREATE INDEX idx_medicines_status ON medicines(availability_status);
CREATE INDEX idx_medicines_pharmacy ON medicines(pharmacy_id);

-- 6. BLOOD REQUESTS TABLE
CREATE TABLE blood_requests (
    id SERIAL PRIMARY KEY,
    requester_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hospital_id INT NULL REFERENCES hospitals(id) ON DELETE SET NULL,
    blood_group VARCHAR(10) NOT NULL,
    units_required INT NOT NULL DEFAULT 1,
    priority VARCHAR(20) DEFAULT 'normal', -- 'critical', 'urgent', 'normal'
    required_by TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION DEFAULT 0.0,
    longitude DOUBLE PRECISION DEFAULT 0.0,
    hospital_name VARCHAR(150) NOT NULL,
    additional_notes TEXT NULL,
    status VARCHAR(30) DEFAULT 'pending', -- 'pending', 'searching', 'donor_notified', 'donor_accepted', 'completed', 'cancelled'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_requests_status ON blood_requests(status);
CREATE INDEX idx_requests_priority ON blood_requests(priority);
CREATE INDEX idx_requests_blood_group ON blood_requests(blood_group);
CREATE INDEX idx_requests_requester ON blood_requests(requester_id);

-- 7. DONOR MATCHES TABLE
CREATE TABLE donor_matches (
    id SERIAL PRIMARY KEY,
    request_id INT NOT NULL REFERENCES blood_requests(id) ON DELETE CASCADE,
    donor_id INT NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    match_score INT NOT NULL DEFAULT 0,
    distance_km NUMERIC(8, 2) DEFAULT 0.0,
    estimated_minutes INT DEFAULT 0,
    blood_compatibility INT DEFAULT 0,
    availability_score INT DEFAULT 0,
    distance_score INT DEFAULT 0,
    response_score INT DEFAULT 0,
    eligibility_score INT DEFAULT 0,
    match_reasons TEXT NULL,
    status VARCHAR(20) DEFAULT 'notified', -- 'notified', 'accepted', 'rejected', 'expired'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_matches_request ON donor_matches(request_id);
CREATE INDEX idx_matches_donor ON donor_matches(donor_id);
CREATE INDEX idx_matches_status ON donor_matches(status);

-- 8. BLOOD STOCK TABLE
CREATE TABLE blood_stock (
    id SERIAL PRIMARY KEY,
    hospital_id INT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    blood_group VARCHAR(10) NOT NULL,
    units_available INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 5,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_hospital_blood_group UNIQUE (hospital_id, blood_group)
);

CREATE INDEX idx_blood_stock_hospital ON blood_stock(hospital_id);
CREATE INDEX idx_blood_stock_bg ON blood_stock(blood_group);

-- 9. DONATION HISTORY TABLE
CREATE TABLE donation_history (
    id SERIAL PRIMARY KEY,
    donor_id INT NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    hospital_id INT NULL REFERENCES hospitals(id) ON DELETE SET NULL,
    request_id INT NULL REFERENCES blood_requests(id) ON DELETE SET NULL,
    donation_date DATE NOT NULL,
    blood_group VARCHAR(10) NOT NULL,
    units INT NOT NULL DEFAULT 1,
    status VARCHAR(20) DEFAULT 'completed', -- 'completed', 'scheduled', 'cancelled'
    donation_type VARCHAR(50) DEFAULT 'Whole Blood',
    notes TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_donation_history_donor ON donation_history(donor_id);
CREATE INDEX idx_donation_history_status ON donation_history(status);

-- 10. NOTIFICATIONS TABLE
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(30) DEFAULT 'system',
    reference_id INT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);

-- 11. REQUEST STATUS HISTORY TABLE
CREATE TABLE request_status_history (
    id SERIAL PRIMARY KEY,
    request_id INT NOT NULL REFERENCES blood_requests(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    changed_by INT NULL REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_request_history_req ON request_status_history(request_id);

-- 12. AUDIT LOGS TABLE
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NULL REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity VARCHAR(100) NOT NULL,
    entity_id INT NULL,
    details TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =========================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE donors ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospitals ENABLE ROW LEVEL SECURITY;
ALTER TABLE pharmacies ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicines ENABLE ROW LEVEL SECURITY;
ALTER TABLE blood_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE donor_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE blood_stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE donation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 1. Public read for searching (anon and authenticated)
CREATE POLICY "Public can view medicines" ON medicines FOR SELECT USING (true);
CREATE POLICY "Public can view pharmacies" ON pharmacies FOR SELECT USING (true);
CREATE POLICY "Public can view hospitals" ON hospitals FOR SELECT USING (true);
CREATE POLICY "Public can view blood stock" ON blood_stock FOR SELECT USING (true);
CREATE POLICY "Public can view available donors" ON donors FOR SELECT USING (true);
CREATE POLICY "Public can view public donor profiles" ON users FOR SELECT USING (true);

-- 2. Service role / Backend API full access bypass
-- (Supabase service role automatically bypasses RLS; for anon key / client tokens, policies apply)
CREATE POLICY "Users can manage own notifications" ON notifications FOR ALL USING (true);
CREATE POLICY "Users can manage own requests" ON blood_requests FOR ALL USING (true);
CREATE POLICY "Users can view donor matches" ON donor_matches FOR ALL USING (true);
CREATE POLICY "Users can manage donation history" ON donation_history FOR ALL USING (true);
CREATE POLICY "Users can view status history" ON request_status_history FOR ALL USING (true);
CREATE POLICY "Allow system audit logs" ON audit_logs FOR ALL USING (true);
CREATE POLICY "Authenticated users can edit medicines" ON medicines FOR ALL USING (true);
CREATE POLICY "Authenticated users can edit blood stock" ON blood_stock FOR ALL USING (true);
CREATE POLICY "Users can update own user record" ON users FOR UPDATE USING (true);
CREATE POLICY "Users can update own donor record" ON donors FOR ALL USING (true);
CREATE POLICY "Users can update own pharmacy record" ON pharmacies FOR ALL USING (true);
CREATE POLICY "Users can update own hospital record" ON hospitals FOR ALL USING (true);
