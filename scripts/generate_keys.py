"""
Utility script to generate secure keys and update the .env file.
Run this script to generate new secure keys for your application.
"""
import os
import secrets
import sys
from pathlib import Path

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(length)

def update_env_file(env_path: Path, updates: dict):
    """Update or add key-value pairs in the .env file."""
    # Read existing .env file if it exists
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Update with new values
    env_vars.update(updates)
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    
    # Generate new keys
    secret_key = generate_secret_key()
    
    # Update .env file
    updates = {
        'SECRET_KEY': secret_key,
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '1440',  # 24 hours
        'DEBUG': 'False',
        'FIRST_SUPERUSER': 'admin@example.com',
        'FIRST_SUPERUSER_PASSWORD': secrets.token_urlsafe(12)
    }
    
    update_env_file(env_path, updates)
    
    print("✅ Successfully generated new secure keys and updated .env file")
    print("\n🔑 New Admin Credentials:")
    print(f"   Email: {updates['FIRST_SUPERUSER']}")
    print(f"   Password: {updates['FIRST_SUPERUSER_PASSWORD']}")
    print("\n⚠️  IMPORTANT: Keep these credentials secure and change them after first login!")

if __name__ == "__main__":
    main()
