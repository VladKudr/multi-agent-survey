#!/usr/bin/env python3
"""Test script for authentication endpoints."""

import asyncio
import sys
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, ".")

from config.database import init_db, get_db_context
from services.llm_config_service import LLMConfigService
from schemas.llm_config import LLMConfigCreate


async def test_database():
    """Test database connection and initialization."""
    print("Testing database...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def test_user_creation():
    """Test user creation flow."""
    print("\nTesting user creation...")
    try:
        async with get_db_context() as db:
            # Check if we can query users
            from sqlalchemy import select
            from models.user import User
            
            result = await db.execute(select(User).limit(1))
            users = result.scalars().all()
            print(f"✅ Can query users. Found {len(users)} users")
            return True
    except Exception as e:
        print(f"❌ User query error: {e}")
        return False


async def test_llm_config():
    """Test LLM config creation."""
    print("\nTesting LLM config...")
    try:
        async with get_db_context() as db:
            service = LLMConfigService()
            
            # Test validation
            is_valid = service.validate_api_key("kimi", "sk-test12345")
            print(f"✅ API key validation works: {is_valid}")
            
            # Get providers
            providers = service.get_available_providers()
            print(f"✅ Found {len(providers)} providers")
            for p in providers:
                print(f"  - {p.name}: {p.default_model}")
            
            return True
    except Exception as e:
        print(f"❌ LLM config error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_auth_api():
    """Test auth API endpoints."""
    print("\nTesting auth API...")
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        print(f"✅ Health check: {response.json()}")
        
        # Test registration
        unique_id = str(uuid4())[:8]
        register_data = {
            "email": f"test_{unique_id}@example.com",
            "password": "TestPass123",
            "full_name": "Test User",
            "organization_name": f"Test Org {unique_id}",
            "llm_provider": "kimi",
            "llm_model": "kimi-k2-07132k-preview",
            "llm_api_key": "sk-test123456789",
            "llm_temperature": 0.7,
            "llm_max_tokens": 2000
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        if response.status_code == 201:
            print(f"✅ Registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Email: {user_data.get('email')}")
        elif response.status_code == 400:
            print(f"⚠️ Registration returned 400: {response.json()}")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
        
        # Test login
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        
        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful")
            print(f"   Access token: {token_data['access_token'][:20]}...")
            
            # Test /me endpoint
            me_response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"✅ /me endpoint works")
                print(f"   User: {me_data.get('full_name')} ({me_data.get('email')})")
            else:
                print(f"❌ /me endpoint failed: {me_response.status_code}")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ Auth API error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Multi-Agent Survey Platform - Auth Tests")
    print("=" * 60)
    
    results = []
    
    # Test database
    results.append(("Database", await test_database()))
    
    # Test user creation
    results.append(("User Creation", await test_user_creation()))
    
    # Test LLM config
    results.append(("LLM Config", await test_llm_config()))
    
    # Test auth API
    results.append(("Auth API", await test_auth_api()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
