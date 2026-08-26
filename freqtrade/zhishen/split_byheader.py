# -*- coding: utf-8 -*-

import pdfplumber
import re
from tqdm import tqdm
import requests
from io import BytesIO
import pymupdf
from pdfreader_new_ceshi import *




def split_pdf_by_all_headers_pypdf(url):
    header_patterns = [
        # (r"^\d+\)", 6),  # 1) -> 一级标题
        (r"^（\d+）.+", 5),  # （1）-> 二级标题
        # (r"^\(\d+\)", 5),  # （1）-> 二级标题
        (r"^\d+\.\d+\.\d+\.\d+\s.+", 4),  # 1.1.1.1 -> 四级标题
        (r"^\d+\.\d+\.\d+\s.+", 3),  # 1.1.1 -> 三级标题
        (r"^\d+\.\d+\s.+", 2),  # 1.1 -> 二级标题
        (r"^\d+\s.+", 1),  # 1 -> 一级标题
    ]

    # 初始化变量
    sections = []
    current_section = None
    # 将 PDF 转换为图像（每页一张图）
    # doc = pymupdf.open(url)
    with pymupdf.open(url) as doc:# 打开 PDF 文档
    # page = doc[5]
    # tp1 = page.get_textpage_ocr()
    # text1 = page.get_text(textpage=tp1)
        for page_num, page in tqdm(enumerate(doc, start=1), total=len(doc), desc="Processing pages sections"):  # 遍历文档页面
            tp = page.get_textpage_ocr()
            text = page.get_text(textpage=tp)
            if not text or "........................" in text:
                continue

            # 遍历每一行文本
            for line in text.splitlines():
                line = line.strip()

                # 判断是否为标题
                is_header = False
                for pattern, level in header_patterns:
                    match = re.match(pattern, line)
                    if match:
                        if match:
                            if level == 2 or level == 1 and len(match.group()) > 25:
                                continue
                        # 如果匹配到标题，保存当前段落并开始新段落
                        if current_section:
                            sections.append(current_section)
                        title = line.strip()
                        current_section = {
                            "level": level,
                            "title": title,
                            "page": page_num,
                            "content": []
                        }
                        is_header = True
                        break

                if not is_header and current_section:
                    # 如果不是标题，则添加到当前段落的内容中
                    # 如果不是标题，则添加到当前段落的内容中
                    data_temp = line.strip()
                    data = re.sub(r'·\d+·', '', data_temp)
                    current_section["content"].append(data)
        print("xxxxx")
        # tp1 = page.get_table_ocr()l
        # table = page.find_tables(tablepage=tp1)
        # text = page.get_text().encode("utf8")
    # image = Image.open(url)
    # text = pytesseract.image_to_string(image)
    # 保存最后一个段落
    if current_section:
        sections.append(current_section)
    text, contents = process_list(sections)
    return contents


def split_pdf_by_all_headers(url):
    """
    按照自定义标题类型切分PDF文档。
    参数：
        pdf_path: PDF文件路径
    返回：
        contents: 切分后的段落内容
    """
    # 定义标题类型的正则表达式及其对应的层级
    header_patterns = [
        # (r"^\d+\)", 6),  # 1) -> 一级标题
        # (r"^（\d+）.+", 5),  # （1）-> 二级标题
        # (r"^\(\d+\)", 5),  # （1）-> 二级标题
        (r"^\d+\.\d+\.\d+\.\d+\s.+", 4),  # 1.1.1.1 -> 四级标题
        (r"^\d+\.\d+\.\d+\s.+", 3),  # 1.1.1 -> 三级标题
        (r"^\d+\.\d+\s.+", 2),  # 1.1 -> 二级标题
        # (r"^\d+\s.+", 1),  # 1 -> 一级标题
    ]

    # 初始化变量
    sections = []
    current_section = None
    res = requests.get(url)
    pdf_file = BytesIO(res.content)
    # 提取PDF文本
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages sections"):
            text = page.extract_text()
            if not text or "........................" in text:
                continue

            # 遍历每一行文本
            for line in text.splitlines():
                line = line.strip()

                # 判断是否为标题
                is_header = False
                for pattern, level in header_patterns:
                    match = re.match(pattern, line)
                    if match:
                        if match:
                            if (level == 2 or level) == 1 and len(match.group()) > 25:
                                continue
                        # 如果匹配到标题，保存当前段落并开始新段落
                        if current_section:
                            sections.append(current_section)
                        title = line.strip()
                        current_section = {
                            "level": level,
                            "title": title,
                            "page": page_num,
                            "content": []
                        }
                        is_header = True
                        break

                if not is_header and current_section:
                    # 如果不是标题，则添加到当前段落的内容中
                    # 如果不是标题，则添加到当前段落的内容中
                    data_temp = line.strip()
                    data = re.sub(r'·\d+·', '', data_temp)
                    current_section["content"].append(data)
                    # print(current_section)

    # 保存最后一个段落
    if current_section:
        sections.append(current_section)
    text,contents = process_list(sections)
    return contents

def split_pdf_by_one_headers(url):
    """
    按照自定义标题类型切分PDF文档。
    参数：
        pdf_path: PDF文件路径
    返回：
        contents: 切分后的章节内容
    """
    # 定义标题类型的正则表达式及其对应的层级
    header_patterns = [
        # (r"^\d+\)", 6),  # 1) -> 一级标题
        # (r"^（\d+）", 5),  # （1）-> 二级标题
        # (r"^\(\d+\)", 5),  # （1）-> 二级标题
        # (r"^\d+\.\d+\.\d+\.\d+\s", 4),  # 1.1.1.1 -> 四级标题
        # (r"^\d+\.\d+\.\d+\s", 3),  # 1.1.1 -> 三级标题
        (r"^\d+\.\d+\s[\u4e00-\u9fa5]+", 2),  # 1.1 -> 二级标题
        (r"^\d+\s[\u4e00-\u9fa5]+", 1),  # 1 -> 一级标题
    ]

    # 初始化变量
    sections = []
    current_section = None
    res = requests.get(url)
    pdf_file = BytesIO(res.content)
    # 提取PDF文本
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages sections"):
            text = page.extract_text()
            if not text or "........................" in text:
                continue

            # 遍历每一行文本
            for line in text.splitlines():
                line = line.strip()

                # 判断是否为标题
                is_header = False
                for pattern, level in header_patterns:
                    match = re.match(pattern, line)
                    if match:
                        # 如果匹配到标题，保存当前段落并开始新段落
                        if current_section:
                            sections.append(current_section)
                        title = line.strip()
                        current_section = {
                            "level": level,
                            "title": title,
                            "page":page_num,
                            "content": []
                        }
                        is_header = True
                        break

                if not is_header and current_section:
                    # 如果不是标题，则添加到当前段落的内容中
                    # 如果不是标题，则添加到当前段落的内容中
                    data_temp = line.strip()
                    data = re.sub(r'·\d+·', '', data_temp)
                    current_section["content"].append(data)
                    # print(current_section)

    # 保存最后一个段落
    if current_section:
        sections.append(current_section)
    text,contents = process_list(sections)
    return contents

# def split_pdf_by_custom_headers1(pdf_path):
#     """
#     按照自定义标题类型切分PDF文档。
#     :param pdf_path: PDF文件路径
#     """
#     # 定义标题类型的正则表达式及其对应的层级
#     header_patterns = [
#         (r"^\d+\)", 6),  # 1) -> 一级标题
#         (r"^（\d+）", 5),  # （1）-> 二级标题
#         # (r"^\(\d+\)", 5),  # （1）-> 二级标题
#         (r"^\d+\.\d+\.\d+\.\d+\s", 4),  # 1.1.1.1 -> 四级标题
#         (r"^\d+\.\d+\.\d+\s", 3),  # 1.1.1 -> 三级标题
#         (r"^\d+\.\d+\s", 2),  # 1.1 -> 二级标题
#         (r"^\d+\s", 1),  # 1 -> 一级标题
#     ]
#
#     # 初始化变量
#     sections = []
#     current_section = None
#
#     # 提取PDF文本
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text()
#             if not text:
#                 continue
#
#             # 遍历每一行文本
#             for line in text.splitlines():
#                 line = line.strip()
#
#                 # 判断是否为标题
#                 is_header = False
#                 for pattern, level in header_patterns:
#                     match = re.match(pattern, line)
#                     if match:
#                         # 如果匹配到标题，保存当前段落并开始新段落
#                         if current_section:
#                             sections.append(current_section)
#
#                         title = line.strip()
#                         current_section = {
#                             "level": level,
#                             "title": title,
#                             "content": []
#                         }
#                         is_header = True
#                         break
#
#                 if not is_header and current_section:
#                     # 如果不是标题，则添加到当前段落的内容中
#                     current_section["content"].append(line.strip())
#                 if is_header:
#                     if len(sections) > 1 and len(sections[-1]["content"]) == 0:
#                         sections[-1]["content"].append(current_section["title"])
#                         sections[-1]["content"].append(current_section["content"])
#
#     # 保存最后一个段落
#     if current_section:
#         sections.append(current_section)
#
#     return sections


#关键词提取页码
def find_text_in_pdf(pdf_path, main_target_text):
    # 定义标题类型的正则表达式及其对应的层级
    header_patterns = [
        (r"^\d+\)", 6),  # 1) -> 一级标题
        (r"^（\d+）", 5),  # （1）-> 二级标题
        # (r"^\(\d+\)", 5),  # （1）-> 二级标题
        (r"^\d+\.\d+\.\d+\.\d+\s", 4),  # 1.1.1.1 -> 四级标题
        (r"^\d+\.\d+\.\d+\s", 3),  # 1.1.1 -> 三级标题
        (r"^\d+\.\d+\s", 2),  # 1.1 -> 二级标题
        (r"^\d+\s", 1),  # 1 -> 一级标题
    ]

    # 初始化变量
    sections = []
    current_section = None
    pages = []
    results = []

    with (pdfplumber.open(pdf_path) as pdf):
        for page_num, page in tqdm(enumerate(pdf.pages, start=1), total=len(pdf.pages), desc="Processing pages"):  # 从第1页开始计数
            text = page.extract_text()  # 提取当前页的文本
            if "........................"in text:
                continue
            else:
                for key_word in main_target_text:
                    if type(key_word)==str and key_word in text:  # 检查目标文本是否在当前页
                        # 遍历每一行文本
                        for line in text.splitlines():
                            line = line.strip()

                            # 判断是否为标题
                            is_header = False
                            for pattern, level in header_patterns:
                                match = re.match(pattern, line)
                                if match:
                                    # 如果匹配到标题，保存当前段落并开始新段落
                                    if current_section:
                                        sections.append(current_section)
                                    title = line.strip()
                                    current_section = {
                                        "level": level,
                                        "title": title,
                                        "content": []
                                    }
                                    is_header = True
                                    break

                            if not is_header and current_section:
                                # 如果不是标题，则添加到当前段落的内容中
                                data_temp = line.strip()
                                data = re.sub(r'.\d+.', '', data_temp)
                                current_section["content"].append(data)
                                # print(current_section)
                        print(f"\n提取结果为: \n{current_section['title']}\n{current_section['content'][:-1]}")
                        # print(f"目标文本 '{main_target_text}' 和'{other_target_text}' 位于第 {page_num} 页。")
                        results.append(f"{current_section['title']}\n{','.join(current_section['content'][:-1])}")
                        pages.append(page_num)
                    elif type(key_word)==list and all(keyword in text for keyword in key_word):  # 检查目标文本是否在当前页
                        # 遍历每一行文本
                        print("xxxxx")
                        for line in text.splitlines():
                            line = line.strip()

                            # 判断是否为标题
                            is_header = False
                            for pattern, level in header_patterns:
                                match = re.match(pattern, line)
                                if match:
                                    # 如果匹配到标题，保存当前段落并开始新段落
                                    if current_section:
                                        sections.append(current_section)
                                    title = line.strip()
                                    current_section = {
                                        "level": level,
                                        "title": title,
                                        "content": []
                                    }
                                    is_header = True
                                    break

                            if not is_header and current_section:
                                # 如果不是标题，则添加到当前段落的内容中
                                data_temp = line.strip()
                                data = re.sub(r'.\d+.', '', data_temp)
                                current_section["content"].append(data)
                                # print(current_section)
                        print(f"\n提取结果为: \n{current_section['title']}\n{current_section['content'][:-1]}")
                        # print(f"目标文本 '{main_target_text}' 和'{other_target_text}' 位于第 {page_num} 页。")
                        results.append(f"{current_section['title']}\n{','.join(current_section['content'][:-1])}")
                        pages.append(page_num)

    if len(pages) > 0:
        return pages,results
    else:
        return '未找到目标文本'  # 如果未找到目标文本，返回 None



# 示例调用
if __name__ == '__main__':
    pdf_path = "F:\python\point15\data\山东青岛平度卢乡（化工）110kV输变电工程-支撑文件/12 勘察资料/12.岩土工程勘察报告书(线路部分).pdf"  # 输入PDF文件路径
    # pdf_path = "D:\代码\代码\docling\docling-main\docling-main\jingyanyuan\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/01 说明书及材料清册\DW10218SC-A-01设计说明书.pdf"  # 替换为你的PDF文件路径
    point_4 = {
        "地下水的腐蚀性": {"content": [], "page": []},
        "场地土的腐蚀性": {"content": [], "page": []},
        "不良地质作用": {"content": [], "page": []},
        "地震液化": {"content": [], "page": []},
        "饱和单轴抗压强度": {"content": [], "page": []},
        "主要地质情况概述": {"content": [], "page": []},
        "地质参数": {"content": [], "page": []},

    }
    url = "http://25.41.21.113/zhdlqx/file/5a5b40f535b24962a45e04da63418055.pdf"
    sections1 = split_pdf_by_all_headers(url)
    sections = process_headers(sections1) 
    # url1 = "F:\python\point15\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/03 线路电缆/02 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（电缆部分）/01 说明书及材料清册\唐田～灰埠（唐灰甲线）T接卢乡（化工）站110kV线路工程 主要设备材料清册0307.pdf"
    # table_result = extract_tables_from_pdf(pdf_path, ["杆塔一览表"],'{"杆塔一览表":["杆塔型式","呼高","全高"],"短路电流计算结果表":["短路电流","冲击电流"]}')
    # table1,page1 = group_by_table_new(table_result[0])
    # table2,page2 = group_by_table_new(table_result[2])
    # temp_content1 = [f"title:11111\n电压等级：110\ndoc_id:21232\npage:{page1[i]}\ncontent:{table}" for i,table in enumerate(table1)]
    # print(section["content"])
    # print(f"xxxxxxx{temp_content1[0]}")
    res = []
    for section in sections:
        if "设备机房和布置" in section["content"]:
            res.append(section)
    print(res)
    
    # # text = find_text_in_pdf(pdf_path,['电缆线路路径'])
    # # print("xxxxx")
    # sections = split_pdf_by_one_headers(pdf_path)
    # # print(sections)
    # for section in sections:
    #     # if re.findall("^\d+\.\d+\s电缆线路路径",section["ceontnt"]):
    #     #     print(section)
    #     #     print("-------------------")

    # #     # if '电缆线路路径' in section:
    # #     #     # if "........................" not in section:
    # #     #     print(section)
    # #         print("-------------------")
    #     if "勘测任务" not in section["content"]:
    #         if "地下水的腐蚀性" in section["content"]:
    #             # if "........................" not in section:
    #             print(section["content"])
    #             point_4["地下水的腐蚀性"]["content"].append(section["content"])
    #             point_4["地下水的腐蚀性"]["page"].extend(section["page"])
    #         elif "地下水" in section["content"] and "腐蚀性" in section["content"]:
    #             print(section["content"])
    #             point_4["地下水的腐蚀性"]["content"].append(section["content"])
    #             point_4["地下水的腐蚀性"]["page"].extend(section["page"])

    print("xxxx")
    # for section in sections:
    #     print(f"Level {section['level']}: {section['title']}")
    #     print("\n".join(section["content"]))
    #     print("-" * 40)



