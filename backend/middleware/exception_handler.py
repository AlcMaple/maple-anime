from fastapi import Request, HTTPException, FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError
import traceback
import logging

from exceptions import (
    BaseException,
    NotFoundException,
    DuplicateException,
    ValidationException,
)
from utils.responses import api_response

logger = logging.getLogger(__name__)


def exception_middleware(app: FastAPI):
    """
    异常处理器
    """

    @app.exception_handler(BaseException)
    async def handle_base_exception(request: Request, exc: BaseException):
        logger.warning(f"Business exception: {exc.message}")
        if isinstance(exc, NotFoundException):
            return api_response(404, exc.message)
        elif isinstance(exc, DuplicateException):
            return api_response(400, exc.message)
        elif isinstance(exc, ValidationException):
            return api_response(400, exc.message)
        else:
            return api_response(400, exc.message)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        return api_response(exc.status_code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request, exc: RequestValidationError
    ):
        error_messages = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        return api_response(400, f"参数验证失败: {'; '.join(error_messages)}")

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        if "UNIQUE constraint failed" in error_msg or "Duplicate entry" in error_msg:
            return api_response(400, "数据重复，请检查唯一性约束")
        elif "FOREIGN KEY constraint failed" in error_msg:
            return api_response(400, "外键约束错误，相关数据不存在")
        else:
            return api_response(400, "数据库约束错误")

    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return api_response(500, "服务器内部错误")
