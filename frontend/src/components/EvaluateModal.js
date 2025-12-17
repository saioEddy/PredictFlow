import React, { useState } from 'react';
import './EvaluateModal.css';

function EvaluateModal({ isOpen, onClose, predictions }) {
  const [activeTab, setActiveTab] = useState('continuous'); // 'continuous' 或 'discontinuous'

  if (!isOpen) return null;

  // 根据预测结果计算评定数据
  // 这里需要根据实际的评定规则来计算，暂时使用示例数据
  const calculateEvaluation = () => {
    if (!predictions || !predictions.predictions) {
      return null;
    }

    const pred = predictions.predictions;
    
    // 从预测结果中提取数据
    // 智能匹配字段名，支持不同的格式
    const getValue = (keys) => {
      for (const key of keys) {
        if (pred[key] !== undefined) {
          return pred[key];
        }
      }
      // 如果直接匹配失败，尝试模糊匹配
      const allKeys = Object.keys(pred);
      for (const key of keys) {
        const keyWithoutUnit = key.replace(/[（(].*?[）)]/g, '').trim();
        const matched = allKeys.find(k => k.includes(keyWithoutUnit));
        if (matched) {
          return pred[matched];
        }
      }
      return 0;
    };
    
    const stressIntensity = getValue(['应力强度最大值 (Mpa)', '应力强度最大值（Mpa）', '应力强度最大值']);
    const strain = getValue(['应变']);
    const membraneStress = getValue(['线性化薄膜应力 (Mpa)', '线性化薄膜应力（Mpa）', '线性化薄膜应力']);
    const membraneBending = getValue(['膜+弯 (Mpa)', '膜+弯（Mpa）', '膜+弯']);
    const stemDeformation = getValue(['阀杆相对变形 (mm)', '阀杆相对变形（mm）', '阀杆相对变形']);

    // 评定标准值（这些值可能需要从后端获取或配置）
    const Sm = 110; // 薄膜应力允许值
    const SmBending = 165; // 1.5Sm
    const maxStrain = 0.43; // 材料的断裂极限应变
    const gap = 2; // 间隙 (mm)
    const material = 'M1114-20MN5M'; // 当前材料

    // 计算总应力
    const totalStress = stressIntensity;

    // 评定结果
    const evaluations = {
      membraneStress: {
        sigmaM_burst: membraneStress,
        sigmaM_other: 0,
        limit: Sm,
        passed: (membraneStress + 0) < Sm
      },
      membraneBending: {
        sigmaMB_burst: membraneBending,
        sigmaMB_other: 0,
        limit: SmBending,
        passed: (membraneBending + 0) < SmBending
      },
      strain: {
        epsilon_burst: strain,
        epsilon_other: 0,
        limit: maxStrain,
        passed: (strain + 0) < maxStrain
      },
      stemDeformation: {
        deformation: stemDeformation,
        gap: gap,
        passed: stemDeformation < gap
      }
    };

    return {
      totalStress,
      material,
      evaluations,
      allPassed: Object.values(evaluations).every(e => e.passed)
    };
  };

  const evaluation = calculateEvaluation();

  if (!evaluation) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>R-CCM评定明细</h2>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="modal-body">
            <p>暂无预测数据</p>
          </div>
        </div>
      </div>
    );
  }

  const { totalStress, material, evaluations, allPassed } = evaluation;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content evaluate-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>R-CCM评定明细</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          {/* 全局参数 */}
          <div className="global-params">
            <div className="param-item">
              <span className="param-label">σ总_破管 (Mpa):</span>
              <span className="param-value">{totalStress.toFixed(2)}</span>
            </div>
            <div className="param-item">
              <span className="param-label">当前材料:</span>
              <span className="param-value">{material}</span>
            </div>
          </div>
          
          {/* 状态栏 */}
          <div className="status-bar">
            {allPassed ? '弹性范围内' : '超出弹性范围'}
          </div>

          {/* 薄膜应力σm */}
          <div className="evaluation-section">
            <div className="section-header">薄膜应力σm</div>
            <div className="section-content">
              <div className="calculation-formula">
                {/* 旧代码：标签在输入框旁边 */}
                {/* <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_burst.toFixed(2)} readOnly />
                <span className="formula-operator">σm_破管</span>
                <span className="formula-operator">+</span>
                <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_other.toFixed(2)} readOnly />
                <span className="formula-operator">σm_其他</span>
                <span className="formula-operator">&lt;</span>
                <span className="formula-operator">Sm(Mpa)</span>
                <input type="text" className="formula-input" value={evaluations.membraneStress.limit} readOnly /> */}
                {/* 新代码：标签在输入框上方 */}
                <div className="formula-item">
                  <span className="formula-label">σm_破管</span>
                  <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_burst.toFixed(2)} readOnly />
                </div>
                <span className="formula-operator">+</span>
                <div className="formula-item">
                  <span className="formula-label">σm_其他</span>
                  <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_other.toFixed(2)} readOnly />
                </div>
                <span className="formula-operator">&lt;</span>
                <div className="formula-item">
                  <span className="formula-label">Sm(Mpa)</span>
                  <input type="text" className="formula-input" value={evaluations.membraneStress.limit} readOnly />
                </div>
              </div>
              <div className={`result-bar ${evaluations.membraneStress.passed ? 'passed' : 'failed'}`}>
                {evaluations.membraneStress.passed ? '通过' : '不通过'}
              </div>
            </div>
          </div>

          {/* 薄膜加弯曲应力σm+b */}
          <div className="evaluation-section">
            <div className="section-header">薄膜加弯曲应力σm+b</div>
            <div className="section-content">
              <div className="tab-container">
                <button 
                  className={`tab-btn ${activeTab === 'continuous' ? 'active' : ''}`}
                  onClick={() => setActiveTab('continuous')}
                >
                  结构连续区域
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'discontinuous' ? 'active' : ''}`}
                  onClick={() => setActiveTab('discontinuous')}
                >
                  局部结构不连续区域
                </button>
              </div>
              <div className="calculation-formula">
                {/* 旧代码：标签在输入框旁边 */}
                {/* <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_burst.toFixed(2)} readOnly />
                <span className="formula-operator">σm+b_破管</span>
                <span className="formula-operator">+</span>
                <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_other.toFixed(2)} readOnly />
                <span className="formula-operator">σm+b_其他</span>
                <span className="formula-operator">&lt;</span>
                <span className="formula-operator">1.5Sm (Mpa)</span>
                <input type="text" className="formula-input" value={evaluations.membraneBending.limit} readOnly /> */}
                {/* 新代码：标签在输入框上方 */}
                <div className="formula-item">
                  <span className="formula-label">σm+b_破管</span>
                  <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_burst.toFixed(2)} readOnly />
                </div>
                <span className="formula-operator">+</span>
                <div className="formula-item">
                  <span className="formula-label">σm+b_其他</span>
                  <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_other.toFixed(2)} readOnly />
                </div>
                <span className="formula-operator">&lt;</span>
                <div className="formula-item">
                  <span className="formula-label">1.5Sm (Mpa)</span>
                  <input type="text" className="formula-input" value={evaluations.membraneBending.limit} readOnly />
                </div>
              </div>
              <div className={`result-bar ${evaluations.membraneBending.passed ? 'passed' : 'failed'}`}>
                {evaluations.membraneBending.passed ? '通过' : '不通过'}
              </div>
            </div>
          </div>

          {/* 应变ε */}
          <div className="evaluation-section">
            <div className="section-header">应变ε</div>
            <div className="section-content">
              <div className="calculation-formula">
                {/* 旧代码：标签在输入框旁边 */}
                {/* <input type="text" className="formula-input" value={evaluations.strain.epsilon_burst.toFixed(4)} readOnly />
                <span className="formula-operator">ε_破管最大</span>
                <span className="formula-operator">+</span>
                <input type="text" className="formula-input" value={evaluations.strain.epsilon_other.toFixed(4)} readOnly />
                <span className="formula-operator">ε_其他</span>
                <span className="formula-operator">&lt;</span>
                <span className="formula-operator">ε_材料的断裂极限应变ε</span>
                <input type="text" className="formula-input" value={evaluations.strain.limit.toFixed(2)} readOnly /> */}
                {/* 新代码：标签在输入框上方 */}
                <div className="formula-item">
                  <span className="formula-label">ε_破管最大</span>
                  <input type="text" className="formula-input" value={evaluations.strain.epsilon_burst.toFixed(4)} readOnly />
                </div>
                <span className="formula-operator">+</span>
                <div className="formula-item">
                  <span className="formula-label">ε_其他</span>
                  <input type="text" className="formula-input" value={evaluations.strain.epsilon_other.toFixed(4)} readOnly />
                </div>
                <span className="formula-operator">&lt;</span>
                <div className="formula-item">
                  <span className="formula-label">ε_材料的断裂极限应变ε</span>
                  <input type="text" className="formula-input" value={evaluations.strain.limit.toFixed(2)} readOnly />
                </div>
              </div>
              <div className={`result-bar ${evaluations.strain.passed ? 'passed' : 'failed'}`}>
                {evaluations.strain.passed ? '通过' : '不通过'}
              </div>
            </div>
          </div>

          {/* 阀杆变形S */}
          <div className="evaluation-section">
            <div className="section-header">阀杆变形S</div>
            <div className="section-content">
              <div className="calculation-formula">
                {/* 旧代码：标签在输入框旁边 */}
                {/* <span className="formula-operator">相对变形S</span>
                <input type="text" className="formula-input" value={evaluations.stemDeformation.deformation.toFixed(4)} readOnly />
                <span className="formula-operator">&lt;</span>
                <span className="formula-operator">间隙 (mm)</span>
                <input type="text" className="formula-input" value={evaluations.stemDeformation.gap} readOnly /> */}
                {/* 新代码：标签在输入框上方 */}
                <div className="formula-item">
                  <span className="formula-label">相对变形S</span>
                  <input type="text" className="formula-input" value={evaluations.stemDeformation.deformation.toFixed(4)} readOnly />
                </div>
                <span className="formula-operator">&lt;</span>
                <div className="formula-item">
                  <span className="formula-label">间隙 (mm)</span>
                  <input type="text" className="formula-input" value={evaluations.stemDeformation.gap} readOnly />
                </div>
              </div>
              <div className={`result-bar ${evaluations.stemDeformation.passed ? 'passed' : 'failed'}`}>
                {evaluations.stemDeformation.passed ? '通过' : '不通过'}
              </div>
            </div>
          </div>

          {/* 最终结论 */}
          <div className="evaluation-section final-conclusion">
            <div className="section-header">最终结论</div>
            <div className="section-content">
              <div className="conclusion-list">
                {/* 旧代码：conclusion-item 没有背景色区分 */}
                {/* <div className="conclusion-item">
                  <span>薄膜应力σm:</span>
                  <span className={evaluations.membraneStress.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.membraneStress.passed ? '通过' : '不通过'}
                  </span>
                </div> */}
                {/* 新代码：根据通过/不通过状态添加背景色类名 */}
                <div className={`conclusion-item ${evaluations.membraneStress.passed ? 'passed' : 'failed'}`}>
                  <span>薄膜应力σm:</span>
                  <span className={evaluations.membraneStress.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.membraneStress.passed ? '通过' : '不通过'}
                  </span>
                </div>
                <div className={`conclusion-item ${evaluations.membraneBending.passed ? 'passed' : 'failed'}`}>
                  <span>薄膜加弯曲应力σm+b:</span>
                  <span className={evaluations.membraneBending.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.membraneBending.passed ? '通过' : '不通过'}
                  </span>
                </div>
                <div className={`conclusion-item ${evaluations.strain.passed ? 'passed' : 'failed'}`}>
                  <span>应变ε:</span>
                  <span className={evaluations.strain.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.strain.passed ? '通过' : '不通过'}
                  </span>
                </div>
                <div className={`conclusion-item ${evaluations.stemDeformation.passed ? 'passed' : 'failed'}`}>
                  <span>阀杆变形S:</span>
                  <span className={evaluations.stemDeformation.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.stemDeformation.passed ? '通过' : '不通过'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EvaluateModal;

