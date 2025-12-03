# config.py
# PredictFlow 配置文件

# =============================================
# 模型配置
# =============================================

# 随机森林参数
RF_N_ESTIMATORS = 200      # 树的数量
RF_MAX_DEPTH = None        # 树的最大深度（None表示不限制）
RF_MIN_SAMPLES_SPLIT = 2   # 内部节点分裂所需的最小样本数
RF_MIN_SAMPLES_LEAF = 1    # 叶节点所需的最小样本数
RF_MAX_FEATURES = "auto"   # 寻找最佳分割时考虑的特征数量
RF_N_JOBS = -1             # 并行作业数（-1表示使用所有CPU核心）
RF_RANDOM_STATE = 42       # 随机种子

# =============================================
# 数据处理配置
# =============================================

# 训练/测试集划分比例
TEST_SIZE = 0.2            # 测试集占比
RANDOM_STATE = 42          # 随机种子

# 缺失值处理策略
# 可选: 'median', 'mean', 'mode', 'drop'
MISSING_VALUE_STRATEGY = 'median'

# 是否进行特征标准化
ENABLE_SCALING = False     # 随机森林通常不需要标准化

# =============================================
# 输入列自动识别配置
# =============================================

# 用于模糊匹配的关键词（识别输入列）
FUZZY_INPUT_KEYS = [
    # 频率相关
    "freq", "frequency", "频率", "倍数", "mult", "multiple",
    # 载荷相关
    "load", "载荷", "载重", "payload", "force", "力",
    # 压力相关
    "pressure", "压力", "press",
    # 速度相关
    "velocity", "速度", "speed",
    # 温度相关（如果作为输入）
    # "temp", "temperature", "温度",
]

# 用于模糊匹配的关键词（识别输出列）
FUZZY_OUTPUT_KEYS = [
    # 应力应变
    "stress", "应力", "strain", "应变",
    # 温度
    "temp", "temperature", "温度",
    # 寿命
    "life", "寿命", "lifetime", "cycle",
    # 位移
    "displacement", "位移", "deformation", "变形",
]

# =============================================
# 数据展示配置
# =============================================

# 展示前N行数据
N_HEAD_ROWS = 5

# 是否显示详细的统计信息
SHOW_DETAILED_STATS = True

# 是否显示相关性矩阵
SHOW_CORRELATION = True

# =============================================
# 文件路径配置
# =============================================

# 默认模型保存路径
DEFAULT_MODEL_PATH = "models/model.joblib"

# 模型保存目录
MODELS_DIR = "models"

# 数据目录
DATA_DIR = "data"
TRAIN_DATA_DIR = "data/train"
INPUT_DATA_DIR = "data/input"

# 输出目录
OUTPUT_DIR = "output"

# 日志配置
LOG_LEVEL = "INFO"         # DEBUG, INFO, WARNING, ERROR
LOG_FILE = None            # 日志文件路径（None表示只输出到控制台）

# =============================================
# 高级模型配置（可选）
# =============================================

# 是否启用交叉验证
ENABLE_CROSS_VALIDATION = False
CV_FOLDS = 5               # 交叉验证折数

# 是否进行超参数搜索
ENABLE_HYPERPARAMETER_SEARCH = False

# 超参数搜索空间
HYPERPARAMETER_GRID = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10],
}

# =============================================
# 其他配置
# =============================================

# 支持的文件格式
SUPPORTED_FILE_FORMATS = ['.csv', '.xlsx', '.xls']

# 数值精度（保留小数位数）
DISPLAY_PRECISION = 4

# 是否在训练时显示进度条
SHOW_PROGRESS = True

