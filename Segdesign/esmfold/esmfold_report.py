import os
import re
import pandas as pd
import biotite.structure.io as bsio
import shutil
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
import sys
import argparse
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录添加到 Python 的模块搜索路径中
sys.path.append(root_dir)
from dssp.dssp import run_dssp
from dssp.dsspcsv import dssp_to_csv
from hmmer.pdb_to_fasta import pdb_to_fasta


def parse_args():
    parser = argparse.ArgumentParser(description='Protein 3D Structure Prediction(esmfold)', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument('--fasta_folder', type=str, default=None, help="Folder for storing sequence files")
    parser.add_argument('--esmfold_report_path', type=str, default=None, help="Folder for storing ESMFold report")
    parser.add_argument('--esmfold_folder', type=str, help="The folder where esmfold's output data is stored")
    parser.add_argument('--original_protein_chain_path', type=str,
                        help="The path to the initial protein chain's PDB file. If the hmmer module has been used, the path is:{hmmer_out_folder}/target_chain_pdb/{your_pdb}")
    parser.add_argument('--plddt_threshold', type=float, default=None, help='pLDDT selection threshold')
    parser.add_argument('--ptm_threshold', type=float, default=None, help='ptm selection threshold')

    parser.add_argument('--seq_range_str', type=str, help='Enter the area to be modified, in the format: start position-end position, such as 1-10')
    return parser.parse_args()

def natural_sort_key(filename):
    """生成自然排序的key：将文件名拆分为字符串和数字部分，数字转整数"""
    parts = re.split(r'(\d+)', os.path.splitext(filename)[0])
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part)
    return key

#为预测的pdb生成dssp文件和对应的csv文件
def make_dssp_csv(structure_prediction_files_folder, dssp_folder, csv_folder):
    backbone_folders = os.listdir(structure_prediction_files_folder)
    backbone_folders = sorted(backbone_folders, key=natural_sort_key)

    for backbone_folder in backbone_folders:
        backbone_folder_path = os.path.join(structure_prediction_files_folder, backbone_folder)

        dssp_backbone_folder_path = os.path.join(dssp_folder, backbone_folder)
        if not os.path.exists(dssp_backbone_folder_path):
            os.makedirs(dssp_backbone_folder_path, exist_ok=True)

        csv_backbone_folder_path = os.path.join(csv_folder, backbone_folder)
        if not os.path.exists(csv_backbone_folder_path):
            os.makedirs(csv_backbone_folder_path, exist_ok=True)

        pdb_files = os.listdir(backbone_folder_path)
        pdb_files = sorted(pdb_files, key=natural_sort_key)

        for pdb_file in pdb_files:
            file_name = os.path.splitext(pdb_file)[0]
            pdb_file_path = os.path.join(backbone_folder_path, pdb_file)
            dssp_file_path = os.path.join(dssp_backbone_folder_path, f'{file_name}.dssp')
            csv_file_path = os.path.join(csv_backbone_folder_path, f'{file_name}.csv')
            run_dssp(pdb_file_path, dssp_file_path)
            dssp_to_csv(dssp_file_path, csv_file_path)

    return

def get_start_end(input_str):
    """
    提取输入中的开始数字和结束数字
    """
    if " " in input_str:
        num_list = [int(num) for num in input_str.split()]
        return num_list[0], num_list[-1]
    elif "-" in input_str:
        match = re.match(r"^[A-Za-z]*(\d+)-(\d+)$", input_str)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            return start, end
    else:
        match = re.match(r"^[A-Za-z]*(\d+)$", input_str)
        if match:
            num = int(match.group(1))
            return num, num
    return None, None


def add_ss_data(esmfold_report_path, dssp_csv_path, start_res, end_res):
    def csv_column_ratio_with_list(csv_path, start_idx, end_idx, column):
        """
        提取CSV指定列、指定行范围的元素列表，并统计各元素占比
        参数：
            csv_path: CSV文件路径（绝对/相对）
            start_idx: 开始索引（从1开始）
            end_idx: 结束索引（从1开始，包含）
            column: 列名（如"性别"）或列索引（从0开始，如0）
        返回：
            字典：
                - 元素列表：指定范围的原始元素（含空值，Python原生列表）
                - 占比统计：{元素: 占比（保留2位小数）}，强制包含H/E/C（无则0.00）
        示例：
            >>> result = csv_column_ratio_with_list("test.csv", 1, 10, "类型")
            >>> print(result["占比统计"])  # {'H': 0.30, 'E': 0.00, 'C': 0.50, 'A': 0.20}
        """
        # 异常处理：检查文件是否存在
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV文件不存在：{csv_path}")

        # 1. 读取CSV文件（跳过空行，保留原始索引）
        try:
            df = pd.read_csv(csv_path, skip_blank_lines=True)
        except Exception as e:
            raise ValueError(f"读取CSV失败：{str(e)}")

        # 异常处理：空DataFrame
        if df.empty:
            raise ValueError("CSV文件无有效数据（空文件/全是空行）")

        # 2. 验证索引范围（从1开始→转换为0开始的切片）
        total_rows = len(df)
        if start_idx < 1 or end_idx < 1:
            raise ValueError("开始/结束索引必须≥1")
        if start_idx > end_idx:
            raise ValueError("开始索引不能大于结束索引")
        if end_idx > total_rows:
            raise ValueError(f"结束索引超出文件总行数（总行数：{total_rows}）")

        # 转换为0开始的切片（左闭右开，end_idx无需-1）
        slice_start = start_idx - 1
        slice_end = end_idx

        # 3. 提取指定列的指定行范围数据
        try:
            # 按列名/列索引提取列
            if isinstance(column, int):
                if column >= len(df.columns):
                    raise IndexError(f"列索引{column}超出范围（文件列数：{len(df.columns)}）")
                target_column = df.iloc[:, column]
            else:
                if column not in df.columns:
                    raise KeyError(f"列名'{column}'不存在（文件列名：{df.columns.tolist()}）")
                target_column = df[column]

            # ① 原始元素列表（含空值，保留原生类型）
            raw_element_list = target_column.iloc[slice_start:slice_end].tolist()
            # ② 去空值的列表（用于统计占比）
            clean_element_list = [x for x in raw_element_list if pd.notna(x)]

        except (KeyError, IndexError) as e:
            raise e
        except Exception as e:
            raise ValueError(f"提取列数据失败：{str(e)}")

        # 4. 统计元素占比（强制包含H/E/C，保留2位小数）
        required_elements = ['H', 'E', 'C']  # 必须包含的元素
        ratio_result = {}
        total_clean = len(clean_element_list)

        if total_clean == 0:
            # 无有效数据时，H/E/C占比均为0
            ratio_result = {elem: 0.00 for elem in required_elements}
        else:
            # 步骤1：初始化占比字典，先将H/E/C设为0
            ratio_result = {elem: 0.00 for elem in required_elements}
            # 步骤2：计算所有元素的占比（包括H/E/C和其他元素）
            count_series = pd.Series(clean_element_list).value_counts()
            for elem, count in count_series.items():
                ratio_result[str(elem)] = round(count / total_clean, 4)

        # 5. 按文档要求返回字典
        str_element = ''.join(raw_element_list)
        return str_element, ratio_result

    design_ss3 = []
    design_ss8 = []
    h_prop = []
    e_prop = []
    c_prop = []
    backbone_folders = os.listdir(dssp_csv_path)
    backbone_folders = sorted(backbone_folders, key=natural_sort_key)
   
    for backbone_folder in backbone_folders:
        backbone_folder_path = os.path.join(dssp_csv_path, backbone_folder)
        
        dssp_csv_files = os.listdir(backbone_folder_path)
        dssp_csv_files = sorted(dssp_csv_files, key=natural_sort_key)

        for dssp_csv_file in dssp_csv_files:
            dssp_csv_file_path = os.path.join(backbone_folder_path, dssp_csv_file)

            design_seq8, useless = csv_column_ratio_with_list(
                csv_path= dssp_csv_file_path,
                start_idx=start_res,
                end_idx=end_res,
                column='SS_8'
            )
            design_seq, dict_prop = csv_column_ratio_with_list(
                csv_path=dssp_csv_file_path,
                start_idx=start_res,
                end_idx=end_res,
                column='SS_3'
            )
            design_ss8.append(design_seq8)
            design_ss3.append(design_seq)
            for key, value in dict_prop.items():
                if key == 'H':
                    h_prop.append(value)
                if key == 'E':
                    e_prop.append(value)
                if key == 'C':
                    c_prop.append(value)

    df = pd.read_csv(esmfold_report_path)
    df['esmfold_ss8'] = design_ss8
    df['esmfold_ss3'] = design_ss3
    df['esmfold_H_prop'] = h_prop
    df['esmfold_E_prop'] = e_prop
    df['esmfold_C_prop'] = c_prop
    df.to_csv(esmfold_report_path, index=False)
    
    return 
    
            
    

#处理ESMfold的CSV文件，根据阈值进行筛选，按backbone分类的字典返回
def process_esmfold_csv(csv_input_path, fasta_output_path,
                        plddt_threshold=None, ptm_threshold=None):
    """
    处理ESMfold的CSV文件，按backbone分类的字典返回

    新增返回值:
    dict: 按backbone分组的字典，结构为 {backbone: {index: sequence, ...}, ...}
    """
    # 1. 基础参数与文件验证

    # 读取CSV并验证必要列（新增backbone列验证）
    print(f"正在读取CSV文件: {csv_input_path}")
    df = pd.read_csv(csv_input_path)
    required_columns = ['ptm_score', 'plddt_score', 'index', 'sequence', 'backbone']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"CSV文件缺少必要的列: {', '.join(missing_columns)}")

    # 2. 数据类型转换与筛选逻辑
    df['ptm_score'] = pd.to_numeric(df['ptm_score'], errors='coerce')
    df['plddt_score'] = pd.to_numeric(df['plddt_score'], errors='coerce')

    # 构建筛选条件（满足任一阈值即通过）
    pass_condition = pd.Series(False, index=df.index)
    if plddt_threshold is not None and ptm_threshold is None:
        print(f"  - plddt筛选阈值: > {plddt_threshold}")
        pass_condition = pass_condition | (df['plddt_score'] > plddt_threshold)
    elif ptm_threshold is not None and plddt_threshold is None:
        print(f"  - ptm筛选阈值: > {ptm_threshold}")
        pass_condition = pass_condition | (df['ptm_score'] > ptm_threshold)
    elif plddt_threshold is not None and ptm_threshold is not None:
        print(f"  - ptm筛选阈值: > {ptm_threshold}, plddt筛选阈值: > {plddt_threshold}")
        pass_condition = pass_condition | ((df['ptm_score'] > ptm_threshold) & (df['plddt_score'] > plddt_threshold))
    else:
        print(f'不进行ptm和plddt筛选')
        pass_condition = pass_condition | (df['plddt_score'] > 0)

    # 3. 更新CSV文件（添加whether_pass列）
    df['whether_pass'] = pass_condition
    df.to_csv(csv_input_path, index=False)
    print(f"\n已更新CSV文件，新增whether_pass列: {csv_input_path}")

    # 4. 生成FASTA文件（仅通过筛选的序列）
    passed_df = df[df['whether_pass']].copy()
    print(f"\n筛选结果统计:")
    print(f"  - 总序列数: {len(df)}")
    print(f"  - 通过筛选序列数: {len(passed_df)}")
    print(f"  - 通过比例: {len(passed_df) / len(df) * 100:.2f}%")

    if len(passed_df) > 0:
        with open(fasta_output_path, 'w', encoding='utf-8') as f:
            for _, row in passed_df.iterrows():
                f.write(f">{row['index']}, pTM={row['ptm_score']}, pLDDT={'plddt_score'}\n{row['sequence']}\n")
        print(f"已生成FASTA文件: {fasta_output_path}")
    else:
        print("\n警告：无序列通过筛选，未生成FASTA文件")

    # 5. 核心新增：生成按backbone分类的字典
    backbone_dict = {}
    # 遍历通过筛选的行，按backbone分组
    for _, row in passed_df.iterrows():
        backbone = row['backbone']
        seq_index = row['index']  # 保留原index作为键
        sequence = row['sequence']
        ptm_score = row['plddt_score']
        plddt_score = row['plddt_score']

        # 若backbone未在字典中，初始化空字典；否则添加index-sequence键值对
        if backbone not in backbone_dict:
            backbone_dict[backbone] = {}
        if seq_index not in backbone_dict[backbone]:
            backbone_dict[backbone][seq_index] = {}
        backbone_dict[backbone][seq_index]['sequence'] = sequence
        backbone_dict[backbone][seq_index]['ptm'] = ptm_score
        backbone_dict[backbone][seq_index]['plddt'] = plddt_score

    print(f"\n已生成按backbone分类的字典，包含 {len(backbone_dict)} 个不同backbone")
    return backbone_dict  # 返回最终字典

#生成筛选后的文件夹
def filter_files(esmfold_folder, filter_folder, backbone_dict):
    if not os.path.exists(filter_folder):
        os.makedirs(filter_folder, exist_ok=True)

    for backbone, values in backbone_dict.items():
        filter_backbone_folder = os.path.join(filter_folder, backbone)
        if not os.path.exists(filter_backbone_folder):
            os.makedirs(filter_backbone_folder, exist_ok=True)
        with open(f'{filter_backbone_folder}/{backbone}_filter.fa', 'a+', encoding='utf-8') as f:
            f.truncate(0)
            for index, values2 in values.items():
                file_path = os.path.join(esmfold_folder, 'structure_prediction_files', backbone, f'{index}.pdb')
                copy_path = os.path.join(filter_folder, backbone, f'{index}.pdb')
                shutil.copy(file_path, copy_path)
                f.write(f">{index}, pTM={values2['ptm']}, pLDDT={values2['plddt']}\n")
                f.write(f"{values2['sequence']}\n")

    return




def main():
    args = parse_args()
    esmfold_report_path = args.esmfold_report_path
    esmfold_folder = args.esmfold_folder
    original_protein_chain_path = args.original_protein_chain_path
    plddt_threshold = args.plddt_threshold
    ptm_threshold = args.ptm_threshold
    seq_range_str = args.seq_range_str

    start, end = get_start_end(seq_range_str)

    work_dir = esmfold_folder.rsplit('/',1)[0]
    if esmfold_report_path is None:
        esmfold_report_path = os.path.join(work_dir, 'esmfold_report.csv')

    structure_prediction_files_folder = os.path.join(esmfold_folder, 'structure_prediction_files')
    dssp_folder = os.path.join(esmfold_folder, 'dssp_files')
    csv_folder = os.path.join(esmfold_folder, 'csv_files')

    make_dssp_csv(
        structure_prediction_files_folder=structure_prediction_files_folder,
        dssp_folder=dssp_folder,
        csv_folder=csv_folder,
    )

    add_ss_data(
        esmfold_report_path=esmfold_report_path,
        dssp_csv_path=csv_folder,
        start_res=start,
        end_res=end
    )

    backbone_dict = process_esmfold_csv(
        csv_input_path = esmfold_report_path,
        fasta_output_path = f'{esmfold_folder}/filter_result.fa',
        plddt_threshold=plddt_threshold,
        ptm_threshold=ptm_threshold
    )

    filter_files(
        esmfold_folder=esmfold_folder,
        filter_folder=f'{esmfold_folder}/filter_files',
        backbone_dict=backbone_dict
    )

    return

if __name__ == '__main__':
    main()




    
    