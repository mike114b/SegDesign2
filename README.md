# SegDesign: Intelligent Protein Segment Design Pipeline

<div align="center">

**An integrated pipeline for intelligent protein segment design combining sequence analysis, structure prediction, and generative modeling**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README_EN.md) | [中文](README_CN.md)

</div>

## 📖 Overview

SegDesign is an automated pipeline for intelligent protein segment design. It integrates multiple state-of-the-art bioinformatics tools and deep learning models to perform comprehensive protein analysis and design.

### Key Features

- **Sequence Conservation Analysis**: Using HMMER for evolutionary conservation analysis
- **Structure Generation**: Using RFdiffusion for targeted protein backbone generation
- **Sequence Design**: Using ProteinMPNN for amino acid sequence optimization
- **Structure Validation**: Using ESMFold for predicted structure quality assessment
- **Sequence Clustering**: Using MMSeqs2 for sequence similarity analysis

## 🏗️ Architecture

```
SegDesign/
├── Segdesign.py              # Main entry point
├── Segdesign/
│   ├── hmmer/               # Sequence conservation analysis
│   ├── rfdiffusion/         # Structure generation
│   ├── mpnn/                # Sequence design
│   ├── esmfold/             # Structure prediction
│   └── dssp/                # Secondary structure analysis
├── config/
│   ├── config.yaml          # User configuration
│   └── setting.yaml         # System settings
├── environments/            # Environment installation scripts
└── example/                 # Example outputs
```

## 🚀 Quick Start

### Prerequisites

| Component | Requirement |
|-----------|-------------|
| OS | Linux (recommended) or Windows with WSL2 |
| Python | 3.9+ |
| Conda/Miniconda | Required for environment management |
| GPU | NVIDIA GPU with CUDA support (recommended) |
| RAM | 16GB minimum (32GB+ recommended) |
| Storage | 50GB+ free space |

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SegDesign.git
   cd SegDesign
   ```

2. **Install conda environments**
   ```bash
   # Main environment (HMMER, MMSeqs2, DSSP)
   bash environments/segdesign_env.sh
   
   # ESMFold environment (requires CUDA)
   bash environments/esmfold_env.sh
   ```

3. **Configure paths** in `config/setting.yaml`

### Basic Usage

```bash
# Run complete pipeline
python Segdesign.py --config config/config.yaml

# Run specific modules
python Segdesign.py --config config/config.yaml --modules hmmer,mpnn
```

## 📋 Configuration

Configure your analysis in `config/config.yaml`:

```yaml
project:
  input_pdb: ./Dusp4.pdb      # Input protein structure
  output_dir: ./output        # Output directory
  chain: A                    # Chain to analyze
  segment: 346-394            # Design region

profile:
  database: ./uniprot_sprot.fasta
  bitscore: 0.3
  cpu: 10

rfdiffusion:
  num_designs: 10
  threshold: 0.04

mpnn:
  num_seq_per_target: 20
  sampling_temp: 0.3

esmfold:
  ptm_threshold: 0.54
  plddt_threshold: 70
```

## 📊 Example Output

See `example/Dusp4_example/` for complete output example with:

- Conservation analysis reports
- Generated backbone structures
- Designed sequences
- Structure validation scores

### Output Files

| File/Folder | Description |
|-------------|-------------|
| `hmmer_out/` | Conservation analysis results |
| `rfdiffusion_out/` | Generated backbone structures |
| `mpnn_out/` | Designed sequences |
| `esmfold_report.csv` | Final validation report |

## 🔧 Modules

| Module | Function | Environment |
|--------|----------|-------------|
| HMMER | Sequence conservation analysis | segdesign |
| RFdiffusion | Structure generation | SE3nv |
| ProteinMPNN | Sequence design | segdesign |
| ESMFold | Structure validation | segdesign_esmfold |
| MMSeqs2 | Sequence clustering | segdesign |

## 📚 Documentation

- [English Documentation](README_EN.md) - Detailed English guide
- [中文文档](README_CN.md) - 详细中文指南

## ⚠️ Troubleshooting

### GPU Memory Issues
```bash
export CUDA_VISIBLE_DEVICES=0
```

### Conda Environment
```bash
export CONDA_PATH="/path/to/anaconda3"
source $CONDA_PATH/etc/profile.d/conda.sh
```

## 📝 Citation

```bibtex
@misc{segdesign2024,
  title = {SegDesign: Intelligent Protein Segment Design Pipeline},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/SegDesign}
}
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

**Happy Protein Designing! 🔬🧬**

</div>
