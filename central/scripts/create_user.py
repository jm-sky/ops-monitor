#!/usr/bin/env python3
"""
Script to create a new user in the ops-monitor system.

Usage:
    python scripts/create_user.py --email user@example.com --name "John Doe" --password SecurePass123

For interactive mode (prompts for password):
    python scripts/create_user.py --email user@example.com --name "John Doe"
"""

import argparse
import getpass
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.modules.auth.models import user_repository
from app.modules.auth.exceptions import UserAlreadyExistsError


def create_user(email: str, name: str, password: str) -> None:
    """Create a new user."""
    try:
        user = user_repository.create_user(email=email, password=password, full_name=name)
        print(f"\n✅ User created successfully!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
        print(f"   Created: {user.createdAt}")

    except UserAlreadyExistsError:
        print(f"\n❌ Error: User with email '{email}' already exists!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        sys.exit(1)


def validate_email(email: str) -> bool:
    """Basic email validation."""
    return "@" in email and "." in email.split("@")[1]


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        print("❌ Password must be at least 8 characters long")
        return False

    if not any(c.isupper() for c in password):
        print("❌ Password must contain at least one uppercase letter")
        return False

    if not any(c.islower() for c in password):
        print("❌ Password must contain at least one lowercase letter")
        return False

    if not any(c.isdigit() for c in password):
        print("❌ Password must contain at least one digit")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Create a new user in ops-monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for password)
  python scripts/create_user.py --email admin@example.com --name "Admin User"

  # Non-interactive mode (provide password via argument)
  python scripts/create_user.py --email admin@example.com --name "Admin User" --password MySecurePass123

  # Create test user quickly
  python scripts/create_user.py -e test@example.com -n "Test User" -p Test123!@#
        """
    )

    parser.add_argument(
        "-e", "--email",
        required=True,
        help="User email address"
    )

    parser.add_argument(
        "-n", "--name",
        required=True,
        help="User full name"
    )

    parser.add_argument(
        "-p", "--password",
        required=False,
        help="User password (if not provided, will prompt securely)"
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip password validation (not recommended)"
    )

    args = parser.parse_args()

    # Validate email
    if not validate_email(args.email):
        print(f"❌ Error: Invalid email address '{args.email}'")
        sys.exit(1)

    # Get password
    if args.password:
        password = args.password
    else:
        print("\nPassword requirements:")
        print("  - At least 8 characters")
        print("  - At least one uppercase letter")
        print("  - At least one lowercase letter")
        print("  - At least one digit")
        print()

        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("\n❌ Error: Passwords do not match!")
            sys.exit(1)

    # Validate password
    if not args.skip_validation:
        if not validate_password(password):
            sys.exit(1)

    # Create user
    print(f"\nCreating user...")
    print(f"  Email: {args.email}")
    print(f"  Name: {args.name}")

    create_user(email=args.email, name=args.name, password=password)


if __name__ == "__main__":
    main()
