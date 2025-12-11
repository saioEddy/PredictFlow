"""Shiv 启动入口，负责启动 FastAPI 服务."""

import os
import sys
import logging
import socket
import argparse

import uvicorn

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def check_port_available(host: str, port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = s.bind((host, port))
            return True
    except OSError:
        return False

def get_local_ip() -> str:
    """获取本机IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP（不会实际发送数据）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"

def main() -> None:
    """启动 uvicorn 服务，支持命令行参数、环境变量指定 host/port。"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="启动 PredictFlow API 服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认端口 8000
  python3 predictflow-api.shiv
  
  # 指定端口
  python3 predictflow-api.shiv --port 8080
  
  # 指定主机和端口
  python3 predictflow-api.shiv --host 127.0.0.1 --port 9000
  
  # 使用环境变量（优先级低于命令行参数）
  PORT=8080 python3 predictflow-api.shiv
        """
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="指定服务端口（默认: 8000 或环境变量 PORT）"
    )
    parser.add_argument(
        "--host", "-H",
        type=str,
        default=None,
        help="指定监听地址（默认: 0.0.0.0 或环境变量 HOST）"
    )
    
    args = parser.parse_args()
    
    # 优先级：命令行参数 > 环境变量 > 默认值
    host = args.host if args.host is not None else os.environ.get("HOST", "0.0.0.0")
    port = args.port if args.port is not None else int(os.environ.get("PORT", "8000"))
    
    # 获取本机IP
    local_ip = get_local_ip()
    
    # 打印详细的启动信息
    logger.info("=" * 60)
    logger.info("正在启动 PredictFlow API 服务...")
    logger.info("=" * 60)
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"本机IP地址: {local_ip}")
    logger.info(f"监听地址: {host}:{port}")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"本地访问: http://localhost:{port}")
    if local_ip != "unknown":
        logger.info(f"网络访问: http://{local_ip}:{port}")
    logger.info(f"健康检查: http://{host}:{port}/api/health")
    logger.info(f"API 文档: http://{host}:{port}/docs")
    logger.info("=" * 60)
    
    # 检查端口是否可用
    if not check_port_available(host, port):
        logger.warning(f"⚠ 警告: 端口 {port} 可能已被占用或不可用")
    else:
        logger.info(f"✓ 端口 {port} 检查通过")
    
    logger.info("=" * 60)
    logger.info("等待请求...")
    logger.info("=" * 60)
    logger.info("提示: 如果无法从外部访问，请检查:")
    logger.info(f"  1. 防火墙是否开放了 {port} 端口")
    logger.info("  2. 运行: firewall-cmd --list-ports  (CentOS/RHEL)")
    logger.info(f"  3. 运行: netstat -tlnp | grep {port}   (检查端口监听)")
    logger.info(f"  4. 在服务器本地测试: curl http://localhost:{port}/api/health")
    logger.info("=" * 60)
    
    # 启动 uvicorn，启用详细日志
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        log_level="info",  # 使用 info 级别以显示所有请求
        access_log=True,   # 启用访问日志
        use_colors=True    # 启用颜色输出
    )


if __name__ == "__main__":
    main()

