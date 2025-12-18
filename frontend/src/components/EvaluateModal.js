import React, { useState } from 'react';
import './EvaluateModal.css';

function EvaluateModal({ isOpen, onClose, predictions }) {
  const [activeTab, setActiveTab] = useState('continuous'); // 'continuous' 或 'discontinuous'
  // 新代码：添加状态管理"其他"字段的值
  const [sigmaMOther, setSigmaMOther] = useState(0);
  const [sigmaMBOther, setSigmaMBOther] = useState(0);
  const [epsilonOther, setEpsilonOther] = useState(0);

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
    
    // 字段映射：评定页面字段对应预测页面的预测值
    // σ总_破管 (Mpa) 对应 应力强度最大值（Mpa）
    const stressIntensity = getValue(['应力强度最大值 (Mpa)', '应力强度最大值（Mpa）', '应力强度最大值']);
    // 应变ε 对应 应变
    const strain = getValue(['应变']);
    // 薄膜应力σm_破管 对应 线性化薄膜应力（Mpa）
    const membraneStress = getValue(['线性化薄膜应力 (Mpa)', '线性化薄膜应力（Mpa）', '线性化薄膜应力']);
    // 薄膜加弯曲应力σm+b_破管 对应 膜+弯（Mpa）
    const membraneBending = getValue(['膜+弯 (Mpa)', '膜+弯（Mpa）', '膜+弯']);
    // 阀杆变形S 对应 阀杆相对变形（mm）
    const stemDeformation = getValue(['阀杆相对变形 (mm)', '阀杆相对变形（mm）', '阀杆相对变形']);

    // 评定标准值（这些值可能需要从后端获取或配置）
    const Sm = 110; // 薄膜应力允许值
    // 旧代码：固定使用 1.5Sm
    /* const SmBending = 165; // 1.5Sm */
    // 新代码：根据标签页选择不同的标准值
    const SmBendingContinuous = 165; // 1.5Sm = 165Mpa (结构连续区域)
    const SmBendingDiscontinuous = 330; // 3Sm = 330Mpa (局部结构不连续区域)
    const SmBending = activeTab === 'continuous' ? SmBendingContinuous : SmBendingDiscontinuous;
    const maxStrain = 0.43; // 材料的断裂极限应变
    const gap = 2; // 间隙 (mm)
    
    // 新代码：确保数值类型一致，避免字符串和数字比较的问题
    const stemDeformationNum = Number(stemDeformation) || 0;
    const material = 'M1114-20MN5M'; // 当前材料

    // 计算总应力
    // σ总_破管 (Mpa) = 应力强度最大值（Mpa）
    const totalStress = stressIntensity;

    // 旧代码：使用固定的0值
    /* const evaluations = {
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
    }; */
    // 新代码：使用状态中的"其他"字段值，并根据标签页使用不同的限制值
    const evaluations = {
      membraneStress: {
        sigmaM_burst: membraneStress,
        sigmaM_other: sigmaMOther,
        limit: Sm,
        passed: (membraneStress + sigmaMOther) < Sm
      },
      membraneBending: {
        sigmaMB_burst: membraneBending,
        sigmaMB_other: sigmaMBOther,
        limit: SmBending,
        passed: (membraneBending + sigmaMBOther) < SmBending
      },
      strain: {
        epsilon_burst: strain,
        epsilon_other: epsilonOther,
        limit: maxStrain,
        passed: (strain + epsilonOther) < maxStrain
      },
      stemDeformation: {
        deformation: stemDeformationNum, // 使用转换后的数字类型
        gap: gap,
        // 旧代码：可能存在类型不一致的问题（如果 stemDeformation 是字符串）
        /* passed: stemDeformation < gap */
        // 新代码：确保使用数字类型进行比较
        passed: stemDeformationNum < gap
      }
    };

    return {
      totalStress,
      material,
      evaluations
      // 旧代码：在这里计算 allPassed
      /* allPassed: Object.values(evaluations).every(e => e.passed) */
      // 新代码：allPassed 在组件中根据 showAllEvaluations 计算
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

  const { totalStress, material, evaluations } = evaluation;

  // 新代码：根据 σ总_破管 的值决定显示哪些评定内容
  // 如果 σ总_破管 < 275MPa：显示所有4段判断内容
  // 如果 σ总_破管 >= 275MPa：只显示应变ε和阀杆变形S
  const stressThreshold = 275; // σ总_破管的阈值（MPa）
  const showAllEvaluations = totalStress < stressThreshold;
  
  // 新代码：判断是否在弹性范围内（仅根据 σ总_破管 的值）
  // totalStress < 275：弹性范围内
  // totalStress >= 275：塑性范围内
  const isElasticRange = totalStress < stressThreshold;
  
  // 旧代码：allPassed 的逻辑
  /* const allPassed = totalStress < stressThreshold 
    ? (showAllEvaluations 
        ? Object.values(evaluations).every(e => e.passed)
        : evaluations.strain.passed && evaluations.stemDeformation.passed)
    : false; */
  // 新代码：allPassed 根据弹性/塑性范围判断
  // 弹性范围内：判断所有显示的评定项
  // 塑性范围内：只判断应变ε和阀杆变形S
  const allPassed = isElasticRange
    ? (showAllEvaluations 
        ? Object.values(evaluations).every(e => e.passed)
        : evaluations.strain.passed && evaluations.stemDeformation.passed)
    : (evaluations.strain.passed && evaluations.stemDeformation.passed); // 塑性范围内只判断应变ε和阀杆变形S

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content evaluate-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="header-title-section">
            <h2>R-CCM评定明细</h2>
            {/* 新代码：添加是否通过状态 */}
            <span className={`header-status ${allPassed ? 'status-passed' : 'status-failed'}`}>
              {allPassed ? '通过' : '不通过'}
            </span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          {/* 全局参数 */}
          <div className="global-params">
            <div className="param-item">
              <span className="param-label">σ总_破管 (Mpa):</span>
              {/* 旧代码：保留原始精度 */}
              {/* <span className="param-value">{totalStress}</span> */}
              {/* 新代码：与预测页面保持一致，显示4位小数 */}
              <span className="param-value">{totalStress.toFixed(4)}</span>
            </div>
            <div className="param-item">
              <span className="param-label">当前材料:</span>
              <span className="param-value">{material}</span>
            </div>
          </div>
          
          {/* 状态栏 */}
          <div className="status-bar">
            {/* 旧代码：根据 allPassed 判断 */}
            {/* {allPassed ? '弹性范围内' : '超出弹性范围'} */}
            {/* 新代码：只根据 σ总_破管 是否超过 275 来判断 */}
            {isElasticRange ? '弹性范围内' : '塑性范围内'}
          </div>

          {/* 旧代码：始终显示所有评定内容 */}
          {/* 新代码：根据 σ总_破管 的值条件显示 */}
          {/* 薄膜应力σm - 只在 σ总_破管 < 275MPa 时显示 */}
          {showAllEvaluations && (
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
                  {/* 旧代码：保留原始精度 */}
                  {/* <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_burst} readOnly /> */}
                  {/* 新代码：与预测页面保持一致，显示4位小数 */}
                  <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_burst.toFixed(4)} readOnly />
                </div>
                <span className="formula-operator">+</span>
                <div className="formula-item">
                  <span className="formula-label">σm_其他</span>
                  {/* 旧代码：只读输入框 */}
                  {/* <input type="text" className="formula-input" value={evaluations.membraneStress.sigmaM_other.toFixed(2)} readOnly /> */}
                  {/* 新代码：可编辑输入框 */}
                  <input 
                    type="number" 
                    className="formula-input" 
                    value={sigmaMOther} 
                    onChange={(e) => setSigmaMOther(parseFloat(e.target.value) || 0)}
                    step="0.01"
                  />
                </div>
                {/* 旧代码：固定显示 < */}
                {/* <span className="formula-operator">&lt;</span> */}
                {/* 新代码：根据实际计算结果动态显示 < 或 > */}
                <span className="formula-operator">
                  {(evaluations.membraneStress.sigmaM_burst + evaluations.membraneStress.sigmaM_other) < evaluations.membraneStress.limit ? '<' : '>'}
                </span>
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
          )}

          {/* 薄膜加弯曲应力σm+b - 只在 σ总_破管 < 275MPa 时显示 */}
          {showAllEvaluations && (
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
                  {/* 旧代码：保留原始精度 */}
                  {/* <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_burst} readOnly /> */}
                  {/* 新代码：与预测页面保持一致，显示4位小数 */}
                  <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_burst.toFixed(4)} readOnly />
                </div>
                <span className="formula-operator">+</span>
                <div className="formula-item">
                  <span className="formula-label">σm+b_其他</span>
                  {/* 旧代码：只读输入框 */}
                  {/* <input type="text" className="formula-input" value={evaluations.membraneBending.sigmaMB_other.toFixed(2)} readOnly /> */}
                  {/* 新代码：可编辑输入框 */}
                  <input 
                    type="number" 
                    className="formula-input" 
                    value={sigmaMBOther} 
                    onChange={(e) => setSigmaMBOther(parseFloat(e.target.value) || 0)}
                    step="0"
                  />
                </div>
                {/* 旧代码：固定显示 < */}
                {/* <span className="formula-operator">&lt;</span> */}
                {/* 新代码：根据实际计算结果动态显示 < 或 > */}
                <span className="formula-operator">
                  {(evaluations.membraneBending.sigmaMB_burst + evaluations.membraneBending.sigmaMB_other) < evaluations.membraneBending.limit ? '<' : '>'}
                </span>
                <div className="formula-item">
                  {/* 旧代码：固定显示 1.5Sm */}
                  {/* <span className="formula-label">1.5Sm (Mpa)</span> */}
                  {/* 新代码：根据标签页显示不同的标准值 */}
                  <span className="formula-label">
                    {activeTab === 'continuous' ? '1.5Sm (Mpa)' : '3Sm (Mpa)'}
                  </span>
                  <input type="text" className="formula-input" value={evaluations.membraneBending.limit} readOnly />
                </div>
              </div>
              <div className={`result-bar ${evaluations.membraneBending.passed ? 'passed' : 'failed'}`}>
                {evaluations.membraneBending.passed ? '通过' : '不通过'}
              </div>
            </div>
          </div>
          )}

          {/* 应变ε - 始终显示 */}
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
                  {/* 旧代码：保留原始精度 */}
                  {/* <input type="text" className="formula-input" value={evaluations.strain.epsilon_burst} readOnly /> */}
                  {/* 新代码：与预测页面保持一致，显示4位小数 */}
                  <input type="text" className="formula-input" value={evaluations.strain.epsilon_burst.toFixed(4)} readOnly />
                </div>
                <span className="formula-operator">+</span>
                <div className="formula-item">
                  <span className="formula-label">ε_其他</span>
                  {/* 旧代码：只读输入框 */}
                  {/* <input type="text" className="formula-input" value={evaluations.strain.epsilon_other.toFixed(4)} readOnly /> */}
                  {/* 新代码：可编辑输入框 */}
                  <input 
                    type="number" 
                    className="formula-input" 
                    value={epsilonOther} 
                    onChange={(e) => setEpsilonOther(parseFloat(e.target.value) || 0)}
                    step="0.0001"
                  />
                </div>
                {/* 旧代码：固定显示 < */}
                {/* <span className="formula-operator">&lt;</span> */}
                {/* 新代码：根据实际计算结果动态显示 < 或 > */}
                <span className="formula-operator">
                  {(evaluations.strain.epsilon_burst + evaluations.strain.epsilon_other) < evaluations.strain.limit ? '<' : '>'}
                </span>
                <div className="formula-item">
                  <span className="formula-label">ε_材料的断裂极限应变ε</span>
                  {/* 旧代码：固定保留两位小数 */}
                  {/* <input type="text" className="formula-input" value={evaluations.strain.limit.toFixed(2)} readOnly /> */}
                  {/* 新代码：保留原始精度 */}
                  <input type="text" className="formula-input" value={evaluations.strain.limit} readOnly />
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
                  {/* 旧代码：保留原始精度 */}
                  {/* <input type="text" className="formula-input" value={evaluations.stemDeformation.deformation} readOnly /> */}
                  {/* 新代码：与预测页面保持一致，显示4位小数 */}
                  <input type="text" className="formula-input" value={evaluations.stemDeformation.deformation.toFixed(4)} readOnly />
                </div>
                {/* 旧代码：固定显示 < */}
                {/* <span className="formula-operator">&lt;</span> */}
                {/* 新代码：根据实际计算结果动态显示 < 或 > */}
                <span className="formula-operator">
                  {evaluations.stemDeformation.deformation < evaluations.stemDeformation.gap ? '<' : '>'}
                </span>
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
                {/* 旧代码：始终显示所有评定项 */}
                {/* 新代码：根据 σ总_破管 的值条件显示 */}
                {/* 薄膜应力σm - 只在 σ总_破管 < 275MPa 时显示 */}
                {showAllEvaluations && (
                <div className={`conclusion-item ${evaluations.membraneStress.passed ? 'passed' : 'failed'}`}>
                  <span>薄膜应力σm:</span>
                  <span className={evaluations.membraneStress.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.membraneStress.passed ? '通过' : '不通过'}
                  </span>
                </div>
                )}
                {/* 薄膜加弯曲应力σm+b - 只在 σ总_破管 < 275MPa 时显示 */}
                {showAllEvaluations && (
                <div className={`conclusion-item ${evaluations.membraneBending.passed ? 'passed' : 'failed'}`}>
                  <span>薄膜加弯曲应力σm+b:</span>
                  <span className={evaluations.membraneBending.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.membraneBending.passed ? '通过' : '不通过'}
                  </span>
                </div>
                )}
                {/* 应变ε - 始终显示 */}
                <div className={`conclusion-item ${evaluations.strain.passed ? 'passed' : 'failed'}`}>
                  <span>应变ε:</span>
                  <span className={evaluations.strain.passed ? 'passed-text' : 'failed-text'}>
                    {evaluations.strain.passed ? '通过' : '不通过'}
                  </span>
                </div>
                {/* 阀杆变形S - 始终显示 */}
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

