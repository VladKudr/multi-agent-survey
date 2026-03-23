#!/usr/bin/env python3
"""Check project structure and provide setup instructions."""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if file exists."""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("=" * 60)
    print("Multi-Agent Survey Simulation Platform - Project Check")
    print("=" * 60)
    print()
    
    # Check project structure
    print("📁 Checking project structure...")
    files_to_check = [
        ("backend/main.py", "Backend entry point"),
        ("backend/requirements.txt", "Backend dependencies"),
        ("backend/models/user.py", "User model with LLM config"),
        ("backend/api/auth.py", "Auth API"),
        ("backend/api/llm_config.py", "LLM Config API"),
        ("backend/llm/gateway.py", "LLM Gateway"),
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/app/page.tsx", "Frontend home page"),
        ("frontend/app/login/page.tsx", "Login page"),
        ("frontend/app/register/page.tsx", "Register page"),
        ("frontend/app/settings/llm/page.tsx", "LLM Settings page"),
        ("infra/docker-compose.yml", "Docker Compose config"),
        ("agent-configs/sample-tech-ooo.yaml", "Sample agent config"),
        (".env.example", "Environment example"),
    ]
    
    all_exist = True
    for path, desc in files_to_check:
        if not check_file(path, desc):
            all_exist = False
    
    print()
    
    if all_exist:
        print("🎉 All required files are in place!")
    else:
        print("⚠️  Some files are missing. Please check the project structure.")
        return 1
    
    print()
    print("=" * 60)
    print("🚀 To start the project:")
    print("=" * 60)
    print()
    print("1. Make sure Docker and Docker Compose are installed:")
    print("   https://docs.docker.com/get-docker/")
    print()
    print("2. Run the start script:")
    print("   chmod +x start.sh")
    print("   ./start.sh")
    print()
    print("Or manually:")
    print("   cd infra")
    print("   docker-compose up -d --build")
    print()
    print("3. Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   API:      http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print()
    print("4. Register a new account with your Kimi API key:")
    print("   - Get your API key from: https://platform.moonshot.cn")
    print("   - Or use OpenAI, Anthropic, or Ollama")
    print()
    print("5. Create surveys and run simulations!")
    print()
    print("To stop:")
    print("   cd infra && docker-compose down")
    print()
    print("To view logs:")
    print("   cd infra && docker-compose logs -f")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
