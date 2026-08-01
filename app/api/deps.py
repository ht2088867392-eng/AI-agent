import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.config import Config


# FastAPI 请求鉴权依赖
async def verify_extension_token(
        x_extension_token: Annotated[str | None, Header()] = None,
) -> None:
    expected = Config.browser_extension_token
    # 请求没有令牌，或者令牌不正确抛出异常
    if (
            x_extension_token is None
            or not secrets.compare_digest(
        x_extension_token,
        expected,
    )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid extension token",
        )
