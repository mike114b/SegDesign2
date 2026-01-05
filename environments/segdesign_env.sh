#!/bin/bash

set -e  # 出错立即退出，避免静默失败
# Hmmer分步安装脚本

echo "=== Hmmer模块环境的安装 ==="

ENV_NAME="segdesign"
# 1. 创建基础环境
echo "创建环境..."
echo "conda create -n '$ENV_NAME' python=3.9 -y"
conda create -n "$ENV_NAME" python=3.9 -y

if [ -n "$CONDA_PATH" ]; then
    echo "检测到 CONDA_PATH，使用环境激活方式安装"
    # 加载conda环境
    if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
        source "$CONDA_PATH/etc/profile.d/conda.sh"
    elif [ -f "$CONDA_PATH/bin/activate" ]; then
        source "$CONDA_PATH/bin/activate"
    else
        echo "找不到conda激活脚本" >&2
        exit 1
    fi

    echo "进入虚拟环境..."
    echo "conda activate '$ENV_NAME'"
    conda activate "$ENV_NAME"

    # 添加 conda-forge 频道（若未添加）
    echo "添加 conda-forge 频道"
    conda config --add channels conda-forge
    conda config --set channel_priority strict

    echo "安装hmmer"
    echo "conda install bioconda::hmmer==3.3.2 -y"
    conda install bioconda::hmmer==3.3.2 -y


    #安装pandas库
    echo "安装pandas库"
    echo "conda install pandas -y"
    conda install pandas -y
    #安装biopython库
    echo "安装biopython库"
    echo "conda install biopython -y"
    conda install biopython -y
    # 安装 hhsuite
    echo "安装hhsuite库"
    echo "conda install -c conda-forge -c bioconda hhsuite -y"
    conda install -c conda-forge -c bioconda hhsuite -y

    echo "安装evcouplings库"
    echo "pip install evcouplings"
    pip install evcouplings

    # 安装dssp
    echo "安装dssp"
    echo "conda install -c conda-forge dssp=4.5.5 -y"
    conda install -c conda-forge dssp=4.5.5 -y

    echo "安装mmseqs2"
    echo "conda install -c conda-forge -c bioconda mmseqs2 -y"
    conda install -c conda-forge -c bioconda mmseqs2 -y

    echo "安装biotite"
    echo "conda install conda-forge::biotite -y"
    conda install conda-forge::biotite -y

else
    echo "未检测到 CONDA_PATH，使用 conda run 方式安装"
    # 添加 conda-forge 频道（若未添加）
    echo "添加 conda-forge 频道"
    conda run -n "$ENV_NAME" conda config --add channels conda-forge
    conda run -n "$ENV_NAME" conda config --set channel_priority strict

    echo "安装hmmer"
    echo "conda run -n '$ENV_NAME' conda install bioconda::hmmer==3.3.2 -y"
    conda run -n "$ENV_NAME" conda install bioconda::hmmer==3.3.2 -y

    #安装pandas库
    echo "安装pandas库"
    echo "conda run -n '$ENV_NAME' conda install pandas -y"
    conda run -n "$ENV_NAME" conda install pandas -y
    #安装biopython库
    echo "安装biopython库"
    echo "conda run -n '$ENV_NAME' conda install biopython -y"
    conda run -n "$ENV_NAME" conda install biopython -y
    # 安装 hhsuite
    echo "安装hhsuite库"
    echo "conda run -n '$ENV_NAME' conda install -c conda-forge -c bioconda hhsuite -y"
    conda run -n "$ENV_NAME" conda install -c conda-forge -c bioconda hhsuite -y

    echo "安装evcouplings库"
    echo "conda run -n '$ENV_NAME' pip install evcouplings"
    conda run -n "$ENV_NAME" pip install evcouplings

    # 安装dssp
    echo "安装dssp"
    echo "conda run -n '$ENV_NAME' conda install -c conda-forge dssp=4.5.5 -y"
    conda run -n "$ENV_NAME" conda install -c conda-forge dssp=4.5.5 -y

    echo "安装mmseqs2"
    echo "conda run -n '$ENV_NAME' conda install -c conda-forge -c bioconda mmseqs2 -y"
    conda run -n "$ENV_NAME" conda install -c conda-forge -c bioconda mmseqs2 -y

    echo "安装biotite"
    echo "conda run -n '$ENV_NAME' conda install conda-forge::biotite -y"
    conda run -n "$ENV_NAME" conda install conda-forge::biotite -y

fi


