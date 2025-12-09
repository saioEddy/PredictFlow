#!/bin/bash
# 网络诊断脚本 - 检查服务是否可访问

echo "============================================================"
echo "PredictFlow 网络诊断工具"
echo "============================================================"
echo ""

# 获取本机IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "本机IP地址: $LOCAL_IP"
echo ""

# 检查8000端口是否在监听
echo "1. 检查8000端口监听状态:"
if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo "   ✓ 端口8000正在监听"
    netstat -tlnp 2>/dev/null | grep ":8000 "
elif ss -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo "   ✓ 端口8000正在监听"
    ss -tlnp 2>/dev/null | grep ":8000 "
else
    echo "   ✗ 端口8000未在监听"
fi
echo ""

# 检查防火墙状态
echo "2. 检查防火墙状态:"
if command -v firewall-cmd &> /dev/null; then
    echo "   防火墙服务状态:"
    systemctl status firewalld --no-pager -l 2>/dev/null | head -3
    echo ""
    echo "   已开放的端口:"
    firewall-cmd --list-ports 2>/dev/null || echo "   无法获取防火墙信息"
    echo ""
    echo "   如果8000端口未开放，运行以下命令:"
    echo "   firewall-cmd --permanent --add-port=8000/tcp"
    echo "   firewall-cmd --reload"
elif command -v ufw &> /dev/null; then
    echo "   UFW防火墙状态:"
    ufw status 2>/dev/null || echo "   无法获取防火墙信息"
    echo ""
    echo "   如果8000端口未开放，运行以下命令:"
    echo "   ufw allow 8000/tcp"
elif command -v iptables &> /dev/null; then
    echo "   检查iptables规则:"
    iptables -L -n | grep 8000 || echo "   未找到8000端口规则"
    echo ""
    echo "   如果需要开放8000端口，运行:"
    echo "   iptables -A INPUT -p tcp --dport 8000 -j ACCEPT"
else
    echo "   未检测到常见的防火墙工具"
fi
echo ""

# 测试本地连接
echo "3. 测试本地连接:"
if command -v curl &> /dev/null; then
    echo "   测试 http://localhost:8000/api/health"
    curl -s -o /dev/null -w "   状态码: %{http_code}\n" --connect-timeout 3 http://localhost:8000/api/health || echo "   ✗ 连接失败"
else
    echo "   未安装curl，无法测试"
fi
echo ""

# 测试网络IP连接
echo "4. 测试网络IP连接:"
if command -v curl &> /dev/null && [ ! -z "$LOCAL_IP" ]; then
    echo "   测试 http://$LOCAL_IP:8000/api/health"
    curl -s -o /dev/null -w "   状态码: %{http_code}\n" --connect-timeout 3 http://$LOCAL_IP:8000/api/health || echo "   ✗ 连接失败"
else
    echo "   未安装curl或无法获取IP，跳过测试"
fi
echo ""

# 检查进程
echo "5. 检查Python服务进程:"
ps aux | grep -E "python.*predictflow|uvicorn" | grep -v grep || echo "   未找到相关进程"
echo ""

echo "============================================================"
echo "诊断完成"
echo "============================================================"

