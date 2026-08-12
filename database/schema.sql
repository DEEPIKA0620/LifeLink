-- LifeLink Emergency Blood & Medicine Locator System
-- Database Schema (MySQL Compatible)

CREATE DATABASE IF NOT EXISTS lifelink_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lifelink_db;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'donor', 'hospital', 'pharmacy', 'admin') NOT NULL DEFAULT 'patient',
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) DEFAULT 0.0,
    longitude DECIMAL(11, 8) DEFAULT 0.0,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. DONORS TABLE
CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    date_of_birth DATE NOT NULL,
    last_donation_date DATE NULL,
    availability_status ENUM('available', 'unavailable') DEFAULT 'available',
    latitude DECIMAL(10, 8) DEFAULT 0.0,
    longitude DECIMAL(11, 8) DEFAULT 0.0,
    city VARCHAR(100) NOT NULL,
    response_rate DECIMAL(5, 2) DEFAULT 100.0,
    total_donations INT DEFAULT 0,
    verified TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_donors_blood_group (blood_group),
    INDEX idx_donors_availability (availability_status),
    INDEX idx_donors_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. HOSPITALS TABLE
CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    hospital_name VARCHAR(150) NOT NULL,
    registration_number VARCHAR(80) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) DEFAULT 0.0,
    longitude DECIMAL(11, 8) DEFAULT 0.0,
    verified TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_hospitals_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. PHARMACIES TABLE
CREATE TABLE IF NOT EXISTS pharmacies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    pharmacy_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) DEFAULT 0.0,
    longitude DECIMAL(11, 8) DEFAULT 0.0,
    opening_time VARCHAR(10) DEFAULT '08:00',
    closing_time VARCHAR(10) DEFAULT '22:00',
    verified TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_pharmacies_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. MEDICINES TABLE
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pharmacy_id INT NOT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    generic_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    quantity INT NOT NULL DEFAULT 0,
    unit VARCHAR(50) DEFAULT 'strips',
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    availability_status ENUM('in_stock', 'low_stock', 'out_of_stock') DEFAULT 'in_stock',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id) ON DELETE CASCADE,
    INDEX idx_medicines_name (medicine_name),
    INDEX idx_medicines_generic (generic_name),
    INDEX idx_medicines_status (availability_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. BLOOD REQUESTS TABLE
CREATE TABLE IF NOT EXISTS blood_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requester_id INT NOT NULL,
    hospital_id INT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_required INT NOT NULL DEFAULT 1,
    priority ENUM('critical', 'urgent', 'normal') DEFAULT 'normal',
    required_by DATETIME NOT NULL,
    latitude DECIMAL(10, 8) DEFAULT 0.0,
    longitude DECIMAL(11, 8) DEFAULT 0.0,
    hospital_name VARCHAR(150) NOT NULL,
    additional_notes TEXT NULL,
    status ENUM('pending', 'searching', 'donor_notified', 'donor_accepted', 'completed', 'cancelled') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    INDEX idx_requests_status (status),
    INDEX idx_requests_priority (priority),
    INDEX idx_requests_blood_group (blood_group)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. DONOR MATCHES TABLE
CREATE TABLE IF NOT EXISTS donor_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    donor_id INT NOT NULL,
    match_score INT NOT NULL DEFAULT 0,
    distance_km DECIMAL(8, 2) DEFAULT 0.0,
    estimated_minutes INT DEFAULT 0,
    blood_compatibility INT DEFAULT 0,
    availability_score INT DEFAULT 0,
    distance_score INT DEFAULT 0,
    response_score INT DEFAULT 0,
    eligibility_score INT DEFAULT 0,
    match_reasons TEXT NULL,
    status ENUM('notified', 'accepted', 'rejected', 'expired') DEFAULT 'notified',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES blood_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
    INDEX idx_matches_request (request_id),
    INDEX idx_matches_donor (donor_id),
    INDEX idx_matches_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. BLOOD STOCK TABLE
CREATE TABLE IF NOT EXISTS blood_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units_available INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 5,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    UNIQUE KEY uq_hospital_blood_group (hospital_id, blood_group)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. DONATION HISTORY TABLE
CREATE TABLE IF NOT EXISTS donation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    hospital_id INT NULL,
    donation_date DATE NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    units INT NOT NULL DEFAULT 1,
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('emergency_request', 'donor_accepted', 'donor_rejected', 'request_completed', 'stock_alert', 'system') DEFAULT 'system',
    reference_id INT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. REQUEST STATUS HISTORY TABLE
CREATE TABLE IF NOT EXISTS request_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    changed_by INT NULL,
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES blood_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    entity VARCHAR(100) NOT NULL,
    entity_id INT NULL,
    details TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
