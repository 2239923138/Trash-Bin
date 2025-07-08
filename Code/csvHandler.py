import os
import csv

def select_file(csv_files):
    print("找到以下CSV文件：")
    for i, file in enumerate(csv_files):
        print(f"{i}: {file}")
    while True:
        try:
            choice = int(input("请输入要操作的文件编号："))
            if 0 <= choice < len(csv_files):
                return csv_files[choice]
            else:
                print("输入超出范围，请重新输入。")
        except ValueError:
            print("请输入有效的数字！")

def get_output_count():
    while True:
        try:
            count = int(input("请输入要生成的新文件数量："))
            if count > 0:
                return count
            else:
                print("请输入大于0的整数。")
        except ValueError:
            print("请输入有效的整数！")

def get_column_indices(headers):
    print("\n列索引与名称对应关系：")
    for idx, header in enumerate(headers):
        print(f"{idx}: {header}")

    while True:
        try:
            user_input = input("请输入要包含的列索引（用空格分隔，例如：0 2 4）：")
            indices = list(map(int, user_input.strip().split()))
            unique_indices = list(set(indices))  # 去重
            invalid = [i for i in unique_indices if i < 0 or i >= len(headers)]
            if invalid:
                print(f"以下索引无效：{invalid}，请重新输入。")
            else:
                return unique_indices
        except ValueError:
            print("请输入有效的整数列表，用空格分隔。")

def split_and_merge_columns(filename, output_count, headers):
    selected_columns_list = []
    
    print("\n开始为每个输出文件选择列：")
    for i in range(output_count):
        print(f"\n--- 第 {i + 1} 个输出文件 ---")
        selected_cols = get_column_indices(headers)
        selected_columns_list.append(selected_cols)

    return selected_columns_list

def write_new_csvs(filename, selected_columns_list):
    base_name = os.path.splitext(filename)[0]

    with open(filename, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data_rows = [row for row in reader]

    for idx, col_indices in enumerate(selected_columns_list):
        new_headers = [headers[i] for i in col_indices]
        new_data = [[row[i] for i in col_indices] for row in data_rows]

        output_filename = f"{base_name}_output_{idx + 1}.csv"
        with open(output_filename, mode='w', newline='', encoding='utf-8') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(new_headers)
            writer.writerows(new_data)
        print(f"已生成文件：{output_filename}")

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # 切换工作目录到脚本目录

    # 查找该目录下的所有CSV文件
    csv_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.csv')]
    
    if not csv_files:
        print("当前脚本目录下没有CSV文件。")
        return

    print("当前目录：", script_dir)
    print("检测到以下CSV文件：")
    for i, f in enumerate(csv_files):
        print(f"{i}: {f}")

    selected_file = select_file(csv_files)

    full_path = os.path.join(script_dir, selected_file)

    with open(full_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

    if not headers:
        print("源文件为空或格式不正确。")
        return

    output_count = get_output_count()
    selected_columns_list = split_and_merge_columns(selected_file, output_count, headers)
    write_new_csvs(full_path, selected_columns_list)

if __name__ == "__main__":
    main()