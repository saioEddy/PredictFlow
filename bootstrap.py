"""Shiv 启动入口，负责启动 FastAPI 服务."""

import os

import uvicorn


def main() -> None:
    """启动 uvicorn 服务，环境变量可覆盖 host/port。"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("api.main:app", host=host, port=port)


if __name__ == "__main__":
    main()

