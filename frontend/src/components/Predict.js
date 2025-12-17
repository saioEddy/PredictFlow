import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Predict.css';
import EvaluateModal from './EvaluateModal';

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

function Predict() {
  const [load, setLoad] = useState('');
  const [frequency, setFrequency] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modelInfo, setModelInfo] = useState(null);
  const [showEvaluateModal, setShowEvaluateModal] = useState(false);
  const navigate = useNavigate();

  // 检查是否已登录
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // 获取模型信息
    const fetchModelInfo = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/model-info`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setModelInfo(response.data);
      } catch (err) {
        console.error('获取模型信息失败:', err);
      }
    };

    fetchModelInfo();
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setPredictions(null);
    setLoading(true);

    const token = localStorage.getItem('token');

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/predict`,
        {
          load: parseFloat(load),
          frequency: parseFloat(frequency)
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setPredictions(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        // token过期，跳转到登录页
        localStorage.removeItem('token');
        navigate('/login');
      } else {
        setError(err.response?.data?.detail || '预测失败，请检查输入数据');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="predict-container">
      <div className="predict-box">
        <div className="header">
          <h1>PredictFlow</h1>
          <button onClick={handleLogout} className="logout-btn">退出登录</button>
        </div>

        <div className="form-section">
          <h2>输入预测参数</h2>
          <div className="form-with-chart">
            <div className="form-container">
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>载荷</label>
                  <input
                    type="number"
                    step="any"
                    value={load}
                    onChange={(e) => setLoad(e.target.value)}
                    placeholder="请输入载荷值"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>频率</label>
                  <input
                    type="number"
                    step="any"
                    value={frequency}
                    onChange={(e) => setFrequency(e.target.value)}
                    placeholder="请输入频率值"
                    required
                  />
                </div>
                {error && <div className="error-message">{error}</div>}
                <button type="submit" disabled={loading} className="submit-btn">
                  {loading ? '预测中...' : '开始预测'}
                </button>
              </form>
            </div>
            {/* <div className="chart-container"> */}
            <div>
              <img 
                src="/images/245f9a38-87e4-4a3c-8c5c-a8a24e7a04c4.png" 
                alt="1倍载荷, 1倍频率冲击加速度时程图"
                className="chart-image"
              />
            </div>
          </div>
        </div>

        {modelInfo && (
          <div className="model-info">
            <h3>模型信息</h3>
            <p><strong>输入列：</strong>{modelInfo.inputs.join(', ')}</p>
            <p><strong>输出列：</strong>{modelInfo.outputs.join(', ')}</p>
          </div>
        )}

        {predictions && (
          <div className="result-section">
            <h2>预测结果</h2>
            <div className="result-with-model">
              <div className="result-box">
                <div className="input-display">
                  <h3>输入参数</h3>
                  <p>载荷: {predictions.input_data.load}</p>
                  <p>频率: {predictions.input_data.frequency}</p>
                </div>
                <div className="output-display">
                  <h3>输出参数</h3>
                  {Object.entries(predictions.predictions).map(([key, value]) => (
                    <p key={key}>
                      <strong>{key}:</strong> {typeof value === 'number' ? value.toFixed(4) : value}
                    </p>
                  ))}
                </div>
              </div>
              {/* <div className="model-3d-container"> */}
              <div >
                <img 
                  src="/images/af80d348-6294-4c32-9886-71640a663d29.png" 
                  alt="3D模型可视化"
                  className="model-3d-image"
                />
              </div>
            </div>
            <div className="evaluate-button-container">
              <button 
                className="evaluate-btn"
                onClick={() => setShowEvaluateModal(true)}
              >
                评定
              </button>
            </div>
          </div>
        )}
      </div>
      
      {/* 评定弹窗 */}
      <EvaluateModal
        isOpen={showEvaluateModal}
        onClose={() => setShowEvaluateModal(false)}
        predictions={predictions}
      />
    </div>
  );
}

export default Predict;

