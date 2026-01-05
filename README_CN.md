# SegDesign：智能蛋白质片段设计 pipeline

<div align="center">

**集序列分析、结构预测和生成建模于一体的智能蛋白质片段设计 pipeline**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📖 项目简介

SegDesign 是一个用于智能蛋白质片段设计的自动化 pipeline。它整合了多种先进的生物信息学工具和深度学习模型，可执行全面的蛋白质分析与设计：

- **序列保守性分析**：使用 HMMER 进行进化保守性分析
- **结构生成**：使用 RFdiffusion 进行靶向蛋白质骨架生成
- **序列设计**：使用 ProteinMPNN 进行氨基酸序列优化
- **结构验证**：使用 ESMFold 进行预测结构质量评估
- **序列聚类**：使用 MMSeqs2 进行序列相似性分析

## 🏗️ 项目架构

```
SegDesign/
├── Segdesign.py              # 主程序入口
├── Segdesign/
│   ├── hmmer/               # 序列保守性分析
│   ├── rfdiffusion/         # 结构生成
│   ├── mpnn/                # 序列设计
│   ├── esmfold/             # 结构预测
│   └── dssp/                # 二级结构分析
├── config/
│   ├── config.yaml          # 用户配置文件
│   └── setting.yaml         # 系统配置文件
├── environments/            # 环境安装脚本
└── example/                 # 示例输出
```

## 🚀 快速开始

### 前置条件

- **操作系统**：Linux（推荐）或 Windows+WSL2
- **Python**：3.9 或更高版本
- **Conda/Miniconda**：环境管理必需
- **GPU**：NVIDIA GPU 且支持 CUDA（强烈推荐用于 ESMFold 和 RFdiffusion）
- **内存**：至少 16GB RAM（推荐 32GB 以上）
- **存储**：至少 50GB 可用空间

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/SegDesign.git
cd SegDesign
```

#### 2. 安装 Conda 环境

项目需要多个 conda 环境来运行不同的模块。请运行安装脚本：

```bash
# 安装主环境（HMMER、MMSeqs2、DSSP 等）
bash environments/segdesign_env.sh

# 如果 conda 不在默认路径，请设置
export CONDA_PATH="/path/to/your/anaconda3"

# 安装 ESMFold 环境（需要 CUDA 支持）
bash environments/esmfold_env.sh
```

#### 3. 安装数据库（可选）

进行 HMMER 分析时，可能需要下载序列数据库：

```bash
# 下载 UniRef90 数据库
bash environments/download_uniref90.sh

# 下载 UniRef100 数据库
bash environments/download_uniref100.sh
```

#### 4. 配置路径

编辑 `config/setting.yaml` 文件，配置以下路径：
- Anaconda 安装路径
- RFdiffusion 安装路径
- ProteinMPNN 安装路径
- 数据库路径

## 📋 配置文件说明

### 用户配置（`config/config.yaml`）

用户配置文件控制整个工作流程的参数：

```yaml
project:
  anaconda_path: /path/to/anaconda3  # Anaconda 安装路径
  input_pdb: ./Dusp4.pdb             # 输入的蛋白质结构文件
  output_dir: ./output               # 输出目录
  chain: A                           # 待分析的链
  sequence_length: 394               # 完整序列长度
  segment: 346-394                   # 设计区域（可选）

profile:
  database: ./uniprot_sprot.fasta    # 序列数据库
  bitscore: 0.3                      # HMMER bit score 阈值
  n_iter: 5                          # JackHMMER 迭代次数
  cpu: 10                            # CPU 核心数
  threshold: 0.6                     # 保守性阈值

rfdiffusion:
  num_designs: 10                    # 生成设计的数量
  threshold: 0.04                    # 设计质量阈值
  helix: false                       # 按 α-螺旋设计
  strand: false                      # 按 β-折叠设计

mpnn:
  num_seq_per_target: 20             # 每个设计生成的序列数
  sampling_temp: 0.3                 # MPNN 采样温度
  seed: 42                           # 随机种子
  top_percent: 0.9                   # 顶部百分比选择

esmfold:
  ptm_threshold: 0.54                # PTM 分数阈值
  plddt_threshold: 70                # pLDDT 分数阈值
```

## 💻 使用方法

### 基本用法

运行完整的 pipeline：

```bash
python Segdesign.py --config config/config.yaml
```

### 模块单独运行

可以单独运行各个模块：

```bash
# 仅运行序列分析
python Segdesign.py --config config/config.yaml --modules hmmer

# 仅运行结构生成和设计
python Segdesign.py --config config/config.yaml --modules rfdiffusion,mpnn

# 仅运行结构验证
python Segdesign.py --config config/config.yaml --modules esmfold
```

### 示例：Dusp4 蛋白质设计

`example/Dusp4_example/` 目录包含完整的输出示例：

```bash
# 运行示例工作流程
python Segdesign.py --config example/Dusp4_example/config.yaml
```

## 📊 输出文件结构

```
output/
├── config.yaml                    # 配置文件的副本
├── hmmer_out/                     # HMMER 分析结果
│   ├── Dusp4_A_Recommended_Design_Area.txt
│   ├── Dusp4_A_conservative_comprehensive_report.csv
│   └── jackhmmer_out/            # 原始 HMMER 比对结果
├── rfdiffusion_out/              # RFdiffusion 结果
│   ├── sample/                   # 生成的骨架结构
│   └── filter_results/           # 过滤后的结构
├── mpnn_out/                     # MPNN 序列设计结果
│   ├── seqs/                     # 设计的序列
│   └── csv_files/                # 分析 CSV 文件
└── esmfold_report.csv            # 最终验证报告
```

### 输出文件列说明

| 列名 | 说明 |
|------|------|
| index | 设计编号 |
| backbone | 骨架来源结构 |
| segment | 设计区域 |
| score | 设计分数 |
| plddt_score | ESMFold pLDDT 置信度分数 |
| ptm_score | ESMFold PTM 分数 |
| whether_pass | 质量控制通过状态 |

## 🔧 模块详细说明

### 1. HMMER 模块
- 使用 JackHMMER 进行序列保守性分析
- 识别保守区域以智能选择设计区域
- 生成综合保守性报告

### 2. RFdiffusion 模块
- 为设计区域生成新的蛋白质骨架
- 支持二级结构约束（螺旋/折叠）
- 生成多个设计候选

### 3. ProteinMPNN 模块
- 为生成的骨架设计氨基酸序列
- 优化序列的稳定性和表达性
- 支持固定骨架位置

### 4. ESMFold 模块
- 使用深度学习预测验证设计结构
- 评估 pLDDT 和 PTM 分数
- 过滤低质量设计

### 5. MMSeqs2 模块（可选）
- 进行序列聚类分析
- 识别序列多样性
- 生成聚类报告

## ⚠️ 常见问题处理

### GPU 内存不足
```bash
# 减小批量大小或设计数量
# 设置 GPU 内存限制环境变量
export CUDA_VISIBLE_DEVICES=0
```

### Conda 环境激活问题
```bash
# 确保 CONDA_PATH 设置正确
export CONDA_PATH="/path/to/anaconda3"
source $CONDA_PATH/etc/profile.d/conda.sh
```

### 数据库错误
- 验证 `config/setting.yaml` 中的数据库路径
- 确保数据库格式正确
- 检查文件权限

## 📝 引用

如果您在研究中使用了 SegDesign，请引用：

```bibtex
@misc{segdesign2024,
  title = {SegDesign: Intelligent Protein Segment Design Pipeline},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/SegDesign}
}
```

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献代码！请随时提交 Pull Request。

## 📧 联系方式

如有疑问或建议，请提交 issue 或联系作者。

---

<div align="center">

**祝您蛋白质设计愉快！🔬🧬**

</div>
