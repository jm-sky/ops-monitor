#!/usr/bin/env python3
"""
User management CLI for ops-monitor.

Usage:
    # Create user (interactive)
    python scripts/manage_users.py create

    # Create user (non-interactive)
    python scripts/manage_users.py create --email admin@example.com --name "Admin" --password Pass123

    # List all users
    python scripts/manage_users.py list

    # Show user details
    python scripts/manage_users.py show admin@example.com

    # Change password
    python scripts/manage_users.py change-password admin@example.com
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import getpass

from app.modules.auth.models import user_repository
from app.modules.auth.exceptions import UserAlreadyExistsError


def create_user_command(args):
    """Create a new user."""
    email = args.email or input("Email: ").strip()
    name = args.name or input("Name: ").strip()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("❌ Passwords do not match!")
            return

    try:
        user = user_repository.create_user(email=email, password=password, full_name=name)
        print(f"\n✅ User created successfully!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
    except UserAlreadyExistsError:
        print(f"❌ User with email '{email}' already exists!")
    except Exception as e:
        print(f"❌ Error: {e}")


def list_users_command(args):
    """List all users."""
    users = user_repository.get_all_users()

    if not users:
        print("No users found.")
        return

    print(f"\n{'ID':<40} {'Email':<30} {'Name':<25} {'Active':<8} {'Created'}")
    print("-" * 130)

    for user in users:
        active = "✓" if user.isActive else "✗"
        created = user.createdAt.strftime("%Y-%m-%d %H:%M")
        print(f"{user.id:<40} {user.email:<30} {user.name:<25} {active:<8} {created}")

    print(f"\nTotal: {len(users)} user(s)")


def show_user_command(args):
    """Show user details."""
    user = user_repository.get_user_by_email(args.email)

    if not user:
        print(f"❌ User with email '{args.email}' not found!")
        return

    print("\n📋 User Details:")
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Name: {user.name}")
    print(f"   Active: {'Yes' if user.isActive else 'No'}")
    print(f"   Created: {user.createdAt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Has Reset Token: {'Yes' if user.resetToken else 'No'}")


def change_password_command(args):
    """Change user password."""
    user = user_repository.get_user_by_email(args.email)

    if not user:
        print(f"❌ User with email '{args.email}' not found!")
        return

    if args.password:
        new_password = args.password
    else:
        new_password = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")
        if new_password != confirm:
            print("❌ Passwords do not match!")
            return

    user.set_password(new_password)
    user_repository.update_user(user)
    print(f"✅ Password changed successfully for {user.email}")


def main():
    parser = argparse.ArgumentParser(
        description="User management CLI for ops-monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create user command
    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("-e", "--email", help="User email")
    create_parser.add_argument("-n", "--name", help="User full name")
    create_parser.add_argument("-p", "--password", help="User password")

    # List users command
    subparsers.add_parser("list", help="List all users")

    # Show user command
    show_parser = subparsers.add_parser("show", help="Show user details")
    show_parser.add_argument("email", help="User email")

    # Change password command
    change_pw_parser = subparsers.add_parser("change-password", help="Change user password")
    change_pw_parser.add_argument("email", help="User email")
    change_pw_parser.add_argument("-p", "--password", help="New password")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "create": create_user_command,
        "list": list_users_command,
        "show": show_user_command,
        "change-password": change_password_command,
    }

    command_func = commands.get(args.command)
    if command_func:
        command_func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
