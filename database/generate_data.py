import os
import sys
import random
import math
from datetime import datetime, date, timedelta
import json

# Ensure backend app is on sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.blood_stock import BloodStock
from app.models.blood_request import BloodRequest
from app.models.donor_match import DonorMatch
from app.models.donation_history import DonationHistory
from app.models.notification import Notification
from app.utils.locations import SUPPORTED_LOCATIONS
from app.utils.distance import calculate_haversine_distance, estimate_travel_time_minutes

# Deterministic random seed for reproducibility
random.seed(42)

# Bcrypt hash for 'LifeLink@123'
PASSWORD_HASH = "$2b$12$OJw.fY9YesTedRYbEzKxgecgGGcRPpv7uisf67au0dtdmXO7hKgji"

BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]

FIRST_NAMES = [
    # Tamil & South Indian names
    "Karthik", "Murugan", "Vignesh", "Anitha", "Priya", "Divya", "Senthil", "Saravanan",
    "Jayanthi", "Deepa", "Meena", "Malathi", "Balaji", "Sundar", "Dhanush", "Revathi",
    "Selvam", "Rajan", "Kannan", "Lakshmi", "Bhuvanesh", "Gowri", "Madhavan", "Nandhini",
    "Pradeep", "Raghav", "Sangeetha", "Thirumalai", "Usha", "Venkat", "Yogesh", "Abirami",
    "Chandran", "Elango", "Hemalatha", "Ilango", "Kalaiarasan", "Manikandan", "Naveen", "Pavithra",
    # Karnataka & Telugu names
    "Ravi", "Sneha", "Vikram", "Ananya", "Arjun", "Kavya", "Sanjay", "Pooja", "Manish",
    "Suresh", "Girish", "Shilpa", "Harish", "Tejas", "Chaithra", "Varun", "Sindhu",
    "Venkatesh", "Srinivas", "Roopa", "Mahesh", "Sushma", "Praveen", "Ashok", "Keerthi",
    # Malayalam names
    "Deepak", "Asha", "Gautam", "Reshma", "Manoj", "Anju", "Sreejith", "Vineeth", "Akhil",
    # Pan-Indian / Marathi / North names
    "Rahul", "Meera", "Swati", "Nikhil", "Amit", "Neha", "Rohit", "Tanvi", "Aditya",
    "Simran", "Rajesh", "Kiran", "Pooja", "Akash", "Ritu", "Alok", "Sunita", "Gaurav"
]

LAST_NAMES = [
    "Kumar", "Raja", "Nair", "Iyer", "Iyengar", "Pillai", "Chettiar", "Gounder", "Nadai",
    "Mudaliar", "Rao", "Reddy", "Sharma", "Varma", "Deshmukh", "Patel", "Singh", "Joshi",
    "Bhatt", "Gupta", "Menon", "Chawla", "Sen", "Roy", "Nambiar", "Prasad", "Naidu",
    "Shetty", "Gowda", "Hegde", "Murthy", "Krishnan", "Subramanian", "Balasubramanian", "Raman"
]

MEDICINE_CATALOG = [
    # Pain Relief & Fever
    {"name": "Paracetamol 650mg", "generic": "Acetaminophen", "cat": "Pain Relief & Fever", "dosage": "Tablet", "strength": "650mg", "unit": "strips", "price": 32.50},
    {"name": "Paracetamol 500mg", "generic": "Acetaminophen", "cat": "Pain Relief & Fever", "dosage": "Tablet", "strength": "500mg", "unit": "strips", "price": 24.00},
    {"name": "Dolo 650", "generic": "Paracetamol", "cat": "Pain Relief & Fever", "dosage": "Tablet", "strength": "650mg", "unit": "strips", "price": 34.00},
    {"name": "Ibuprofen 400mg", "generic": "Ibuprofen", "cat": "Pain Relief & Fever", "dosage": "Tablet", "strength": "400mg", "unit": "strips", "price": 28.50},
    {"name": "Combiflam", "generic": "Ibuprofen & Paracetamol", "cat": "Pain Relief & Fever", "dosage": "Tablet", "strength": "400mg/325mg", "unit": "strips", "price": 42.00},
    {"name": "Tramadol 50mg", "generic": "Tramadol Hydrochloride", "cat": "Pain Relief & Fever", "dosage": "Capsule", "strength": "50mg", "unit": "strips", "price": 85.00},
    {"name": "Aceclofenac 100mg", "generic": "Aceclofenac", "cat": "Pain Relief & Fever", "dosage": "Tablet", "strength": "100mg", "unit": "strips", "price": 55.00},
    {"name": "Diclofenac Gel 30g", "generic": "Diclofenac Diethylamine", "cat": "Pain Relief & Fever", "dosage": "Ointment", "strength": "1.16% w/w", "unit": "tube", "price": 75.00},

    # Antibiotics
    {"name": "Amoxicillin 500mg", "generic": "Amoxicillin Trihydrate", "cat": "Antibiotics", "dosage": "Capsule", "strength": "500mg", "unit": "strips", "price": 105.00},
    {"name": "Augmentin 625 Duo", "generic": "Amoxicillin & Potassium Clavulanate", "cat": "Antibiotics", "dosage": "Tablet", "strength": "625mg", "unit": "strips", "price": 198.50},
    {"name": "Azithromycin 500mg", "generic": "Azithromycin", "cat": "Antibiotics", "dosage": "Tablet", "strength": "500mg", "unit": "strips", "price": 125.00},
    {"name": "Azithromycin 250mg", "generic": "Azithromycin", "cat": "Antibiotics", "dosage": "Tablet", "strength": "250mg", "unit": "strips", "price": 72.00},
    {"name": "Ciprofloxacin 500mg", "generic": "Ciprofloxacin", "cat": "Antibiotics", "dosage": "Tablet", "strength": "500mg", "unit": "strips", "price": 52.00},
    {"name": "Doxycycline 100mg", "generic": "Doxycycline Hyclate", "cat": "Antibiotics", "dosage": "Capsule", "strength": "100mg", "unit": "strips", "price": 68.00},
    {"name": "Cefixime 200mg", "generic": "Cefixime Trihydrate", "cat": "Antibiotics", "dosage": "Tablet", "strength": "200mg", "unit": "strips", "price": 145.00},
    {"name": "Metronidazole 400mg", "generic": "Metronidazole", "cat": "Antibiotics", "dosage": "Tablet", "strength": "400mg", "unit": "strips", "price": 22.00},

    # Allergy & Respiratory
    {"name": "Cetirizine 10mg", "generic": "Cetirizine Hydrochloride", "cat": "Allergy Medicines", "dosage": "Tablet", "strength": "10mg", "unit": "strips", "price": 18.50},
    {"name": "Levocetirizine 5mg", "generic": "Levocetirizine Dihydrochloride", "cat": "Allergy Medicines", "dosage": "Tablet", "strength": "5mg", "unit": "strips", "price": 45.00},
    {"name": "Montelukast 10mg", "generic": "Montelukast Sodium", "cat": "Allergy Medicines", "dosage": "Tablet", "strength": "10mg", "unit": "strips", "price": 115.00},
    {"name": "Allegra 120mg", "generic": "Fexofenadine Hydrochloride", "cat": "Allergy Medicines", "dosage": "Tablet", "strength": "120mg", "unit": "strips", "price": 185.00},
    {"name": "Salbutamol Inhaler 100mcg", "generic": "Salbutamol", "cat": "Respiratory Care", "dosage": "Inhaler", "strength": "100mcg", "unit": "inhaler", "price": 145.00},
    {"name": "Budesonide Respules 0.5mg", "generic": "Budesonide", "cat": "Respiratory Care", "dosage": "Respules", "strength": "0.5mg", "unit": "pack", "price": 165.00},
    {"name": "Foracort Inhaler 200", "generic": "Formoterol & Budesonide", "cat": "Respiratory Care", "dosage": "Inhaler", "strength": "200mcg", "unit": "inhaler", "price": 380.00},

    # Diabetes Care
    {"name": "Metformin 500mg", "generic": "Metformin Hydrochloride", "cat": "Diabetes Care", "dosage": "Tablet", "strength": "500mg", "unit": "strips", "price": 35.00},
    {"name": "Metformin 1000mg SR", "generic": "Metformin Extended Release", "cat": "Diabetes Care", "dosage": "Tablet", "strength": "1000mg", "unit": "strips", "price": 62.00},
    {"name": "Glimepiride 2mg", "generic": "Glimepiride", "cat": "Diabetes Care", "dosage": "Tablet", "strength": "2mg", "unit": "strips", "price": 48.00},
    {"name": "Sitagliptin 100mg (Januvia)", "generic": "Sitagliptin Phosphate", "cat": "Diabetes Care", "dosage": "Tablet", "strength": "100mg", "unit": "strips", "price": 320.00},
    {"name": "Insulin Glargine 100IU", "generic": "Insulin Glargine (rDNA)", "cat": "Diabetes Care", "dosage": "Cartridge", "strength": "100IU/ml", "unit": "cartridge", "price": 640.00},

    # Blood Pressure & Heart Care
    {"name": "Amlodipine 5mg", "generic": "Amlodipine Besylate", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "5mg", "unit": "strips", "price": 28.00},
    {"name": "Telmisartan 40mg", "generic": "Telmisartan", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "40mg", "unit": "strips", "price": 75.00},
    {"name": "Telma 40", "generic": "Telmisartan", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "40mg", "unit": "strips", "price": 82.00},
    {"name": "Atenolol 50mg", "generic": "Atenolol", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "50mg", "unit": "strips", "price": 32.00},
    {"name": "Atorvastatin 20mg", "generic": "Atorvastatin Calcium", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "20mg", "unit": "strips", "price": 135.00},
    {"name": "Losartan 50mg", "generic": "Losartan Potassium", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "50mg", "unit": "strips", "price": 54.00},
    {"name": "Ecosprin 75mg", "generic": "Aspirin / Acetylsalicylic Acid", "cat": "Blood Pressure & Heart Care", "dosage": "Tablet", "strength": "75mg", "unit": "strips", "price": 12.50},

    # Gastric & Digestive Care
    {"name": "Pantoprazole 40mg (Pan 40)", "generic": "Pantoprazole Sodium", "cat": "Gastric & Digestive Care", "dosage": "Tablet", "strength": "40mg", "unit": "strips", "price": 95.00},
    {"name": "Omeprazole 20mg (Omez)", "generic": "Omeprazole", "cat": "Gastric & Digestive Care", "dosage": "Capsule", "strength": "20mg", "unit": "strips", "price": 62.00},
    {"name": "Rabeprazole 20mg", "generic": "Rabeprazole Sodium", "cat": "Gastric & Digestive Care", "dosage": "Tablet", "strength": "20mg", "unit": "strips", "price": 85.00},
    {"name": "Ranitidine 150mg (Rantac)", "generic": "Ranitidine Hydrochloride", "cat": "Gastric & Digestive Care", "dosage": "Tablet", "strength": "150mg", "unit": "strips", "price": 26.00},
    {"name": "Digene Gel 200ml", "generic": "Magnesium Hydroxide & Simethicone", "cat": "Gastric & Digestive Care", "dosage": "Syrup", "strength": "200ml", "unit": "bottle", "price": 140.00},
    {"name": "Gelusil Antacid Liquid 200ml", "generic": "Aluminium Hydroxide & Magnesium", "cat": "Gastric & Digestive Care", "dosage": "Syrup", "strength": "200ml", "unit": "bottle", "price": 128.00},

    # Cough & Cold
    {"name": "Ascoril D Plus Syrup", "generic": "Dextromethorphan, Phenylephrine, Chlorpheniramine", "cat": "Cough & Cold", "dosage": "Syrup", "strength": "100ml", "unit": "bottle", "price": 118.00},
    {"name": "Benadryl Cough Syrup", "generic": "Diphenhydramine Hydrochloride", "cat": "Cough & Cold", "dosage": "Syrup", "strength": "150ml", "unit": "bottle", "price": 132.00},
    {"name": "Solvin Cold Tablet", "generic": "Paracetamol, Phenylephrine, Chlorpheniramine", "cat": "Cough & Cold", "dosage": "Tablet", "strength": "Multi", "unit": "strips", "price": 48.00},
    {"name": "Cheston Cold Tablet", "generic": "Cetirizine, Paracetamol, Phenylephrine", "cat": "Cough & Cold", "dosage": "Tablet", "strength": "Multi", "unit": "strips", "price": 42.00},

    # Vitamins & Supplements
    {"name": "Limcee 500mg Vitamin C", "generic": "Ascorbic Acid (Vitamin C)", "cat": "Vitamins & Supplements", "dosage": "Chewable Tablet", "strength": "500mg", "unit": "strips", "price": 22.00},
    {"name": "Shelcal 500mg", "generic": "Calcium & Vitamin D3", "cat": "Vitamins & Supplements", "dosage": "Tablet", "strength": "500mg", "unit": "strips", "price": 115.00},
    {"name": "Zincovit Tablets", "generic": "Multivitamin & Minerals with Zinc", "cat": "Vitamins & Supplements", "dosage": "Tablet", "strength": "Multi", "unit": "strips", "price": 105.00},
    {"name": "Becosules Capsules", "generic": "Vitamin B-Complex & Vitamin C", "cat": "Vitamins & Supplements", "dosage": "Capsule", "strength": "Multi", "unit": "strips", "price": 48.00},
    {"name": "Neurobion Forte", "generic": "Vitamin B1, B6, B12", "cat": "Vitamins & Supplements", "dosage": "Tablet", "strength": "Multi", "unit": "strips", "price": 38.00},
    {"name": "Vitamin D3 60K Capsules", "generic": "Cholecalciferol 60000 IU", "cat": "Vitamins & Supplements", "dosage": "Capsule", "strength": "60000 IU", "unit": "strips", "price": 130.00},

    # First Aid & Antiseptic
    {"name": "Betadine 10% Ointment 20g", "generic": "Povidone Iodine 10% w/w", "cat": "First-Aid Products", "dosage": "Ointment", "strength": "10%", "unit": "tube", "price": 95.00},
    {"name": "Dettol Antiseptic Liquid 250ml", "generic": "Chloroxylenol", "cat": "First-Aid Products", "dosage": "Liquid", "strength": "250ml", "unit": "bottle", "price": 135.00},
    {"name": "Silver Sulfadiazine Cream", "generic": "Silver Sulfadiazine 1% w/w", "cat": "Skin Care", "dosage": "Ointment", "strength": "1%", "unit": "tube", "price": 68.00},
    {"name": "Band-Aid Waterproof Strips", "generic": "Adhesive Bandages", "cat": "First-Aid Products", "dosage": "Strips", "strength": "Standard", "unit": "pack", "price": 45.00},

    # Paediatric Medicines
    {"name": "Crocin Paediatric Drops", "generic": "Paracetamol Drops 100mg/ml", "cat": "Paediatric Medicines", "dosage": "Drops", "strength": "100mg/ml", "unit": "bottle", "price": 42.00},
    {"name": "Maxtra Syrup 60ml", "generic": "Phenylephrine & Chlorpheniramine", "cat": "Paediatric Medicines", "dosage": "Syrup", "strength": "60ml", "unit": "bottle", "price": 82.00},
    {"name": "Pediasure Vanilla 400g", "generic": "Complete Balanced Nutrition", "cat": "Paediatric Medicines", "dosage": "Powder", "strength": "400g", "unit": "tin", "price": 680.00}
]

HOSPITAL_DEFINITIONS = [
    # Chennai
    {"name": "Apollo Hospitals Greams Road", "city": "Chennai", "locality": "Central", "address": "21 Greams Lane, Thousand Lights", "lat": 13.0604, "lon": 80.2503},
    {"name": "Fortis Malar Hospital Adyar", "city": "Chennai", "locality": "Adyar", "address": "52 1st Main Rd, Gandhi Nagar, Adyar", "lat": 13.0076, "lon": 80.2570},
    {"name": "MIOT International Manapakkam", "city": "Chennai", "locality": "Guindy", "address": "4/112 Mount Poonamallee Rd", "lat": 13.0185, "lon": 80.1740},
    {"name": "Rajiv Gandhi Government General Hospital", "city": "Chennai", "locality": "Central", "address": "EVR Periyar Salai, Park Town", "lat": 13.0818, "lon": 80.2778},
    {"name": "Sundaram Medical Foundation Anna Nagar", "city": "Chennai", "locality": "Anna Nagar", "address": "9C 4th Ave, Shanthi Colony", "lat": 13.0845, "lon": 80.2110},

    # Coimbatore
    {"name": "G. Kuppuswamy Naidu Memorial Hospital (GKNM)", "city": "Coimbatore", "locality": "Peelamedu", "address": "P.B. No. 6327, Nethaji Road, Pappanaickenpalayam", "lat": 11.0142, "lon": 76.9785},
    {"name": "PSG Hospitals Peelamedu", "city": "Coimbatore", "locality": "Peelamedu", "address": "Avinashi Road, Peelamedu", "lat": 11.0280, "lon": 77.0090},
    {"name": "Kovai Medical Center and Hospital (KMCH)", "city": "Coimbatore", "locality": "Singanallur", "address": "99 Avinashi Road, Civil Aerodrome Post", "lat": 11.0425, "lon": 77.0430},
    {"name": "Sri Ramakrishna Hospital", "city": "Coimbatore", "locality": "Gandhipuram", "address": "395 Sarojini Naidu Rd, Sidhapudur", "lat": 11.0195, "lon": 76.9740},

    # Madurai
    {"name": "Meenakshi Mission Hospital and Research Centre", "city": "Madurai", "locality": "KK Nagar", "address": "Melur Road, Madurai", "lat": 9.9485, "lon": 78.1630},
    {"name": "Apollo Speciality Hospitals Madurai", "city": "Madurai", "locality": "KK Nagar", "address": "Lake Area, Mattuthavani", "lat": 9.9380, "lon": 78.1560},
    {"name": "Government Rajaji Hospital", "city": "Madurai", "locality": "Goripalayam", "address": "Panagal Road, Goripalayam", "lat": 9.9295, "lon": 78.1285},
    {"name": "Vadamalayan Hospitals", "city": "Madurai", "locality": "Tallakulam", "address": "9A Vallabai Road, Chokkikulam", "lat": 9.9350, "lon": 78.1380},

    # Tiruchirappalli
    {"name": "Kauvery Hospital Cantonment", "city": "Tiruchirappalli", "locality": "Cantonment", "address": "No. 1 K.C. Road, Tennur", "lat": 10.8140, "lon": 78.6860},
    {"name": "Apollo Speciality Hospitals Trichy", "city": "Tiruchirappalli", "locality": "Thillai Nagar", "address": "Old Collector Office Rd", "lat": 10.8220, "lon": 78.6890},
    {"name": "Mahatma Gandhi Memorial Govt Hospital", "city": "Tiruchirappalli", "locality": "Central", "address": "Collector Office Rd, Trichy", "lat": 10.7950, "lon": 78.6980},

    # Salem
    {"name": "Manipal Hospital Salem", "city": "Salem", "locality": "Fairlands", "address": "Dalmia Board, Bangalore Highway", "lat": 11.6840, "lon": 78.1360},
    {"name": "SKS Hospital Fairlands", "city": "Salem", "locality": "Fairlands", "address": "23 SKS Hospital Rd, Fairlands", "lat": 11.6760, "lon": 78.1480},

    # Erode
    {"name": "Lotus Hospital and Research Centre", "city": "Erode", "locality": "Brough Road", "address": "Poondurai Road, Erode", "lat": 11.3380, "lon": 77.7240},
    {"name": "Care24 Medical Center", "city": "Erode", "locality": "Perundurai Road", "address": "Perundurai Main Road, Erode", "lat": 11.3310, "lon": 77.6980},

    # Tirunelveli
    {"name": "Tirunelveli Medical College Hospital", "city": "Tirunelveli", "locality": "Palayamkottai", "address": "High Ground, Palayamkottai", "lat": 8.7180, "lon": 77.7460},
    {"name": "Shifa Hospitals", "city": "Tirunelveli", "locality": "Junction", "address": "82 Kailasapuram Middle St", "lat": 8.7260, "lon": 77.7180},

    # Vellore
    {"name": "Christian Medical College (CMC) Hospital", "city": "Vellore", "locality": "Bagayam (CMC)", "address": "Ida Scudder Road, Vellore", "lat": 12.9240, "lon": 79.1350},
    {"name": "Naruvi Hospitals Vellore", "city": "Vellore", "locality": "Sathuvachari", "address": "Collectorate Rd, Sathuvachari", "lat": 12.9380, "lon": 79.1650},

    # Bengaluru
    {"name": "Manipal Hospital Indiranagar", "city": "Bengaluru", "locality": "Indiranagar", "address": "98 HAL Old Airport Rd", "lat": 12.9585, "lon": 77.6483},
    {"name": "Apollo Hospitals Bannerghatta", "city": "Bengaluru", "locality": "Jayanagar", "address": "154/11 Bannerghatta Road", "lat": 12.8950, "lon": 77.5988},
    {"name": "Fortis Hospital Cunningham", "city": "Bengaluru", "locality": "Central / MG Road", "address": "14 Cunningham Road", "lat": 12.9882, "lon": 77.5960},
    {"name": "St. Johns Medical College Hospital", "city": "Bengaluru", "locality": "Koramangala", "address": "Sarjapur Main Road, Koramangala", "lat": 12.9322, "lon": 77.6198},
    {"name": "Narayana Health City", "city": "Bengaluru", "locality": "Electronic City", "address": "258/A Bommasandra Industrial Area", "lat": 12.8124, "lon": 77.6941},

    # Hyderabad
    {"name": "Apollo Hospitals Jubilee Hills", "city": "Hyderabad", "locality": "Jubilee Hills", "address": "Road No 72, Film Nagar", "lat": 17.4260, "lon": 78.4110},
    {"name": "Yashoda Hospitals Somajiguda", "city": "Hyderabad", "locality": "Central", "address": "Raj Bhavan Rd, Somajiguda", "lat": 17.4225, "lon": 78.4610},
    {"name": "KIMS Hospitals Secunderabad", "city": "Hyderabad", "locality": "Secunderabad", "address": "Minister Rd, Krishna Nagar", "lat": 17.4360, "lon": 78.4890},

    # Kochi & Trivandrum
    {"name": "Amrita Institute of Medical Sciences", "city": "Kochi", "locality": "Edappally", "address": "Ponekkara, Edappally", "lat": 10.0320, "lon": 76.2940},
    {"name": "Government Medical College Hospital Trivandrum", "city": "Thiruvananthapuram", "locality": "Pattom", "address": "Medical College PO, Trivandrum", "lat": 8.5280, "lon": 76.9290},

    # Mumbai & Delhi
    {"name": "Lilavati Hospital and Research Centre", "city": "Mumbai", "locality": "Bandra", "address": "A-791, Bandra Reclamation", "lat": 19.0515, "lon": 72.8290},
    {"name": "All India Institute of Medical Sciences (AIIMS)", "city": "Delhi", "locality": "South Extension", "address": "Ansari Nagar East, New Delhi", "lat": 28.5672, "lon": 77.2100}
]

PHARMACY_DEFINITIONS = [
    # Chennai
    {"name": "Apollo Pharmacy Anna Nagar", "city": "Chennai", "locality": "Anna Nagar", "address": "2nd Ave, Near Roundtana, Anna Nagar", "lat": 13.0860, "lon": 80.2120},
    {"name": "MedPlus T. Nagar", "city": "Chennai", "locality": "T. Nagar", "address": "45 Usman Road, T. Nagar", "lat": 13.0420, "lon": 80.2330},
    {"name": "Wellness Forever Adyar", "city": "Chennai", "locality": "Adyar", "address": "Sardar Patel Road, Adyar", "lat": 13.0030, "lon": 80.2550},
    {"name": "Netmeds Store Velachery", "city": "Chennai", "locality": "Velachery", "address": "100 Feet Bypass Rd, Velachery", "lat": 12.9820, "lon": 80.2190},
    {"name": "Apollo Pharmacy Mylapore", "city": "Chennai", "locality": "Mylapore", "address": "Luz Church Road, Mylapore", "lat": 13.0380, "lon": 80.2660},
    {"name": "MedPlus Tambaram", "city": "Chennai", "locality": "Tambaram", "address": "GST Road, Tambaram Sanatorium", "lat": 12.9260, "lon": 80.1040},

    # Coimbatore
    {"name": "Apollo Pharmacy Gandhipuram", "city": "Coimbatore", "locality": "Gandhipuram", "address": "Cross Cut Road, Gandhipuram", "lat": 11.0190, "lon": 76.9650},
    {"name": "MedPlus RS Puram", "city": "Coimbatore", "locality": "RS Puram", "address": "DB Road, RS Puram", "lat": 11.0095, "lon": 76.9495},
    {"name": "Aster Pharmacy Peelamedu", "city": "Coimbatore", "locality": "Peelamedu", "address": "Avinashi Road, Peelamedu", "lat": 11.0270, "lon": 77.0110},
    {"name": "Wellness Forever Saravanampatti", "city": "Coimbatore", "locality": "Saravanampatti", "address": "Sathy Road, Saravanampatti", "lat": 11.0810, "lon": 77.0010},

    # Madurai
    {"name": "Apollo Pharmacy KK Nagar", "city": "Madurai", "locality": "KK Nagar", "address": "80 Feet Road, KK Nagar", "lat": 9.9340, "lon": 78.1520},
    {"name": "MedPlus Anna Nagar", "city": "Madurai", "locality": "Anna Nagar", "address": "Kuruvikaran Salai, Anna Nagar", "lat": 9.9220, "lon": 78.1475},
    {"name": "Thulasi Pharmacies Simmakkal", "city": "Madurai", "locality": "Simmakkal", "address": "North Veli St, Simmakkal", "lat": 9.9290, "lon": 78.1220},

    # Trichy
    {"name": "Apollo Pharmacy Thillai Nagar", "city": "Tiruchirappalli", "locality": "Thillai Nagar", "address": "Main Road, Thillai Nagar", "lat": 10.8250, "lon": 78.6880},
    {"name": "MedPlus Cantonment", "city": "Tiruchirappalli", "locality": "Cantonment", "address": "McDonalds Road, Cantonment", "lat": 10.8040, "lon": 78.6860},
    {"name": "Apollo Pharmacy Srirangam", "city": "Tiruchirappalli", "locality": "Srirangam", "address": "Gandhi Road, Srirangam", "lat": 10.8630, "lon": 78.6950},

    # Salem & Erode
    {"name": "Apollo Pharmacy Fairlands", "city": "Salem", "locality": "Fairlands", "address": "Brindavan Road, Fairlands", "lat": 11.6790, "lon": 78.1460},
    {"name": "MedPlus Hasthampatti", "city": "Salem", "locality": "Hasthampatti", "address": "Yercaud Main Road, Hasthampatti", "lat": 11.6820, "lon": 78.1630},
    {"name": "Apollo Pharmacy Brough Road", "city": "Erode", "locality": "Brough Road", "address": "Brough Road, Erode", "lat": 11.3470, "lon": 77.7220},
    {"name": "MedPlus Perundurai Road", "city": "Erode", "locality": "Perundurai Road", "address": "Opp. Collector Office, Perundurai Rd", "lat": 11.3330, "lon": 77.6960},

    # Tirunelveli & Vellore
    {"name": "Apollo Pharmacy Palayamkottai", "city": "Tirunelveli", "locality": "Palayamkottai", "address": "Tiruchendur Rd, Palayamkottai", "lat": 8.7160, "lon": 77.7430},
    {"name": "MedPlus Tirunelveli Junction", "city": "Tirunelveli", "locality": "Junction", "address": "SN High Rd, Junction", "lat": 8.7290, "lon": 77.7130},
    {"name": "Apollo Pharmacy Katpadi", "city": "Vellore", "locality": "Katpadi", "address": "Chittoor Bus Stand Rd, Katpadi", "lat": 12.9820, "lon": 79.1380},
    {"name": "MedPlus Sathuvachari", "city": "Vellore", "locality": "Sathuvachari", "address": "Phase 2, Sathuvachari", "lat": 12.9360, "lon": 79.1630},

    # Bengaluru
    {"name": "Apollo Pharmacy Koramangala", "city": "Bengaluru", "locality": "Koramangala", "address": "12 Koramangala 5th Block", "lat": 12.9350, "lon": 77.6150},
    {"name": "MedPlus Indiranagar", "city": "Bengaluru", "locality": "Indiranagar", "address": "412 100ft Road Indiranagar", "lat": 12.9740, "lon": 77.6400},
    {"name": "Wellness Forever Jayanagar", "city": "Bengaluru", "locality": "Jayanagar", "address": "88 11th Main Jayanagar", "lat": 12.9280, "lon": 77.5890},
    {"name": "Aster Pharmacy Whitefield", "city": "Bengaluru", "locality": "Whitefield", "address": "ITPL Main Road Whitefield", "lat": 12.9850, "lon": 77.7310},
    {"name": "Frank Ross Pharmacy HSR", "city": "Bengaluru", "locality": "HSR Layout", "address": "Sector 1 HSR Layout", "lat": 12.9150, "lon": 77.6510},
    {"name": "Apollo Pharmacy Malleshwaram", "city": "Bengaluru", "locality": "Malleshwaram", "address": "Margosa Road, Malleshwaram", "lat": 12.9990, "lon": 77.5710},

    # Hyderabad
    {"name": "Apollo Pharmacy Banjara Hills", "city": "Hyderabad", "locality": "Banjara Hills", "address": "Road No 2, Banjara Hills", "lat": 17.4160, "lon": 78.4360},
    {"name": "MedPlus Jubilee Hills", "city": "Hyderabad", "locality": "Jubilee Hills", "address": "Road No 36, Jubilee Hills", "lat": 17.4325, "lon": 78.4080},
    {"name": "Wellness Forever Gachibowli", "city": "Hyderabad", "locality": "Gachibowli", "address": "Old Mumbai Highway, Gachibowli", "lat": 17.4410, "lon": 78.3495},
    {"name": "Apollo Pharmacy Hitec City", "city": "Hyderabad", "locality": "Madhapur / Hitec City", "address": "Cyber Towers Rd, Madhapur", "lat": 17.4490, "lon": 78.3920},

    # Kochi, Trivandrum, Mumbai, Pune, Delhi
    {"name": "Apollo Pharmacy Edappally", "city": "Kochi", "locality": "Edappally", "address": "Toll Junction, Edappally", "lat": 10.0240, "lon": 76.3120},
    {"name": "Neethi Medical Store Kowdiar", "city": "Thiruvananthapuram", "locality": "Kowdiar", "address": "Kowdiar Junction, Trivandrum", "lat": 8.5290, "lon": 76.9610},
    {"name": "Wellness Forever Bandra", "city": "Mumbai", "locality": "Bandra", "address": "Hill Road, Bandra West", "lat": 19.0580, "lon": 72.8310},
    {"name": "Apollo Pharmacy Kothrud", "city": "Pune", "locality": "Kothrud", "address": "Paud Road, Kothrud", "lat": 18.5080, "lon": 73.8090},
    {"name": "Apollo Pharmacy South Extension", "city": "Delhi", "locality": "South Extension", "address": "South Extension Part 1", "lat": 28.5720, "lon": 77.2220},
    {"name": "MedPlus Connaught Place", "city": "Delhi", "locality": "Central / CP", "address": "Barakhamba Road, Connaught Place", "lat": 28.6310, "lon": 77.2190}
]

def generate_all_seed_data():
    db = SessionLocal()
    print("Beginning LifeLink Expanded Dataset Generation...")

    # Ensure admin user exists
    admin = db.query(User).filter(User.email == "admin@lifelink.org").first()
    if not admin:
        admin = User(
            full_name="LifeLink Master Admin",
            email="admin@lifelink.org",
            phone="+91 9876543210",
            password_hash=PASSWORD_HASH,
            role="admin",
            address="Central Healthcare Command",
            city="Bengaluru",
            latitude=12.9716,
            longitude=77.5946,
            is_active=True
        )
        db.add(admin)
        db.flush()

    # Ensure test patients exist
    patients_data = [
        ("Aarav Sharma", "patient1@example.com", "+91 9812345670", "Indiranagar", "Bengaluru", 12.9784, 77.6408),
        ("Priya Patel", "patient2@example.com", "+91 9812345671", "Anna Nagar", "Chennai", 13.0850, 80.2100),
        ("Karthikeyan S", "patient3@example.com", "+91 9812345672", "Gandhipuram", "Coimbatore", 11.0183, 76.9644),
        ("Meenakshi Sundaram", "patient4@example.com", "+91 9812345673", "KK Nagar", "Madurai", 9.9328, 78.1511),
    ]
    created_patients = []
    for full_name, email, phone, addr, city, lat, lon in patients_data:
        p = db.query(User).filter(User.email == email).first()
        if not p:
            p = User(
                full_name=full_name,
                email=email,
                phone=phone,
                password_hash=PASSWORD_HASH,
                role="patient",
                address=addr,
                city=city,
                latitude=lat,
                longitude=lon,
                is_active=True
            )
            db.add(p)
            db.flush()
        created_patients.append(p)

    # 1. GENERATE HOSPITALS
    print(f"Creating/updating {len(HOSPITAL_DEFINITIONS)} hospitals across cities...")
    hospital_objs = []
    for i, h_def in enumerate(HOSPITAL_DEFINITIONS, start=1):
        email = f"hospital{i}@{h_def['city'].lower().replace(' ', '')}.lifelink.org"
        h_user = db.query(User).filter(User.email == email).first()
        if not h_user:
            h_user = User(
                full_name=h_def["name"],
                email=email,
                phone=f"+91 44{20000000 + i}",
                password_hash=PASSWORD_HASH,
                role="hospital",
                address=h_def["address"],
                city=h_def["city"],
                latitude=h_def["lat"],
                longitude=h_def["lon"],
                is_active=True
            )
            db.add(h_user)
            db.flush()

        hospital = db.query(Hospital).filter(Hospital.user_id == h_user.id).first()
        if not hospital:
            hospital = Hospital(
                user_id=h_user.id,
                hospital_name=h_def["name"],
                registration_number=f"REG-HOSP-{1000 + i}",
                phone=h_user.phone,
                address=h_def["address"],
                city=h_def["city"],
                latitude=h_def["lat"],
                longitude=h_def["lon"],
                verified=True
            )
            db.add(hospital)
            db.flush()
        hospital_objs.append(hospital)

        # Populate Blood Stock for each blood group for this hospital
        for bg in BLOOD_GROUPS:
            bs = db.query(BloodStock).filter(
                BloodStock.hospital_id == hospital.id,
                BloodStock.blood_group == bg
            ).first()
            if not bs:
                # Distribution of units: majority in_stock, some low stock, few 0
                r_val = random.random()
                if r_val < 0.12:
                    units = 0
                elif r_val < 0.35:
                    units = random.randint(2, 5)
                else:
                    units = random.randint(12, 45)
                bs = BloodStock(
                    hospital_id=hospital.id,
                    blood_group=bg,
                    units_available=units,
                    low_stock_threshold=5
                )
                db.add(bs)
    db.commit()

    # 2. GENERATE PHARMACIES
    print(f"Creating/updating {len(PHARMACY_DEFINITIONS)} pharmacies across cities...")
    pharmacy_objs = []
    for i, p_def in enumerate(PHARMACY_DEFINITIONS, start=1):
        email = f"pharmacy{i}@{p_def['city'].lower().replace(' ', '')}.lifelink.org"
        p_user = db.query(User).filter(User.email == email).first()
        if not p_user:
            p_user = User(
                full_name=p_def["name"],
                email=email,
                phone=f"+91 44{30000000 + i}",
                password_hash=PASSWORD_HASH,
                role="pharmacy",
                address=p_def["address"],
                city=p_def["city"],
                latitude=p_def["lat"],
                longitude=p_def["lon"],
                is_active=True
            )
            db.add(p_user)
            db.flush()

        pharmacy = db.query(Pharmacy).filter(Pharmacy.user_id == p_user.id).first()
        if not pharmacy:
            pharmacy = Pharmacy(
                user_id=p_user.id,
                pharmacy_name=p_def["name"],
                phone=p_user.phone,
                address=p_def["address"],
                city=p_def["city"],
                latitude=p_def["lat"],
                longitude=p_def["lon"],
                opening_time="08:00" if i % 4 != 0 else "00:00",
                closing_time="22:30" if i % 4 != 0 else "23:59",
                verified=True
            )
            db.add(pharmacy)
            db.flush()
        pharmacy_objs.append(pharmacy)
    db.commit()

    # 3. GENERATE MEDICINE INVENTORY RECORDS (Target: 450+ records)
    print("Creating/updating medicine inventory across pharmacies...")
    med_count = 0
    for pharmacy in pharmacy_objs:
        # Each pharmacy stocks 10 to 18 distinct medicines from catalog
        # Core essentials like Paracetamol, Amoxicillin, Cetirizine, Metformin, Pantoprazole are in nearly every pharmacy!
        core_meds = MEDICINE_CATALOG[:12]
        other_meds = random.sample(MEDICINE_CATALOG[12:], k=min(len(MEDICINE_CATALOG) - 12, random.randint(6, 12)))
        pharm_catalog = core_meds + other_meds

        for med_item in pharm_catalog:
            existing_med = db.query(Medicine).filter(
                Medicine.pharmacy_id == pharmacy.id,
                Medicine.medicine_name == med_item["name"]
            ).first()

            if not existing_med:
                # Random realistic quantity and status
                q_rand = random.random()
                if q_rand < 0.10:
                    qty = 0
                    status_str = "out_of_stock"
                elif q_rand < 0.25:
                    qty = random.randint(4, 14)
                    status_str = "low_stock"
                else:
                    qty = random.randint(35, 250)
                    status_str = "in_stock"

                # Small price variance between pharmacies (+/- 5%)
                price_adj = round(med_item["price"] * random.uniform(0.95, 1.05), 2)

                new_med = Medicine(
                    pharmacy_id=pharmacy.id,
                    medicine_name=med_item["name"],
                    generic_name=med_item["generic"],
                    category=med_item["cat"],
                    dosage_form=med_item["dosage"],
                    strength=med_item["strength"],
                    quantity=qty,
                    unit=med_item["unit"],
                    price=price_adj,
                    availability_status=status_str
                )
                db.add(new_med)
                med_count += 1
    db.commit()
    print(f"Added {med_count} new medicine records. Total in DB: {db.query(Medicine).count()}")

    # 4. GENERATE 550 SYNTHETIC DONORS
    print("Creating/updating 550 synthetic donors across all cities and blood groups...")
    # Target allocations per city to reach 550
    city_donor_targets = {
        "Chennai": 75,
        "Coimbatore": 55,
        "Madurai": 45,
        "Tiruchirappalli": 35,
        "Salem": 30,
        "Erode": 25,
        "Tirunelveli": 20,
        "Vellore": 25,
        "Bengaluru": 70,
        "Hyderabad": 50,
        "Kochi": 30,
        "Thiruvananthapuram": 25,
        "Mumbai": 30,
        "Pune": 25,
        "Delhi": 30
    }

    donor_idx = 1
    created_donors = []

    for city_name, target_count in city_donor_targets.items():
        city_data = SUPPORTED_LOCATIONS[city_name]
        localities_list = list(city_data["localities"].items())

        for c_idx in range(target_count):
            loc_name, loc_coords = localities_list[c_idx % len(localities_list)]

            email = f"donor.{city_name.lower().replace(' ', '')}{c_idx + 1}@example.com"
            f_name = random.choice(FIRST_NAMES)
            l_name = random.choice(LAST_NAMES)
            full_name = f"{f_name} {l_name}"

            # Plausible coordinates with slight jitter (+/- 0.003 deg approx 300m)
            jitter_lat = round(loc_coords["lat"] + random.uniform(-0.0035, 0.0035), 6)
            jitter_lon = round(loc_coords["lon"] + random.uniform(-0.0035, 0.0035), 6)

            # Blood group assignment ensuring uniform distribution
            bg = BLOOD_GROUPS[donor_idx % len(BLOOD_GROUPS)]

            # Check if user already exists
            d_user = db.query(User).filter(User.email == email).first()
            if not d_user:
                d_user = User(
                    full_name=full_name,
                    email=email,
                    phone=f"+91 9{random.randint(100000000, 999999999)}",
                    password_hash=PASSWORD_HASH,
                    role="donor",
                    address=f"{loc_name}, {city_name}",
                    city=city_name,
                    latitude=jitter_lat,
                    longitude=jitter_lon,
                    is_active=True
                )
                db.add(d_user)
                db.flush()

            donor = db.query(Donor).filter(Donor.user_id == d_user.id).first()
            if not donor:
                # Realistic DOB (1970 - 2005)
                dob = date(random.randint(1972, 2004), random.randint(1, 12), random.randint(1, 28))
                
                # Availability: 76% available, 17% unavailable, 7% busy
                av_r = random.random()
                if av_r < 0.76:
                    av_status = "available"
                elif av_r < 0.93:
                    av_status = "unavailable"
                else:
                    av_status = "busy"

                # Last donation date
                months_ago = random.randint(1, 24)
                last_don = date.today() - timedelta(days=months_ago * 30 + random.randint(1, 25))

                donor = Donor(
                    user_id=d_user.id,
                    blood_group=bg,
                    date_of_birth=dob,
                    last_donation_date=last_don,
                    availability_status=av_status,
                    latitude=jitter_lat,
                    longitude=jitter_lon,
                    city=city_name,
                    locality=loc_name,
                    response_rate=round(random.uniform(70.0, 100.0), 1),
                    total_donations=0, # Will be calculated strictly from completed donations
                    verified=(random.random() > 0.08)
                )
                db.add(donor)
                db.flush()

            created_donors.append(donor)
            donor_idx += 1

    db.commit()
    print(f"Total Donors in DB: {db.query(Donor).count()}")

    # 5. GENERATE 280 DONATION HISTORY RECORDS (Synchronized with donor donation count)
    print("Generating 280 donation history records with status distribution...")
    all_donors = db.query(Donor).all()
    all_hospitals = db.query(Hospital).all()

    # First clean existing donation history to ensure 100% data consistency
    db.query(DonationHistory).delete()
    db.commit()

    don_types = ["Whole Blood", "Platelets", "Plasma", "Red Blood Cells"]
    total_donations_created = 0

    # Distribute 280 donations among donors
    # Some donors have 3-8 completed donations, some 1-2, some 0
    selected_donors_for_donations = all_donors[:220]

    for d in selected_donors_for_donations:
        # Determine number of donations for this donor (1 to 4)
        num_donations = 1 if d.id % 3 == 0 else (2 if d.id % 5 == 0 else 1)
        if total_donations_created >= 280:
            break

        for rec_num in range(num_donations):
            if total_donations_created >= 280:
                break

            # Find a hospital in the same city or closest hospital
            city_hospitals = [h for h in all_hospitals if h.city == d.city]
            target_hosp = random.choice(city_hospitals) if city_hospitals else random.choice(all_hospitals)

            # Status distribution: 75% completed, 15% scheduled, 10% cancelled
            st_rand = random.random()
            if st_rand < 0.75:
                don_status = "completed"
                don_date = date.today() - timedelta(days=random.randint(20, 720))
                notes = random.choice([
                    "Voluntary blood camp donation",
                    "Emergency hospital patient requirement",
                    "Regular platelet apheresis donation",
                    "Replacement donation for surgery patient",
                    "World Blood Donor Day camp"
                ])
            elif st_rand < 0.90:
                don_status = "scheduled"
                don_date = date.today() + timedelta(days=random.randint(2, 28))
                notes = "Scheduled appointment at hospital blood bank"
            else:
                don_status = "cancelled"
                don_date = date.today() - timedelta(days=random.randint(5, 120))
                notes = "Cancelled due to temporary low hemoglobin / fever"

            don_rec = DonationHistory(
                donor_id=d.id,
                hospital_id=target_hosp.id,
                donation_date=don_date,
                blood_group=d.blood_group,
                units=1 if d.blood_group not in ["O+", "A+"] else random.choice([1, 2]),
                status=don_status,
                donation_type=random.choice(don_types) if don_status == "completed" else "Whole Blood",
                notes=notes
            )
            db.add(don_rec)
            total_donations_created += 1

    db.commit()

    # Now update every donor's total_donations to match their actual completed records!
    print("Synchronizing donor total_donations count with completed donation records...")
    for d in all_donors:
        completed_count = db.query(DonationHistory).filter(
            DonationHistory.donor_id == d.id,
            DonationHistory.status == "completed"
        ).count()
        d.total_donations = completed_count

    db.commit()
    print(f"Created {total_donations_created} donation history records.")

    # 6. GENERATE EMERGENCY REQUESTS & MATCHES
    print("Generating emergency requests across multiple cities...")
    if db.query(BloodRequest).count() < 15:
        emergency_specs = [
            ("Chennai", "O-", 2, "critical", "Apollo Hospitals Greams Road", 13.0604, 80.2503),
            ("Chennai", "B+", 3, "urgent", "MIOT International Manapakkam", 13.0185, 80.1740),
            ("Coimbatore", "A+", 2, "critical", "PSG Hospitals Peelamedu", 11.0280, 77.0090),
            ("Coimbatore", "AB-", 1, "urgent", "G. Kuppuswamy Naidu Memorial Hospital (GKNM)", 11.0142, 76.9785),
            ("Madurai", "O+", 3, "critical", "Meenakshi Mission Hospital and Research Centre", 9.9485, 78.1630),
            ("Madurai", "A-", 2, "normal", "Apollo Speciality Hospitals Madurai", 9.9380, 78.1560),
            ("Tiruchirappalli", "B-", 1, "critical", "Kauvery Hospital Cantonment", 10.8140, 78.6860),
            ("Salem", "O+", 2, "urgent", "Manipal Hospital Salem", 11.6840, 78.1360),
            ("Bengaluru", "O+", 2, "critical", "Manipal Hospital Indiranagar", 12.9585, 77.6483),
            ("Bengaluru", "A+", 3, "urgent", "St. Johns Medical College Hospital", 12.9322, 77.6198),
            ("Hyderabad", "B+", 2, "critical", "Apollo Hospitals Jubilee Hills", 17.4260, 78.4110),
            ("Kochi", "AB+", 1, "normal", "Amrita Institute of Medical Sciences", 10.0320, 76.2940)
        ]

        patient_user = created_patients[0]
        for city, bg, units, prio, hosp_name, lat, lon in emergency_specs:
            hosp = db.query(Hospital).filter(Hospital.hospital_name == hosp_name).first()
            hosp_id = hosp.id if hosp else None

            breq = BloodRequest(
                requester_id=patient_user.id,
                hospital_id=hosp_id,
                blood_group=bg,
                units_required=units,
                priority=prio,
                required_by=datetime.utcnow() + timedelta(hours=random.randint(4, 48)),
                latitude=lat,
                longitude=lon,
                hospital_name=hosp_name,
                additional_notes=f"Emergency blood needed for surgical patient in {city}.",
                status="searching"
            )
            db.add(breq)
            db.flush()

            # Find matching donors within 35 km
            matching_donors = db.query(Donor).filter(
                Donor.blood_group == bg,
                Donor.availability_status == "available"
            ).all()

            ranked = []
            for d in matching_donors:
                dist = calculate_haversine_distance(lat, lon, d.latitude, d.longitude)
                if dist <= 40.0:
                    score = 90 - int(dist * 1.2) + (10 if d.response_rate >= 90 else 5)
                    score = min(98, max(50, score))
                    ranked.append((d, dist, score))

            ranked.sort(key=lambda x: x[1]) # sort by distance
            for d_match, dist_km, m_score in ranked[:5]:
                est_m = estimate_travel_time_minutes(dist_km)
                reasons_list = [
                    f"Exact blood group match ({bg})",
                    f"Located {dist_km} km away in {d_match.locality or d_match.city}",
                    f"Available status confirmed",
                    f"High response rate ({d_match.response_rate}%)"
                ]
                dm = DonorMatch(
                    request_id=breq.id,
                    donor_id=d_match.id,
                    match_score=m_score,
                    distance_km=dist_km,
                    estimated_minutes=est_m,
                    match_reasons=json.dumps(reasons_list),
                    status="notified"
                )
                db.add(dm)
        db.commit()

    print("=================================================================")
    print("LifeLink Database Summary:")
    print(f"- Total Users:            {db.query(User).count()}")
    print(f"- Total Donors:           {db.query(Donor).count()} (All 8 blood groups)")
    print(f"- Total Hospitals:        {db.query(Hospital).count()} (15 cities)")
    print(f"- Total Blood Stock Rows: {db.query(BloodStock).count()}")
    print(f"- Total Pharmacies:       {db.query(Pharmacy).count()} (15 cities)")
    print(f"- Total Medicines:        {db.query(Medicine).count()}")
    print(f"- Total Blood Requests:   {db.query(BloodRequest).count()}")
    print(f"- Total Donor Matches:    {db.query(DonorMatch).count()}")
    print(f"- Total Donation History: {db.query(DonationHistory).count()}")
    print("=================================================================")
    db.close()

if __name__ == "__main__":
    generate_all_seed_data()
