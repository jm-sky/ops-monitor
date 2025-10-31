# User Management Scripts

Scripts for managing users in ops-monitor Central application.

## Prerequisites

Make sure you're in the `central/` directory and have activated the virtual environment:

```bash
cd central/
source ../.venv/bin/activate  # Linux/Mac
# or
..\.venv\Scripts\activate  # Windows
```

## Available Scripts

### 1. `create_user.py` - Simple User Creation

Simple script to create a single user.

**Usage:**

```bash
# Interactive mode (prompts for password)
python scripts/create_user.py --email admin@example.com --name "Admin User"

# Non-interactive mode
python scripts/create_user.py --email admin@example.com --name "Admin User" --password MySecurePass123

# Short form
python scripts/create_user.py -e test@example.com -n "Test User" -p Test123!@#
```

**Password Requirements:**
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Options:**
- `-e, --email` - User email (required)
- `-n, --name` - User full name (required)
- `-p, --password` - User password (optional, will prompt if not provided)
- `--skip-validation` - Skip password validation (not recommended)

### 2. `manage_users.py` - Full User Management CLI

More advanced script with multiple commands for user management.

**Commands:**

#### Create User

```bash
# Interactive
python scripts/manage_users.py create

# With arguments
python scripts/manage_users.py create --email admin@example.com --name "Admin" --password Pass123
```

#### List All Users

```bash
python scripts/manage_users.py list
```

Output example:
```
ID                                       Email                          Name                      Active   Created
----------------------------------------------------------------------------------------------------------------------------------
01JBQR8X9Y0Z1M2N3P4Q5R6S7T               admin@example.com              Admin User                ✓        2024-10-31 10:30
01JBQR9A1B2C3D4E5F6G7H8I9J               test@example.com               Test User                 ✓        2024-10-31 10:45

Total: 2 user(s)
```

#### Show User Details

```bash
python scripts/manage_users.py show admin@example.com
```

Output example:
```
📋 User Details:
   ID: 01JBQR8X9Y0Z1M2N3P4Q5R6S7T
   Email: admin@example.com
   Name: Admin User
   Active: Yes
   Created: 2024-10-31 10:30:00
   Has Reset Token: No
```

#### Change Password

```bash
# Interactive
python scripts/manage_users.py change-password admin@example.com

# With password argument
python scripts/manage_users.py change-password admin@example.com --password NewPass123
```

## Quick Examples

### Create Admin User

```bash
python scripts/create_user.py \
  --email admin@ops-monitor.com \
  --name "System Administrator" \
  --password AdminSecure123!
```

### Create Test User for Development

```bash
python scripts/create_user.py \
  -e test@example.com \
  -n "Test User" \
  -p Test123!@#
```

### Create Multiple Users

```bash
# Create admin
python scripts/manage_users.py create -e admin@example.com -n "Admin" -p Admin123

# Create developer
python scripts/manage_users.py create -e dev@example.com -n "Developer" -p Dev123

# Create viewer
python scripts/manage_users.py create -e viewer@example.com -n "Viewer" -p View123

# List all users
python scripts/manage_users.py list
```

## Using with Docker

If running the application in Docker, you can execute the scripts inside the container:

```bash
# Enter the container
docker-compose exec central bash

# Run the script inside container
cd /app
python scripts/create_user.py -e admin@example.com -n "Admin" -p Admin123
```

Or run directly without entering:

```bash
docker-compose exec central python scripts/create_user.py \
  -e admin@example.com \
  -n "Admin User" \
  -p Admin123
```

## Important Notes

⚠️ **Security Warnings:**

1. **In-Memory Storage**: Currently users are stored in-memory and will be lost on restart
2. **Production Use**: Replace `UserStore` with a proper database (PostgreSQL) in production
3. **Password in CLI**: Avoid passing passwords via command line arguments in production (use interactive mode)
4. **Environment Variables**: Never store passwords in environment variables or config files

## Migration to Database

When you migrate to a database-backed user store, these scripts will continue to work with minimal changes. Just ensure your `UserStore` implementation maintains the same interface:

- `create_user(email, password, full_name)`
- `get_user_by_email(email)`
- `get_all_users()`
- `update_user(user)`

## Troubleshooting

### ModuleNotFoundError

If you get import errors, make sure you're running the script from the `central/` directory:

```bash
cd /home/madeyskij/projects/private/ops-monitor/central
python scripts/create_user.py --help
```

### User Already Exists

If you get "User already exists" error, either:
1. Use a different email
2. List existing users with `python scripts/manage_users.py list`
3. Restart the application to clear in-memory storage (development only!)

### Permission Denied

Make sure scripts are executable:

```bash
chmod +x scripts/*.py
```

## Development User Seeding

For development, you can also enable automatic user seeding by setting environment variables:

```bash
# In .env file
ENVIRONMENT=development
SEED_DEVELOPMENT_USER=true
```

This will create a test user:
- Email: `test@example.com`
- Password: `Test123!@#`

⚠️ **NEVER enable this in production!**
