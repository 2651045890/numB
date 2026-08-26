import pandas as pd
import os
import xlrd
import requests
from io import BytesIO

def find_value_in_df(df, value):
    """
    在DataFrame中查找指定值并返回详细信息

    参数：
        df: 要搜索的DataFrame
        value: 要查找的值，可以是整数或字符串

    返回：
        None，但会打印出所有匹配项的详细信息
    """
    print(f"\n查找值'{value}'的结果：")

    # 使用applymap查找所有包含该值的单元格
    mask = df.map(lambda x: str(value) in str(x))

    # 打印每个匹配项的详细信息
    for col in df.columns:
        column_mask = mask[col]
        matches = df[column_mask]
        if not matches.empty:
            print(f"\n在列 '{col}' 中找到：")
            return col

            # for idx, row in matches.iterrows():
            #     print(f"行索引 {idx}: {dict(row)}")

def read_and_find_rows(file_path, sheet_name, target_values, unit_values):
    """
    从Excel文件中查找特定值

    参数：
        file_path: Excel文件路径，参数为 file_path
        sheet_name: 工作表名称，参数为 sheet_name
        target_values: 要搜索的值，参数为 target_values
        unit_values: 要搜索的列值，参数为 target_values

    返回：
        包含目标值的行数据，单位对应的列数
    """
    try:
        Unit_column = ""
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df = df.fillna("")
        # 创建用于过滤的掩码
        mask = pd.Series(False, index=df.index)
        if target_values==[]:
            result_df = df
            # 对于每个目标值，更新掩码
        else:
            for value in target_values:
                current_mask = df.apply(lambda x: x.astype(str).str.contains(str(value)))
                mask |= current_mask.any(axis=1)
            result_df = df[mask]
        if unit_values!="":
            Unit_column = find_value_in_df(df,unit_values)

        return result_df, Unit_column

    except FileNotFoundError:
        print("错误：未找到文件，请检查文件路径")
        return None
    except ValueError as e:
        print(f"错误：{str(e)}")
        return None
    except Exception as e:
        print(f"发生意外错误：{str(e)}")
        return None

def search_section(url,sheet_name,start_word,end_word):
    #excel章节获取
    # url = "D:\代码\代码\docling\docling-main\docling-main\jingyanyuan\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/02 山东青岛平度卢乡（化工）110kV变电站新建工程/06 概算书/1.山东青岛平度卢乡（化工）110千伏变电站新建工程 2025-4-2.xlsx"
    df = pd.read_excel(url, sheet_name=sheet_name)

    # 初始化索引
    start_index = None
    end_index = None

    # 遍历 DataFrame 行
    for i, row in df.iterrows():
        # 将整行转换为字符串并拼接（忽略大小写和空格）
        row_str = ' '.join(row.astype(str).str.strip().str.lower())

        if start_index is None:
            # 还没找到开始标志，继续找
            if start_word.lower() in row_str:
                start_index = i
        else:
            # 已找到开始标志，现在找结束标志
            if end_word.lower() in row_str:
                end_index = i
                break  # 找到第一个就停止

    # 判断是否找到完整范围
    if start_index is not None and end_index is not None and start_index <= end_index:
        result_df = df.loc[start_index:end_index]
        result_df = result_df.fillna("")
        print("提取结果：")
        print(result_df)
    else:
        result_df =""
        print("未找到完整的开始标志或结束标志")
    return result_df

def search_excel(file_path,keywords):
    #关键词查询
    # file_path = 'data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书\唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    # name = file_path.split('\\')
    # 读取所有 sheet
    
    xls = pd.ExcelFile(file_path)

    found = []
    for i,sheet_name in enumerate(xls.sheet_names):
        df = xls.parse(sheet_name)

        for col in df.columns:
            for value in df[col]:
                if any(keyword in str(value).lower() for keyword in keywords):
                    print(f'在 sheet "{sheet_name}" {i}页 中找到关键词 "今天真好"')
                    print(value)
                    found.append(f'在 sheet "{sheet_name}" 页 中找到相关描述: {value}')
                    # break
        # if found:
        #     break

    # if not found:
    #     return f"{name[-1]}架空单项工程无施工验收辅助措施"
    #     print('未找到关键词 "今天真好"')
    # else:
    os.remove(file_path)
    return found

def convert_xls2xlsx(data):
    # file_xls = "D:\代码\代码\线路结构api\point\data/11.xls"
    workbook = xlrd.open_workbook(file_contents=data.getvalue())

    # 假设我们读取第一个 sheet
    sheet = workbook.sheet_by_index(0)

    # 将数据转换为列表
    data = []
    for row_idx in range(sheet.nrows):
        row = sheet.row_values(row_idx)
        data.append(row)

    # 获取列名（第一行作为列名）
    columns = data[0]
    rows = data[1:]

    # 转为 DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # 另存为 .xlsx
    output_xlsx = 'F:\python\point15/test/output.xlsx'
    df.to_excel(output_xlsx, index=False, engine='openpyxl')

    # print(f"已成功将 {file_xls} 转换为 {output_xlsx}")
    return output_xlsx

if __name__=="__main__":
    # 使用示例

    # a = search_excel("data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/02 郁秩～卢乡（化工）110kV线路工程（架空部分）/04 概算书\郁秩～卢乡（化工）110kV线路工程（架空部分）.xlsx",["钢板","井点降水","声波管","大应变","小应变","防腐涂层","钢筋阻锈剂","钢护筒"])
    # print("---------------------------------")
    # b = search_excel("data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/03 线路电缆/01 郁秩～卢乡（化工）110kV线路工程（电缆部分）/04 概算书\郁秩～卢乡（化工）110kV线路工程（电缆部分）.xlsx",["支护","井点降水"])

    #16
    # sheet_name = "输电线路工程工地运输工程量计算表"
    # path = 'data/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    # first_result,first_column = read_and_find_rows(path,sheet_name,["人力运输","汽车运输"],"")
    # if first_result is not None:
    #     if first_column:
    #         result_1 = first_result.loc[:,first_column].values
    #     else:
    #         result_1 = first_result.loc[:].values
    #     print("\n找到以下行数据：")
    #     print(result_1)
    # result_2_dan=float("27")
    # result_2_gexiang=float("26")
    #
    # result_3_dan= float("27")
    # result_3_gexiang= float("26.5")
    # if result_2_gexiang>25 and result_2_gexiang<32 and result_3_gexiang>25 and result_3_gexiang<32:
    #     if abs(result_2_gexiang-result_3_gexiang)<1:
    #         result = "杆塔基础投资占比合理。"
    # else:
    #     result = "杆塔基础投资占比不合理。"
    # print(result)

    a = read_and_find_rows()
