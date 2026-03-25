import sys
import os

# Add current directory to path to import app
sys.path.append(os.getcwd())

from app.services.auth_service import AuthService
import bcrypt

def test_bcrypt_fix():
    print("Testing bcrypt fix for long passwords...")

    # Test 1: Long password (> 72 chars)
    long_password = "a" * 100
    print(f"Password length: {len(long_password)}")

    # Hash the password
    hashed = AuthService.get_password_hash(long_password)
    print("Password hashed successfully.")

    # Verify the password
    is_valid = AuthService.verify_password(long_password, hashed)
    print(f"Verification result: {is_valid}")

    if is_valid:
        print("✅ Success! Long password hashed and verified correctly.")
    else:
        print("❌ Failure! Long password verification failed.")
        return False

    # Test 2: Standard password
    short_password = "secure_password123"
    hashed_short = AuthService.get_password_hash(short_password)
    is_valid_short = AuthService.verify_password(short_password, hashed_short)
    print(f"Standard password verification result: {is_valid_short}")

    if is_valid_short:
        print("✅ Success! Standard password hashed and verified correctly.")
    else:
        print("❌ Failure! Standard password verification failed.")
        return False

    # Test 3: Truncation check
    # Bcrypt should treat "a" * 72 and "a" * 100 as the same password due to truncation
    p72 = "a" * 72
    p100 = "a" * 100
    h72 = AuthService.get_password_hash(p72)

    if AuthService.verify_password(p100, h72):
        print("✅ Success! Truncation logic is working as expected (p100 matches h72).")
    else:
        print("❌ Failure! Truncation logic mismatch.")
        return False

    return True

if __name__ == "__main__":
    try:
        if test_bcrypt_fix():
            print("\nALL TESTS PASSED! The bcrypt fix is working correctly.")
            sys.exit(0)
        else:
            print("\nTESTS FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
