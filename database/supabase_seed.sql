-- LifeLink Synthetic Demo Data for Supabase PostgreSQL
-- Populates 20 Donors, 5 Hospitals, 5 Pharmacies, 30 Medicines, Blood Stock, Requests & Notifications.
-- Default Password for all seed users: Password123!
-- Hash: $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW

-- 1. USERS (Admin, Patients, Donors, Hospitals, Pharmacies)
INSERT INTO users (id, full_name, email, phone, password_hash, role, address, city, latitude, longitude, is_active) VALUES
(1, 'LifeLink Admin', 'admin@lifelink.org', '+91 9876543210', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', 'Central Health Admin Tower', 'Bengaluru', 12.9716, 77.5946, TRUE),
(2, 'Aarav Sharma', 'patient1@example.com', '+91 9812345670', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'patient', '102 MG Road, Indiranagar', 'Bengaluru', 12.9784, 77.6408, TRUE),
(3, 'Priya Patel', 'patient2@example.com', '+91 9812345671', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'patient', '45 Koramangala 4th Block', 'Bengaluru', 12.9352, 77.6245, TRUE),

-- Donors (User IDs 4 to 23)
(4, 'Ravi Kumar', 'ravi.kumar@example.com', '+91 9900112233', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Indiranagar 100ft Road', 'Bengaluru', 12.9719, 77.6412, TRUE),
(5, 'Sneha Rao', 'sneha.rao@example.com', '+91 9900112234', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Koramangala 80ft Road', 'Bengaluru', 12.9340, 77.6220, TRUE),
(6, 'Vikram Singh', 'vikram.singh@example.com', '+91 9900112235', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'HSR Layout Sector 2', 'Bengaluru', 12.9121, 77.6445, TRUE),
(7, 'Ananya Deshmukh', 'ananya.d@example.com', '+91 9900112236', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Jayanagar 4th Block', 'Bengaluru', 12.9250, 77.5938, TRUE),
(8, 'Karthik Raja', 'karthik.r@example.com', '+91 9900112237', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Whitefield Main Road', 'Bengaluru', 12.9698, 77.7499, TRUE),
(9, 'Deepa Nair', 'deepa.nair@example.com', '+91 9900112238', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Marathahalli Bridge', 'Bengaluru', 12.9591, 77.6974, TRUE),
(10, 'Rahul Verma', 'rahul.verma@example.com', '+91 9900112239', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'BTM Layout 2nd Stage', 'Bengaluru', 12.9166, 77.6101, TRUE),
(11, 'Meera Joshi', 'meera.j@example.com', '+91 9900112240', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'JP Nagar 6th Phase', 'Bengaluru', 12.9063, 77.5857, TRUE),
(12, 'Arjun Reddy', 'arjun.reddy@example.com', '+91 9900112241', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Banashankari 3rd Stage', 'Bengaluru', 12.9255, 77.5468, TRUE),
(13, 'Kavya Menon', 'kavya.m@example.com', '+91 9900112242', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Malleshwaram 18th Cross', 'Bengaluru', 12.9982, 77.5704, TRUE),
(14, 'Sanjay Gupta', 'sanjay.g@example.com', '+91 9900112243', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Rajajinagar 1st Block', 'Bengaluru', 12.9901, 77.5523, TRUE),
(15, 'Pooja Hegde', 'pooja.h@example.com', '+91 9900112244', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Hebbal Flyover', 'Bengaluru', 13.0358, 77.5970, TRUE),
(16, 'Manish Chawla', 'manish.c@example.com', '+91 9900112245', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Yelahanka New Town', 'Bengaluru', 13.0998, 77.5971, TRUE),
(17, 'Divya Pillai', 'divya.p@example.com', '+91 9900112246', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Electronic City Phase 1', 'Bengaluru', 12.8452, 77.6602, TRUE),
(18, 'Nikhil Sharma', 'nikhil.s@example.com', '+91 9900112247', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Bellandur EcoSpace', 'Bengaluru', 12.9260, 77.6762, TRUE),
(19, 'Swati Bhatt', 'swati.b@example.com', '+91 9900112248', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Sarjapur Road', 'Bengaluru', 12.9087, 77.6871, TRUE),
(20, 'Gautam Nambiar', 'gautam.n@example.com', '+91 9900112249', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Domlur Layout', 'Bengaluru', 12.9609, 77.6387, TRUE),
(21, 'Ritu Sen', 'ritu.sen@example.com', '+91 9900112250', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Old Airport Road', 'Bengaluru', 12.9568, 77.6534, TRUE),
(22, 'Amitabh Roy', 'amitabh.r@example.com', '+91 9900112251', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Ulsoor Lake Circle', 'Bengaluru', 12.9817, 77.6189, TRUE),
(23, 'Bhavana K', 'bhavana.k@example.com', '+91 9900112252', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', 'Frazer Town', 'Bengaluru', 12.9968, 77.6133, TRUE),

-- Hospitals (User IDs 24 to 28)
(24, 'Manipal Hospital Indiranagar', 'manipal@lifelink.org', '+91 8025024444', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'hospital', '98 HAL Old Airport Rd', 'Bengaluru', 12.9585, 77.6483, TRUE),
(25, 'Apollo Hospitals Bannerghatta', 'apollo@lifelink.org', '+91 8026304050', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'hospital', '154/11 Bannerghatta Road', 'Bengaluru', 12.8950, 77.5988, TRUE),
(26, 'Fortis Hospital Cunningham', 'fortis@lifelink.org', '+91 8041994444', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'hospital', '14 Cunningham Road', 'Bengaluru', 12.9882, 77.5960, TRUE),
(27, 'St. Johns Medical College Hospital', 'stjohns@lifelink.org', '+91 8022065000', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'hospital', 'Sarjapur Main Road, Koramangala', 'Bengaluru', 12.9322, 77.6198, TRUE),
(28, 'Narayana Health City', 'narayana@lifelink.org', '+91 8071222222', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'hospital', '258/A Bommasandra Industrial Area', 'Bengaluru', 12.8124, 77.6941, TRUE),

-- Pharmacies (User IDs 29 to 33)
(29, 'Apollo Pharmacy Koramangala', 'apollopharm1@lifelink.org', '+91 8025531122', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'pharmacy', '12 Koramangala 5th Block', 'Bengaluru', 12.9350, 77.6150, TRUE),
(30, 'MedPlus Indiranagar', 'medplus1@lifelink.org', '+91 8025203344', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'pharmacy', '412 100ft Road Indiranagar', 'Bengaluru', 12.9740, 77.6400, TRUE),
(31, 'Wellness Forever Jayanagar', 'wellness1@lifelink.org', '+91 8026645566', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'pharmacy', '88 11th Main Jayanagar', 'Bengaluru', 12.9280, 77.5890, TRUE),
(32, 'Aster Pharmacy Whitefield', 'asterpharm1@lifelink.org', '+91 8028457788', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'pharmacy', 'ITPL Main Road Whitefield', 'Bengaluru', 12.9850, 77.7310, TRUE),
(33, 'Frank Ross Pharmacy HSR', 'frankross1@lifelink.org', '+91 8025729900', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'pharmacy', 'Sector 1 HSR Layout', 'Bengaluru', 12.9150, 77.6510, TRUE)
ON CONFLICT (id) DO NOTHING;

SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- 2. DONORS DETAILS
INSERT INTO donors (id, user_id, blood_group, date_of_birth, last_donation_date, availability_status, latitude, longitude, city, response_rate, total_donations, verified) VALUES
(1, 4, 'O+', '1992-05-14', '2025-10-15', 'available', 12.9719, 77.6412, 'Bengaluru', 95.0, 6, TRUE),
(2, 5, 'A+', '1995-08-22', '2025-11-20', 'available', 12.9340, 77.6220, 'Bengaluru', 90.0, 4, TRUE),
(3, 6, 'B+', '1988-12-10', '2025-09-01', 'available', 12.9121, 77.6445, 'Bengaluru', 98.0, 12, TRUE),
(4, 7, 'O-', '1990-03-18', '2025-08-10', 'available', 12.9250, 77.5938, 'Bengaluru', 100.0, 8, TRUE),
(5, 8, 'AB+', '1996-07-04', '2025-12-05', 'available', 12.9698, 77.7499, 'Bengaluru', 85.0, 3, TRUE),
(6, 9, 'A-', '1994-01-30', '2025-07-14', 'available', 12.9591, 77.6974, 'Bengaluru', 92.0, 5, TRUE),
(7, 10, 'B-', '1991-11-11', '2025-06-25', 'available', 12.9166, 77.6101, 'Bengaluru', 88.0, 7, TRUE),
(8, 11, 'AB-', '1997-09-09', '2025-10-01', 'available', 12.9063, 77.5857, 'Bengaluru', 80.0, 2, TRUE),
(9, 12, 'O+', '1989-04-25', '2026-01-10', 'unavailable', 12.9255, 77.5468, 'Bengaluru', 75.0, 9, TRUE),
(10, 13, 'A+', '1993-06-17', '2025-05-19', 'available', 12.9982, 77.5704, 'Bengaluru', 94.0, 6, TRUE),
(11, 14, 'B+', '1995-02-12', '2025-11-11', 'available', 12.9901, 77.5523, 'Bengaluru', 96.0, 5, TRUE),
(12, 15, 'O-', '1992-10-08', '2025-04-04', 'available', 13.0358, 77.5970, 'Bengaluru', 99.0, 10, TRUE),
(13, 16, 'A-', '1998-03-03', '2025-09-30', 'available', 13.0998, 77.5971, 'Bengaluru', 87.0, 3, TRUE),
(14, 17, 'AB+', '1990-12-24', '2025-08-15', 'available', 12.8452, 77.6602, 'Bengaluru', 91.0, 4, TRUE),
(15, 18, 'O+', '1996-01-19', '2025-10-10', 'available', 12.9260, 77.6762, 'Bengaluru', 93.0, 7, TRUE),
(16, 19, 'B+', '1994-07-27', '2025-07-07', 'available', 12.9087, 77.6871, 'Bengaluru', 89.0, 5, TRUE),
(17, 20, 'O+', '1991-08-14', '2025-11-01', 'available', 12.9609, 77.6387, 'Bengaluru', 97.0, 8, TRUE),
(18, 21, 'A+', '1993-09-21', '2025-12-12', 'available', 12.9568, 77.6534, 'Bengaluru', 92.0, 4, TRUE),
(19, 22, 'B-', '1987-04-09', '2025-06-01', 'available', 12.9817, 77.6189, 'Bengaluru', 90.0, 11, TRUE),
(20, 23, 'AB-', '1999-11-30', '2025-10-20', 'available', 12.9968, 77.6133, 'Bengaluru', 82.0, 2, TRUE)
ON CONFLICT (id) DO NOTHING;

SELECT setval('donors_id_seq', (SELECT MAX(id) FROM donors));

-- 3. HOSPITALS DETAILS
INSERT INTO hospitals (id, user_id, hospital_name, registration_number, phone, address, city, latitude, longitude, verified) VALUES
(1, 24, 'Manipal Hospital Indiranagar', 'REG-KA-BLR-001', '+91 8025024444', '98 HAL Old Airport Rd', 'Bengaluru', 12.9585, 77.6483, TRUE),
(2, 25, 'Apollo Hospitals Bannerghatta', 'REG-KA-BLR-002', '+91 8026304050', '154/11 Bannerghatta Road', 'Bengaluru', 12.8950, 77.5988, TRUE),
(3, 26, 'Fortis Hospital Cunningham', 'REG-KA-BLR-003', '+91 8041994444', '14 Cunningham Road', 'Bengaluru', 12.9882, 77.5960, TRUE),
(4, 27, 'St. Johns Medical College Hospital', 'REG-KA-BLR-004', '+91 8022065000', 'Sarjapur Main Road, Koramangala', 'Bengaluru', 12.9322, 77.6198, TRUE),
(5, 28, 'Narayana Health City', 'REG-KA-BLR-005', '+91 8071222222', '258/A Bommasandra Industrial Area', 'Bengaluru', 12.8124, 77.6941, TRUE)
ON CONFLICT (id) DO NOTHING;

SELECT setval('hospitals_id_seq', (SELECT MAX(id) FROM hospitals));

-- 4. PHARMACIES DETAILS
INSERT INTO pharmacies (id, user_id, pharmacy_name, phone, address, city, latitude, longitude, opening_time, closing_time, verified) VALUES
(1, 29, 'Apollo Pharmacy Koramangala', '+91 8025531122', '12 Koramangala 5th Block', 'Bengaluru', 12.9350, 77.6150, '07:00', '23:00', TRUE),
(2, 30, 'MedPlus Indiranagar', '+91 8025203344', '412 100ft Road Indiranagar', 'Bengaluru', 12.9740, 77.6400, '08:00', '22:30', TRUE),
(3, 31, 'Wellness Forever Jayanagar', '+91 8026645566', '88 11th Main Jayanagar', 'Bengaluru', 12.9280, 77.5890, '00:00', '23:59', TRUE),
(4, 32, 'Aster Pharmacy Whitefield', '+91 8028457788', 'ITPL Main Road Whitefield', 'Bengaluru', 12.9850, 77.7310, '08:00', '22:00', TRUE),
(5, 33, 'Frank Ross Pharmacy HSR', '+91 8025729900', 'Sector 1 HSR Layout', 'Bengaluru', 12.9150, 77.6510, '08:30', '21:30', TRUE)
ON CONFLICT (id) DO NOTHING;

SELECT setval('pharmacies_id_seq', (SELECT MAX(id) FROM pharmacies));

-- 5. BLOOD STOCK (Hospitals 1 to 5, all 8 blood groups)
INSERT INTO blood_stock (hospital_id, blood_group, units_available, low_stock_threshold) VALUES
-- Manipal
(1, 'A+', 15, 5), (1, 'A-', 3, 5), (1, 'B+', 20, 5), (1, 'B-', 2, 5), (1, 'AB+', 8, 5), (1, 'AB-', 1, 5), (1, 'O+', 25, 5), (1, 'O-', 4, 5),
-- Apollo
(2, 'A+', 10, 5), (2, 'A-', 2, 5), (2, 'B+', 14, 5), (2, 'B-', 4, 5), (2, 'AB+', 6, 5), (2, 'AB-', 2, 5), (2, 'O+', 18, 5), (2, 'O-', 2, 5),
-- Fortis
(3, 'A+', 8, 5), (3, 'A-', 1, 5), (3, 'B+', 12, 5), (3, 'B-', 3, 5), (3, 'AB+', 5, 5), (3, 'AB-', 0, 5), (3, 'O+', 15, 5), (3, 'O-', 1, 5),
-- St. Johns
(4, 'A+', 22, 5), (4, 'A-', 6, 5), (4, 'B+', 30, 5), (4, 'B-', 5, 5), (4, 'AB+', 12, 5), (4, 'AB-', 3, 5), (4, 'O+', 35, 5), (4, 'O-', 7, 5),
-- Narayana
(5, 'A+', 18, 5), (5, 'A-', 4, 5), (5, 'B+', 25, 5), (5, 'B-', 4, 5), (5, 'AB+', 9, 5), (5, 'AB-', 2, 5), (5, 'O+', 28, 5), (5, 'O-', 5, 5)
ON CONFLICT (hospital_id, blood_group) DO UPDATE SET units_available = EXCLUDED.units_available;

-- 6. MEDICINES (30 entries across 5 pharmacies)
INSERT INTO medicines (pharmacy_id, medicine_name, generic_name, category, quantity, unit, price, availability_status) VALUES
(1, 'Paracetamol 650mg', 'Acetaminophen', 'Analgesics / Antipyretics', 150, 'tablets', 32.50, 'in_stock'),
(1, 'Amoxicillin 500mg', 'Amoxicillin Trihydrate', 'Antibiotics', 60, 'capsules', 120.00, 'in_stock'),
(1, 'Azithromycin 500mg', 'Azithromycin', 'Antibiotics', 25, 'strips', 145.00, 'in_stock'),
(1, 'Insulin Glargine 100IU', 'Insulin Glargine', 'Diabetes', 8, 'pens', 850.00, 'low_stock'),
(1, 'Pantoprazole 40mg', 'Pantoprazole', 'Gastrointestinal', 100, 'strips', 85.00, 'in_stock'),
(1, 'Remdesivir 100mg', 'Remdesivir', 'Antiviral', 0, 'vials', 2800.00, 'out_of_stock'),

(2, 'Paracetamol 650mg', 'Acetaminophen', 'Analgesics / Antipyretics', 200, 'tablets', 30.00, 'in_stock'),
(2, 'Metformin 500mg', 'Metformin HCl', 'Diabetes', 180, 'tablets', 45.00, 'in_stock'),
(2, 'Atorvastatin 10mg', 'Atorvastatin', 'Cardiovascular', 90, 'strips', 110.00, 'in_stock'),
(2, 'Amlodipine 5mg', 'Amlodipine Besylate', 'Cardiovascular', 120, 'strips', 55.00, 'in_stock'),
(2, 'Ceftriaxone 1g', 'Ceftriaxone Sodium', 'Antibiotics', 15, 'vials', 95.00, 'in_stock'),
(2, 'Human Albumin 20%', 'Human Albumin', 'Emergency Blood Products', 2, 'bottles', 4500.00, 'low_stock'),

(3, 'Paracetamol 650mg', 'Acetaminophen', 'Analgesics / Antipyretics', 300, 'tablets', 28.00, 'in_stock'),
(3, 'Ibuprofen 400mg', 'Ibuprofen', 'NSAID Painkillers', 140, 'tablets', 40.00, 'in_stock'),
(3, 'Enoxaparin 40mg', 'Enoxaparin Sodium', 'Anticoagulants', 6, 'syringes', 620.00, 'low_stock'),
(3, 'Normal Saline 0.9%', 'Sodium Chloride', 'IV Fluids', 50, 'bottles', 35.00, 'in_stock'),
(3, 'Dextrose 5%', 'Dextrose Monohydrate', 'IV Fluids', 40, 'bottles', 38.00, 'in_stock'),
(3, 'Adrenaline Injection 1mg/ml', 'Epinephrine', 'Emergency Life Support', 10, 'ampoules', 85.00, 'in_stock'),

(4, 'Augmentin 625mg', 'Amoxicillin + Clavulanic Acid', 'Antibiotics', 85, 'strips', 210.00, 'in_stock'),
(4, 'Telmisartan 40mg', 'Telmisartan', 'Cardiovascular', 110, 'strips', 78.00, 'in_stock'),
(4, 'Levothyroxine 50mcg', 'Levothyroxine Sodium', 'Thyroid', 95, 'tablets', 135.00, 'in_stock'),
(4, 'Salbutamol Inhaler 100mcg', 'Salbutamol', 'Respiratory', 18, 'inhalers', 160.00, 'in_stock'),
(4, 'Ondansetron 4mg', 'Ondansetron', 'Antiemetic', 70, 'strips', 52.00, 'in_stock'),
(4, 'Dexamethasone 4mg', 'Dexamethasone', 'Steroids', 4, 'vials', 45.00, 'low_stock'),

(5, 'Paracetamol 650mg', 'Acetaminophen', 'Analgesics / Antipyretics', 110, 'tablets', 31.00, 'in_stock'),
(5, 'Ciprofloxacin 500mg', 'Ciprofloxacin', 'Antibiotics', 50, 'strips', 88.00, 'in_stock'),
(5, 'Ranitidine 150mg', 'Ranitidine HCl', 'Gastrointestinal', 0, 'strips', 25.00, 'out_of_stock'),
(5, 'Oral Rehydration Salts', 'ORS Formula', 'Electrolytes', 200, 'sachets', 18.00, 'in_stock'),
(5, 'Tramadol 50mg', 'Tramadol HCl', 'Analgesics', 30, 'capsules', 115.00, 'in_stock'),
(5, 'Furosemide 40mg', 'Furosemide', 'Diuretics', 45, 'strips', 34.00, 'in_stock');

-- 7. BLOOD REQUESTS
INSERT INTO blood_requests (id, requester_id, hospital_id, blood_group, units_required, priority, required_by, latitude, longitude, hospital_name, additional_notes, status) VALUES
(1, 2, 1, 'O+', 2, 'critical', '2026-08-12 18:00:00+00', 12.9585, 77.6483, 'Manipal Hospital Indiranagar', 'Emergency trauma unit requirement', 'donor_notified'),
(2, 3, 4, 'A+', 1, 'urgent', '2026-08-13 12:00:00+00', 12.9322, 77.6198, 'St. Johns Medical College Hospital', 'Scheduled cardiac surgery', 'donor_accepted'),
(3, 2, 2, 'O-', 3, 'critical', '2026-08-12 21:00:00+00', 12.8950, 77.5988, 'Apollo Hospitals Bannerghatta', 'Severe anemia case in ICU', 'searching')
ON CONFLICT (id) DO NOTHING;

SELECT setval('blood_requests_id_seq', (SELECT MAX(id) FROM blood_requests));

-- 8. DONOR MATCHES FOR REQUEST 1
INSERT INTO donor_matches (request_id, donor_id, match_score, distance_km, estimated_minutes, blood_compatibility, availability_score, distance_score, response_score, eligibility_score, match_reasons, status) VALUES
(1, 1, 95, 1.8, 5, 30, 20, 19, 16, 10, 'Compatible blood group | Available now | Located within 2 km | High response rate | Recorded donation history indicates eligibility', 'notified'),
(1, 17, 92, 1.5, 4, 30, 20, 20, 12, 10, 'Compatible blood group | Available now | Located nearby | Recorded donation history indicates eligibility', 'notified'),
(1, 15, 88, 5.2, 15, 30, 20, 14, 14, 10, 'Compatible blood group | Available now | Recorded donation history indicates eligibility', 'notified'),
(2, 2, 94, 0.8, 3, 30, 20, 20, 14, 10, 'Compatible blood group | Available now | Located within 1 km | Accepted emergency request', 'accepted');

-- 9. NOTIFICATIONS
INSERT INTO notifications (user_id, title, message, type, reference_id, is_read) VALUES
(4, 'CRITICAL BLOOD EMERGENCY NEAR YOU', 'Manipal Hospital Indiranagar requires 2 units of O+ blood. Match Score: 95/100.', 'emergency_request', 1, FALSE),
(2, 'DONOR MATCHED & ACCEPTED', 'Donor Priya Patel (A+) accepted your blood request for St. Johns Hospital.', 'donor_accepted', 2, TRUE),
(24, 'LOW BLOOD STOCK ALERT', 'AB- blood group stock has reached 1 unit (Below threshold 5).', 'stock_alert', 1, FALSE);
