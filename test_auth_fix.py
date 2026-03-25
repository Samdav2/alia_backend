import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.security import get_current_user
from fastapi.security import HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.models.user import User
import uuid

@pytest.mark.asyncio
async def test_get_current_user_fix():
    # Mock dependencies
    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = "valid_token"

    db = AsyncMock() # Mock AsyncSession

    # Mock AuthService.verify_token
    AuthService.verify_token = MagicMock(return_value={"sub": str(uuid.uuid4()), "type": "access"})

    # Mock AuthService.get_user_by_id
    mock_user = MagicMock(spec=User)
    mock_user.id = uuid.uuid4()
    mock_user.is_active = True

    # This is the critical part: get_user_by_id MUST be awaited
    AuthService.get_user_by_id = AsyncMock(return_value=mock_user)

    # Call the function
    user = await get_current_user(credentials, db)

    # Assertions
    assert user == mock_user
    AuthService.get_user_by_id.assert_called_once()
    print("\n✅ get_current_user correctly awaited AuthService.get_user_by_id!")

if __name__ == "__main__":
    pytest.main([__file__])
