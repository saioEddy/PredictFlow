import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

// API 基础URL：如果设置了环境变量 REACT_APP_API_URL 则使用，否则使用相对路径
// 相对路径适用于 FastAPI 同时提供前后端服务
// 绝对路径适用于前后端分离部署
// const API_BASE_URL = process.env.REACT_APP_API_URL || '';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

