# -*- coding: utf-8 -*-
# created by mdc 2025.8.25

import csv
import os

import pdfplumber
from PIL import Image
from io import BytesIO
import requests
import re
import fitz # PyMuPDF
from tqdm import tqdm
import pandas as pd
import json



def process_table(data):
    """
    处理一个包含多个长度相同的列表的主列表：
    如果某个子列表的第一个值为空，则赋值为上一个子列表的第一个值。

    :param data: list[list] - 主列表，其中每个子列表长度为3
    :return: list[list] - 处理后的主列表
    """
    k = 1
    if data[0][0].replace('\n','') == "序号":
        k = 2
    # 遍历主列表
    for i in range(1, len(data)): # 从索引1开始，因为需要参考前一个子列表
        for j in range(k):
            if data[i][j] == None:  # 检查当前子列表的第一个值是否为空
                data[i][j] = data[i - 1][j]  # 赋值为上一个子列表的第一个值

    return data
#提取检测表格
def exact_table(matchs,page_num,table_list,page):

    result = []
    result_df = []
    page_res = []
    # if matchs:
    try:
        table_match = [item.replace("\n", "") for item in matchs]
        table_section = {
            'num': page_num,
            'table_name': table_match
        }
        # print(table_section)
        table_list.append(table_section)

        #####提取表格######
        exact_tables = page.extract_tables()
        if len(exact_tables) > len(table_match):
            table_match.insert(0, table_list[-2]['table_name'][-1])
        if exact_tables:
            for table_num, table in enumerate(exact_tables):
                # print(any(name in table_match[table_num] for name in table_name))
                # for name in table_name:
                #     print(table_match[table_num])
                # if any(name in table_match[table_num] for name in table_name):
            # if any(name in table_match[table_num] for name in table_name):
                    print(f"表格名称 {table_match[table_num]},page:{page_num}")
                    res = {"name": table_match[table_num], "page": page_num}

                    result.append(json.dumps(res))
                    df_value = []
                    page_res.append(page_num)
                    for row in table:
                        print(row)
                        res = {"name": row, "page": ""}
                        result.append(json.dumps(res))
                        df_value.append(row)
                    new_result = process_table(df_value)
                    df_result = pd.DataFrame(new_result[1:],columns=new_result[0])
                    print("-" * 50)
                    result_df.append(df_result)
        return result,result_df
    except:
        return result,result_df

def exact_table1(matchs,page_num,table_list,page,table_name):
    #非全量
    result = []
    result_df = []
    page_res = []
    # if matchs:
    try:
        table_match = [item.replace("\n", "") for item in matchs]
        table_section = {
            'num': page_num,
            'table_name': table_match
        }
        # print(table_section)
        table_list.append(table_section)

        #####提取表格######
        exact_tables = page.extract_tables()
        if len(exact_tables) > len(table_match):
            table_match.insert(0, table_list[-2]['table_name'][-1])
        if exact_tables:
            for table_num, table in enumerate(exact_tables):
                # print(any(name in table_match[table_num] for name in table_name))
                # for name in table_name:
                #     print(table_match[table_num])
                # if any(name in table_match[table_num] for name in table_name):
            # if any(name in table_match[table_num] for name in table_name):
                    print(f"表格名称 {table_match[table_num]},page:{page_num}")
                    res = {"name": table_match[table_num], "page": page_num}

                    result.append(json.dumps(res))
                    df_value = []
                    page_res.append(page_num)
                    for row in table:
                        print(row)
                        res = {"name": row, "page": ""}
                        result.append(json.dumps(res))
                        df_value.append(row)
                    new_result = process_table(df_value)
                    df_result = pd.DataFrame(new_result[1:],columns=new_result[0])
                    print("-" * 50)
                    result_df.append(df_result)
        return result,result_df
    except:
        return result,result_df

def extract_table_from_page(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages"):
            # print(f"正在处理第 {page_num} 页...")
            table = page.extract_tables()
            df_result = pd.DataFrame(table[0][1:], columns=table[0][0])
            df_result.columns = df_result.columns.str.replace('\n', '', regex=False)
        return df_result


def deal_match(s, lst):
    order_map = {}
    for item in lst:
        idx = s.find(item)
        if idx != -1:
            order_map[item] = idx
    
    sorted_list = sorted(
        [item for item in lst if item in order_map],
        key = lambda x: order_map[x]
    )

    not_found_items = [item for item in lst if item not in order_map]

    return sorted_list + not_found_items

def extract_tables_from_pdf(url,table_content):
    """
    按照自定义标题类型切分PDF文档提取表格、附件。
    入参：
        pdf_path: str PDF文件路径
        table_name: str 表格名称
    返回：
        biaoges: list[list] 表格列表格式结果
        biaoges_df: list[Dataframe] 表格df格式结果
        fujians: list[list] 附件列表格式结果
        fujians_df: list[Dataframe] 附件df格式结果
    """
    tu_patterns = {
        # 1: r"1\.1\s[\u4e00-\u9fa5]+",
        1: r"\n表\s\d..+?\n",
        2: r".+?\s表\d",
        3: r".+?表\n",
        4: r".+?表.+?\n"
    }
    fujian_patterns = {
        1: r"附件\s\d\s.+\n",
        2: r".+?附件\n",
    }
    tables = []
    biaoges = []
    biaoges_df = []
    fujian_lists = []
    fujians = []
    fujians_df = []
    page_list=[]
    # pdf_file=url
    res = requests.get(url)
    pdf_file = BytesIO(res.content)
    # 提取PDF文本
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages"):
            # print(f"正在处理第 {page_num} 页...")
            text = page.extract_text()
            exact_tables = page.extract_tables()
            
            table_matchs = []
            fujian_matchs = []
            for num,pattern in tu_patterns.items():
                table_match = re.findall(pattern, text)
                table_match = [item.replace('\n', '') for item in table_match if '见表' not in item and len(item) < 30]
                if table_match:
                    table_matchs.extend(table_match)
            cleaned_data = [s.replace(' ','') for s in table_matchs]
            table_matchs = deal_match(text.replace(' ',''),cleaned_data)
            # if exact_tables:
            #     print(table_matchs)
            res = []
            for ta in table_matchs:
                if ta not in res:
                    res.append(ta)
            
            for num_fujian,pattern_fujian in fujian_patterns.items():
                # fujian_match = re.findall(pattern_fujian, text,re.DOTALL)
                fujian_match = re.findall(pattern_fujian, text)

                fujian_matchs.extend(fujian_match)
            try:
                if table_matchs:
                    # biaoge,biaoge_df,pa = exact_table(table_matchs, page_num, tables, page, table_name=table_name)

                    biaoge,biaoge_df = exact_table(table_matchs, page_num, tables, page)
                    if biaoge:
                        page_list.append(page_num)
                        # page_list.append(pa)

                        biaoges.extend(biaoge)
                        biaoges_df.extend(biaoge_df)
                    # break
                elif fujian_matchs:

                    fujian,fujian_df = exact_table(fujian_matchs, page_num, fujian_lists, page)
                    if fujian:
                        page_list.append(page_num)
                        fujians.extend(fujian)
                        fujians_df.extend(fujian_df)

                elif exact_tables:
                    biaoge_str = ""
                    if table_content:
                        table_content_json = json.loads(table_content)
                        for t_name, t_value in table_content_json.items():
                            temp_exact_table = str(exact_tables).replace("\n", "").replace("\\n", "")
                            # print(temp_exact_table)
                            # print("$$$$$$$$$$$$$$$$")
                            if all(t in temp_exact_table for t in t_value):
                                biaoge_str, biaoge_df = exact_table([t_name], page_num, tables, page)
                                # print(f"==========================={biaoge}==============================")
                                if biaoge_str:
                                    page_list.append(page_num)
                                    biaoges.extend(biaoge_str)
                                    biaoges_df.extend(biaoge_df)
                    if biaoges and not biaoge_str:
                        print(f"biaoges[-1]{biaoges[-1]}exact_tables[0][0]{exact_tables[0][0]}biaoges[0]{biaoges[0]}")

                        if len(json.loads(biaoges[-1])["name"]) == len(exact_tables[0][0]) or len(json.loads(biaoges[0])["name"]) == 2:
                    # elif exact_tables and any(d['num'] == page_num-1 for d in tables):
                            biaoge,biaoge_df = exact_table("", page_num, tables, page)
                            if biaoge:
                                page_list.append(page_num)
                                biaoges.extend(biaoge)
                                ###df格式 如果后期需要 df格式继续修改，暂时有错
                                # df_columns = pd.DataFrame([biaoge_df[0].columns],columns=biaoges_df[-1].columns)
                                # biaoges_df[-1] = pd.concat([biaoges_df[-1],df_columns],ignore_index=True)

                                # biaoge_df[0].columns = biaoges_df[-1].columns
                                # biaoges_df[-1] = pd.concat([biaoges_df[-1],biaoge_df[0]],ignore_index=True)
                                ######
                        # biaoges_df[-1].extend(biaoge_df[0])
            # elif exact_tables and table_content:
            #     # print(".........................................")
            #     # lists = ["杆塔型式","呼高","全高"]
            #     table_content_json = json.loads(table_content)
            #     for t_name,t_value in table_content_json.items():
            #         temp_exact_table = str(exact_tables).replace("\n","").replace("\\n","")
            #         print(temp_exact_table)
            #         if all(t in temp_exact_table for t in t_value):
            #             biaoge,biaoge_df = exact_table([t_name], page_num, tables, page, table_name=[t_name])
            #             # print(f"==========================={biaoge}==============================")
            #             if biaoge:
            #                 page_list.append(page_num)
            #                 biaoges.extend(biaoge)
            #                 biaoges_df.extend(biaoge_df)
            except:
                continue
            
        return biaoges,biaoges_df,fujians,fujians_df,page_list


def extract_table_from_one_page(url):
    res = requests.get(url)
    pdf_file = BytesIO(res.content)
    # 提取PDF文本
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages"):
            # print(f"正在处理第 {page_num} 页...")
            text = page.extract_text()
            table = page.extract_tables()
            df_result = pd.DataFrame(table[0][1:], columns=table[0][0])
            df_result.columns = df_result.columns.str.replace('\n', '', regex=False)
            return df_result

# def deal_match(s, lst):
#     order= {}
#     result = []
#     for idx, chars in enumerate(s):
#         # if chars not in order_map:
#         seen[chars] = idx
#     # filtered_sort =  sorted(
#     #     (x for x in lst if x in order_map),
#     #     key = lambda x: order_map[x]
#     # )
#     #     seen[item] = idx
#     for idx, item in enumerate(s):
#         if seen[item] == idx:
#             result.append(item)
#     return result

def group_by_table(data):
    result=[]
    names = []
    i=0
    while i <len(data):
        item = data[i]
        if isinstance(item, str) and item not in result:
            name = item 
            names.append(item)
            group=[item]
            i +=1
            while i< len(data) and (not isinstance(data[i], str) or data[i]==name):
                if not isinstance(data[i], str):
                    group.append(data[i])
                else:
                    names.append(data[i])
                i +=1
            result.append(group)
        else:
            i+=1
    return result,names

def group_by_table_new(data):
    result=[]
    names = []
    pages = []
    i=0
    while i <len(data):
        item = json.loads(data[i])
        if isinstance(item["name"], str) and item["name"] not in result:
            name = item["name"]
            names.append(item["name"])
            group=[item["name"]]
            page = [item["page"]]
            i +=1
            item = json.loads(data[i])
            while i< len(data) and (not isinstance(item["name"], str) or item["name"]==name):
                if not isinstance(item["name"], str):
                    group.append(item["name"])

                else:
                    page.append(item["page"])
                    names.append(item["name"])
                i +=1
                if i <len(data):
                    item = json.loads(data[i])
            result.append(group)
            pages.append(page)
        else:
            i+=1
    return result,pages


def extract_tables_from_pdf_tujian(url,table_name):
    """
    按照自定义标题类型切分PDF文档提取表格、附件。
    入参：
        pdf_path: str PDF文件路径
        table_name: str 表格名称
    返回：
        biaoges: list[list] 表格列表格式结果
        biaoges_df: list[Dataframe] 表格df格式结果
        fujians: list[list] 附件列表格式结果
        fujians_df: list[Dataframe] 附件df格式结果
    """
    tu_patterns = {
        2: r"\n表\s\d..+?\n",
        3: r".+?\s表\d",
        4: r".+?表\n"
    }
    fujian_patterns = {
        1: r"附件\s\d\s.+\n",
        2: r".+?附件\n",
    }
    tables = []
    biaoges = []
    biaoges_df = []
    fujian_lists = []
    fujians = []
    fujians_df = []
    page_list = []

    res = requests.get(url)
    pdf_file = BytesIO(res.content)
    # pdf_file = url
    # 提取PDF文本
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages"):
            # print(f"正在处理第 {page_num} 页...")
            text = page.extract_text()
            exact_tables = page.extract_tables()
            table_matchs = []
            fujian_matchs = []
            for num,pattern in tu_patterns.items():
                table_match = re.findall(pattern, text)
                table_match = [item.replace('\n', '') for item in table_match if '见表' not in item and len(item) < 30]
                if table_match:
                    table_matchs.extend(table_match)
            cleaned_data = [s.replace(' ','') for s in table_matchs]
            table_matchs = deal_match(text.replace(' ',''),cleaned_data)
            res = []
            for ta in table_matchs:
                if ta not in res:
                    res.append(ta)
            for num_fujian,pattern_fujian in fujian_patterns.items():
                # fujian_match = re.findall(pattern_fujian, text,re.DOTALL)
                fujian_match = re.findall(pattern_fujian, text)

                fujian_matchs.extend(fujian_match)
            try:
                if table_matchs:
                    biaoge,biaoge_df = exact_table(table_matchs, page_num, tables, page, table_name=table_name)
                    if biaoge:
                        page_list.append(page_num)
                        biaoges.extend(biaoge)
                        biaoges_df.extend(biaoge_df)
                    # break
                elif fujian_matchs:

                    fujian,fujian_df = exact_table(fujian_matchs, page_num, fujian_lists, page, table_name=table_name)
                    if fujian:
                        page_list.append(page_num)
                        fujians.extend(fujian)
                        fujians_df.extend(fujian_df)
                # if page_num == 177:
                #
                #     print(f"xxxxxxxxxxxxxxx{len(biaoges[0])}")
                elif exact_tables and biaoges:

                    if len(biaoges[1]) == len(exact_tables[0][0]) or len(biaoges) == 2:
                # elif exact_tables and any(d['num'] == page_num-1 for d in tables):
                        biaoge,biaoge_df = exact_table("", page_num, tables, page, table_name=table_name)
                        if biaoge:
                            page_list.append(page_num)
                            biaoges.extend(biaoge)
                            # 表头在上一页 表格数据下一页情况 还需继续验证
                            if biaoges_df[-1].values.size == 0:
                                biaoges_df = biaoge_df
                            else:
                                df_columns = pd.DataFrame([biaoge_df[0].columns], columns=biaoges_df[-1].columns)
                                biaoges_df[-1] = pd.concat([biaoges_df[-1], df_columns], ignore_index=True)

                                biaoge_df[0].columns = biaoges_df[-1].columns
                                biaoges_df[-1] = pd.concat([biaoges_df[-1], biaoge_df[0]], ignore_index=True)
                                # biaoges_df[-1].extend(biaoge_df[0])
            except:
                continue
        return biaoges,biaoges_df,fujians,fujians_df,page_list


def convert_to_markdown(table_data):
    # 提取表头
    headers = table_data[0]

    # 创建 Markdown 表格的分隔符行（默认左对齐）
    separator = ["---"] * len(headers)

    # 构建 Markdown 表格
    markdown_table = []
    markdown_table.append("| " + " | ".join(headers) + " |")  # 表头
    markdown_table.append("| " + " | ".join(separator) + " |")  # 分隔符

    # 添加数据行
    for row in table_data[1:]:
        row_t = [str(item) if item is not None else "" for item in row]
        markdown_table.append("| " + " | ".join(row_t).replace("\n", "<br>") + " |")  # 换行符替换为 <br>

    # 将列表拼接为字符串并返回
    return "\n".join(markdown_table)


## 处理合并表格单元格
# #OCR 提取无边框表格
# import pdfplumber
# from PIL import Image
# import pytesseract
#
#
# def extract_table_with_ocr(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf.pages, start=1):
#             print(f"正在处理第 {page_num} 页...")
#
#             # 将页面转换为图片
#             image = page.to_image(resolution=300).original
#
#             # 使用 OCR 提取文本
#             text = pytesseract.image_to_string(image)
#             print(f"OCR 提取的文本内容：\n{text}")
#
#             # 如果需要进一步解析表格，可以自行实现逻辑
#             # 例如按行分割文本并处理



#检测表格并保存csv

def save_tables_to_csv(pdf_path, output_folder):
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if tables:
                for table_num, table in enumerate(tables, start=1):
                    # 定义输出文件路径
                    output_file = f"{output_folder}/page_{page_num}_table_{table_num}.csv"

                    # 写入 CSV 文件
                    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerows(table)

                    print(f"已保存表格到 {output_file}")
            else:
                print(f"第 {page_num} 页未检测到表格。")

# # 检测提取图片

def extract_images_from_pdf(pdf_path, output_folder):
    """
    检测某页是否包含输入关键词
    入参：
        pdf_path: str PDF文件路径
        keywords: list 关键字列表
    返回：
        pages：list 关键词页码
    """
    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, start=1):
            print(f"正在处理第 {page_num} 页...")
            text = page.extract_text()

            table_matchs = re.findall(r"图\s\d.+\n", text)
            table_match = [item.replace("\n", "") for item in table_matchs if len(item.replace("\n", ""))>14]
            if table_match:
                # 获取当前页的所有图片
                images = page.images

                if images:
                    for img_num, img in enumerate(images):
                        # 提取图片数据
                        x0, y0, x1, y1 = img["x0"], img["y0"], img["x1"], img["y1"]
                        width, height = img["width"], img["height"]
                        image_data = img["stream"].get_data()

                        # 将图片数据转换为 PIL 图像对象
                        image = Image.open(BytesIO(image_data))

                        # 保存图片到文件
                        output_file = f"{output_folder}/page_{page_num}_{table_match[img_num]}.png"
                        image.save(output_file)
                        print(f"已提取图片并保存到 {output_file}")
                else:
                    if len(table_match) ==1 and len(table_match[0])>14:
                        doc = fitz.open(pdf_path)
                        page = doc[page_num-1]
                        # 设置截图区域（这里设置为整个页面）
                        rect = page.rect
                        clip = fitz.Rect(rect.x0, rect.y0 + 50, rect.x1, rect.y1 - 70)
                        # 获取截图
                        pix = page.get_pixmap(clip=clip)
                        # 保存截图
                        output_file = f"{output_folder}/page22_{page_num}_{table_match[0]}.png"
                        pix.save(output_file)
                        print(f"第 {page_num} 页截图非嵌入式图片。")


# 检测某页图片
def extract_images_from_page(pdf_path, page, output_folder):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page]
        page_num = page
        print(f"正在处理第 {page_num} 页...")
        text = page.extract_text()

        table_matchs = re.findall(r"图\s\d.+\n", text)
        table_match = [item.replace("\n", "") for item in table_matchs]
        # 获取当前页的所有图片
        images = page.images

        if images:
            for img_num, img in enumerate(images, start=1):
                # 提取图片数据
                x0, y0, x1, y1 = img["x0"], img["y0"], img["x1"], img["y1"]
                width, height = img["width"], img["height"]
                image_data = img["stream"].get_data()

                # 将图片数据转换为 PIL 图像对象
                image = Image.open(BytesIO(image_data))

                # 保存图片到文件
                output_file = f"{output_folder}/{table_match[img_num]}.png"
                image.save(output_file)
                print(f"已提取图片并保存到 {output_file}")
        else:
            print(f"第 {page_num} 页未检测到嵌入式图片。")

def process_headers(data):
    # 片段添加一二级标题
    # 当前生效的标题（用于当前条目）
    current_chapter = ""  # 如 "第 1 章 总的部分"
    current_section = ""  # 如 "1.3 aaaaaa"

    # 待生效的标题（在当前条目中发现，但延迟到下一条生效）
    pending_chapter = ""
    pending_section = ""

    # 正则：匹配“第 x 章 xxx”（允许空格）
    # chapter_pattern = re.compile(r'第\s*\d+\s*章\s+[^\d\n].*?(?=\s*\d+\.\d+\.\d+|\s*$|\.?\n|$)')
    chapter_pattern = re.compile(r'第\s*\d+\s*章\s+[^ \n\r]+')
    # 正则：匹配“x.x 标题名”（不是 x.x.x 的一部分）
    # section_pattern = re.compile(r'(?<!\.)\b(\d+\.\d+)\s+[^\d\n].*?(?=\s*\d+\.\d+\.\d+|\s*$|\.?\n|$)')
    section_pattern = re.compile(r'\s+\d+\.\d+\s[\u4e00-\u9fa5]+')

    # 正则：匹配子节开头，如 1.3.1
    subsection_pattern = re.compile(r'^\s*\d+\.\d+\.\d+')

    result = []

    for item in data:
        content = item['content']
        page = item['page']

        # ===== 1. 提取当前条目中的新章节和新分节 =====
        chapter_match = chapter_pattern.search(content)
        if chapter_match:

            pending_chapter = re.sub(r'\s+', ' ', chapter_match.group().strip())  # 规范化空格

        section_match = section_pattern.search(content)
        try:
            if section_match:
                section_match = section_match[-1]
                section_match_temp = section_match.strip().split(' ')
                section_match = f"{section_match_temp[0]} {section_match_temp[1]}"
                section_first = int(section_match_temp[0].split('.')[0])
                section_second = int(section_match_temp[0].split('.')[1])

                if section_first<=25 and section_second<=25 and len(str(section_second))<=2:
                    pending_section = re.sub(r'\s+', ' ', section_match)
        except:
            pass
        # ===== 2. 构造当前应使用的前缀 =====
        prefix = ""
        if current_chapter:
            prefix += current_chapter
            if current_section and current_section not in prefix:
                prefix += " " + current_section
        elif current_section and not prefix:
            prefix += current_section

        # ===== 3. 判断是否需要添加前缀 =====
        stripped = content.strip()
        starts_with_subsection = bool(subsection_pattern.match(stripped))

        new_content = content
        if prefix and starts_with_subsection:
            # 如果内容不以 prefix 开头，则添加
            if not stripped.startswith(prefix):
                new_content = prefix + " " + stripped
            # 否则保持原样（已包含）

        result.append({'content': new_content.replace('\n',''), 'page': page})
        # result.append({'content': new_content, 'page': page})

        # ===== 4. 当前条目处理完后，更新 current 标题（延迟生效）=====
        if pending_chapter:
            current_chapter = pending_chapter
            pending_chapter = ""
        if pending_section:
            current_section = pending_section
            pending_section = ""

    return result


# 标题划分段落
def process_list(data):
    """
    处理一个包含多个字典的列表：
    如果某个字典的 'content' 值为空，则用下一个字典的 'content' 值替换，
    并移除下一个字典，直到遇到 'content' 不为空的字典为止。

    :param data: list[dict] - 包含多个字典的列表
    :return: list[dict] - 处理后的列表
    """
    i = 0
    while i < len(data) - 1:  # 遍历列表，注意索引不要越界
        if not data[i].get("content"):  # 检查当前字典的 content 是否为空
            # 找到下一个 content 不为空的字典
            j = i + 1
            k = j + 1
            page_list=[data[i].get("page")]
            content = []
            while j < len(data) and not data[j].get("content") and not data[k].get("content"):
                # if :
                    page_list.append(data[j].get("page"))
                    content.append(f'{data[j].get("title")}\n')
                    j += 1
                    k += 1

            if j < len(data):  # 如果找到有效的 content
                next_content = data[j].get("content")
                content.append(data[j].get("title"))
                next_content.insert(0, ''.join(content))
                page_list.append(data[j].get("page"))
                page = list(set(page_list))
                data[i]["content"] = next_content  # 替换当前字典的 content
                data[i]["page"] = page  # 替换当前字典的 content

                del data[i + 1:j + 1]  # 删除从 i+1 到 j 的所有字典
            else:
                # 如果后续没有有效的 content，直接退出循环
                break
        i += 1  # 移动到下一个字典
    texts = []
    for con in data:
        if isinstance(con["page"],list):
            page_nums=con["page"]
        else:
            page_nums=[con["page"]]

        res = {
            "content":f'{con["title"]}\n{" ".join(con["content"])}\n',
            "page": page_nums
        }
        texts.append(res)

    return data,texts

# 示例调用
def process_table1(data):
    """
    处理一个包含多个长度相同的列表的主列表：
    如果某个子列表的第一个值为空，则赋值为上一个子列表的第一个值。

    :param data: list[list] - 主列表，其中每个子列表长度为3
    :return: list[list] - 处理后的主列表
    """
    k = 1
    if data[1][0].replace('\n','') == "序号":
        k = 2
    # 遍历主列表
    for i in range(1, len(data)): # 从索引1开始，因为需要参考前一个子列表
        for j in range(k):
            if data[i][j] == None:  # 检查当前子列表的第一个值是否为空
                data[i][j] = data[i - 1][j]  # 赋值为上一个子列表的第一个值

    return data
if __name__ == '__main__':
    pdf_path = "D:\代码\代码\docling\docling-main\docling-main\jingyanyuan\data\山东青岛平度卢乡（化工）110kV输变电工程-支撑文件/12 勘察资料/12.岩土工程勘察报告书(线路部分).pdf"  # 输入PDF文件路径
    main_target_text = "主变"
    other_target_text = "容量"
    list2 = [['工程概况', '电压等级', '500/220/35'],
[None, '主变台数及容量（MVA）', '4/1×1000'],
[None, '出线规模（高/中）', '高：10/5；中：16/10'],
[None, '变电站类型（地上/地下；户内/户外/半户内）', '地上；半户内'],
[None, '配电装置类型A：GIS；B：HGIS；C：瓷柱式；D：罐式', 'A：GIS'],
['设计\n方案选择', '通用设计编号', '500-A3-1\n500-B1-3'],
['配电\n装置设计', '500kV（高压侧）配电装置模块编号', '500-A3-1-500'],
[None, '220kV（中压侧）配电装置模块编号', '500-A3-1-220'],
[None, '主变及35kV（低压侧）配电装置模块编号', '500-B1-3-35'],
['总平面\n设计', 'A：直接采用通用设计方案；\nB：合理采用模块拼接；\nC：未采用通用设计方案、模块。', 'B'],
['二次\n系统设计', '控制、保护是否满足二次系统通用设计配置要求（A.\n是；B.否）。A1：不设置独立“五防”工作站；A2：\n设立独立“五防”终端，数据与监控系统共享；A3：\n设立独立“五防”系统。', 'A，A1'],
['土建设计', '围墙内占地面积（hm2）\n（A：不高于同规模通用设计方案；B：高于同规模通\n用设计方案）', 'B'],
[None, '总建筑面积（m2）\n（A：不高于同规模通用设计方案；B：高于同规模通\n用设计方案）', 'B'],
['通用设备', '主变压器设备编号', '5T-DS-2B/334'],
[None, '并联电容器设备编号', 'BC-K-60'],
[None, '并联电抗器设备编号', 'BL-0F3-60'],
[None, '500kV（高压侧）GIS设备编号', '5GIS-5000/63'],
[None, '500kV避雷器设备编号', '5MOA-420/1046\n5MOA-444/1106'],
[None, '220kV（中压侧）GIS设备编号', '2GIS-5000/50'],
[None, '220kV避雷器设备编号', '2MOA-204/532'],
    ]
    list1 = [{'level': 5,'page': 1, 'title': '（2）站内外排水系统，站内给水系统。', 'content': []},
             {'level': 5, 'page': 2,'title': '（3）进站道路及进站道路中的桥涵洞。', 'content': []},
             {'level': 5, 'page': 3,'title': '（4）系统继电保护、通信及远动的站内部分。', 'content': []},
             {'level': 5, 'page': 4,'title': '（5）地质、测量、水文气象。', 'content': ["667788"]},
             {'level': 5, 'page': 4,'title': '（6）外接站用电源。', 'content': []},
             {'level': 5,'page': 4, 'title': '（7）工程概预算部分。', 'content': []},
             {'level': 3,'page': 4, 'title': '1.2.3 附属工程', 'content': []},
             {'level': 4,'page': 4, 'title': '1.2.3.1 外接站用电源', 'content': ['根据变电站所在区域电网建设情况，峡山500kV变电站外接电源引自', '110kV北园变电站10kVⅡ段母线037待用二十四间隔，采用1回专线方式供电。', '110kV北园变电站两路电源进线，分别接入220kV恒祥站和220kV昌邑站，作为', '本站外引电源专线安全可靠。', '10kV外引电源线路路径长度约6.96公里。其中架空段线路长度约1.05公', '里，采用架空绝缘导线JKLGYJ-150/25；电缆段线路长度约5.91公里，采用', 'ZC-YJV22-8.7/15-3×120型电缆。站内采用10kV干式无励磁调压箱式变电站。']},
             {'level': 4, 'page': 5,'title': '1.2.3.2 临时施工电源', 'content': ['本站临时施工电源由站址附近10kV瓦城线王家庄子支线#34杆处T接并引', '接至本站，线路长度1.3km，架空段线路长度1.05公里，采用JKLGYJ-10-95/15', '型绝缘导线；电缆段线路长度0.25公里，采用ZR-YJV22-8.7/15-3×70型电缆。']},
             {'level': 2, 'page': 5,'title': '1.3 站址概况', 'content': []}]
    # from ces import group_by_table_new
    # page_number = find_text_in_pdf(pdf_path, main_target_text,other_target_text)
    # page_table = extract_tables_from_pdf(pdf_path,table_name="地基土主要物理力学指标及地基承载力特征值")
#17 18
    url = "http://25.41.21.113/szjy/jinqu/2025-03-07/5524e50573d44cbd9ecda52b2ef2b9e6.pdf"
    # url = "http://25.41.21.113/szjy/jinqu/2024-03-18/4954508064bb4e43acd4ce3379e50abe.pdf"
    # url = "D:\代码\代码\线路结构api\point\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/03 线路电缆/02 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（电缆部分）/01 说明书及材料清册\唐田～灰埠（唐灰甲线）T接卢乡（化工）站110kV线路工程 主要设备材料清册0307.pdf"
    results = extract_tables_from_pdf(url,'{"杆塔一览表":["杆塔型式","呼高","全高"],"短路电流计算结果表":["短路电流","冲击电流"]}')
    # xx = process_table1(results[0])
    x1,page = group_by_table_new(results[0])
    x2,pag2 = group_by_table_new(results[2])
    con = [f"title:1111\n电压等级：110\ndoc_id:a213212\npage:{page[i]}\ncontent:{table}" for i,table in enumerate(x1)]

    # xx=results[0]
    print(f"**************************{x1}")
    # print(results[0])
    # print_table = convert_to_markdown(list)
    # print(print_table)
    # output_folder = "extracted_images"
    # b,contents = process_list(list1)
    # print(contents)
    #
    # images = extract_images_from_pdf(pdf_path,output_folder)
    # images = extract_images_from_page(pdf_path, 46, output_folder)
    # pdf_path="data\山东青岛平度卢乡（化工）110kV输变电工程-支撑文件/12 勘察资料/12.岩土工程勘察报告书(线路部分).pdf"
    # page_number = find_text_in_page_pdf(pdf_path, "12.岩土工程勘察报告书(线路部分)",[0,1], ["详勘阶段","施工图阶段","(详勘)阶段","(施工图)阶段"],["可研阶段","初设阶段","(可研)阶段","(初设)阶段"])
    # point4_1 = find_text_in_pdf()
    # b = extract_table_from_page("D:\代码\代码\docling\docling-main\docling-main\jingyanyuan\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/01 山东青岛平度卢乡（化工）灰埠变110kV保护改造工程/01 说明书\变电部分初步设计说明书.pdf")