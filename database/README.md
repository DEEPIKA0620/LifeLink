# LifeLink Database Setup Guide

This directory contains the database migration and seeding scripts for the LifeLink Emergency Blood & Medicine Locator System.

## Database Files

- `schema.sql`: DDL script defining normalized tables, primary keys, foreign keys, unique constraints, and indexes.
- `seed.sql`: Seed data containing fictional demo users, donors, hospitals, pharmacies, medicines, blood stock, requests, and notifications.

## Database Setup

### Option 1: MySQL (Production / Standard Setup)

1. Connect to your MySQL server:
   ```bash
   mysql -u root -p
   ```
2. Run schema and seed scripts:
   ```sql
   SOURCE schema.sql;
   SOURCE seed.sql;
   ```
3. Update `backend/.env` with your MySQL credentials:
   ```env
   DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/lifelink_db
   ```

### Option 2: Automatic SQLite Fallback (Local Testing Mode)

If MySQL is not installed or configured, the FastAPI backend automatically falls back to an embedded SQLite database (`lifelink.db`) and seeds it automatically upon first startup!

## Pre-populated Seed Accounts

Default Password for all accounts: `Password123!`

- **Admin**: `admin@lifelink.org`
- **Patient**: `patient1@example.com`
- **Donor (O+)**: `ravi.kumar@example.com`
- **Hospital**: `manipal@lifelink.org`
- **Pharmacy**: `apollopharm1@lifelink.org`
