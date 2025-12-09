import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

// API 基础URL配置优先级：
// 1. 运行时配置（window.env.REACT_APP_API_URL）- 适用于 Tomcat 等生产环境
// 2. 构建时环境变量（process.env.REACT_APP_API_URL）- 适用于构建时配置
// 3. 相对路径（空字符串）- 适用于同域部署或通过反向代理访问
// 注意：相对路径适用于后端在同一域名下，或通过 Tomcat 配置反向代理
const getApiBaseUrl = () => {
  // 优先使用运行时配置（适用于 Tomcat 部署）
  if (typeof window !== 'undefined' && window.env && window.env.REACT_APP_API_URL) {
    const url = window.env.REACT_APP_API_URL;
    // 如果配置为占位符，则使用相对路径
    if (url && url !== '$REACT_APP_API_URL' && url !== '') {
      return url;
    }
  }
  // 其次使用构建时环境变量
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // 默认使用相对路径（适用于 Tomcat 反向代理或同域部署）
  return '';
};

const API_BASE_URL = getApiBaseUrl();

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/login`, {
        username,
        password
      });

      if (response.data.success) {
        // 保存token到localStorage
        localStorage.setItem('token', response.data.token);
        // 跳转到预测页面
        navigate('/predict');
      }
    } catch (err) {
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>PredictFlow</h1>
        <h2>用户登录</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>用户名</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              required
            />
          </div>
          <div className="form-group">
            <label>密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
        <div className="login-hint">
          {/* <p>测试账号：admin / admin123</p>
          <p>或：user / user123</p> */}
        </div>
      </div>
    </div>
  );
}

export default Login;

