
import uvicorn
import os
import re
from split_byheader import find_text_in_pdf,split_pdf_by_all_headers,split_pdf_by_one_headers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pdfreader_new_ceshi import *
from excel import read_and_find_rows,search_excel,search_section
from collections import Counter
from inference_post import inference_post_QWEN, inference_post_QWEN_vl
import json
from pydantic import BaseModel
import fitz
import numpy as np
import pandas as pd
from get_oss import oss_url
from postdify import *
from upload import *

app = FastAPI()

headers = {"Content-Type": "application/json"}
origins = [

    "http://localhost",
    "http://localhost:8080",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    url: str = None
    fileList: list = None
    guize_url: str = None
    name: str = None
    rignt_word: list = None
    false_word: list = None
    sheet: str = None
    keywords: list = None
    point_type: str = None
    target_values: list = None
    unit_values: str = None
    target_value: str = None
    informations:dict = None
    text_keys:list = None
    table_keys:list= None
    da_id:str = None
    doc_id:str = None
    text_keys_2:list = None
    table_cons: str = None
    pages:list = None
    prompt:str = None


@app.post('/Point_4s')

def Point_4(url):
    # url = "data\山东青岛平度卢乡（化工）110kV输变电工程-支撑文件/12 勘察资料/12.岩土工程勘察报告书(线路部分).pdf"  # 输入PDF文件路径
    # url = "http://25.41.65.226:25000/api/oss/zhdlqx/folder/point4.pdf"
    sections = split_pdf_by_all_headers(url)
    point_4 = {
        "地下水的腐蚀性": {"content": [], "page": []},
        "场地土的腐蚀性": {"content": [], "page": []},
        "不良地质作用": {"content": [], "page": []},
        "地震液化": {"content": [], "page": []},
        "饱和单轴抗压强度": {"content": [], "page": []},
        "主要地质情况概述": {"content": [], "page": []},
        "地质参数": {"content": [], "page": []},
    }

    # print(sections)
    for section in sections:
        if "勘测任务" not in section["content"] and "地质调查" not in section["content"]:
            if "地下水的腐蚀性" in section["content"]:
                point_4["地下水的腐蚀性"]["content"].append(section["content"])
                point_4["地下水的腐蚀性"]["page"].extend(section["page"])

                # if "........................" not in section:
                print(f"地下水的腐蚀性:{section['content']}")
            elif "地下水" in section["content"] and "腐蚀性" in section['content']:
                print(f"地下水的腐蚀性:{section['content']}")
                point_4["地下水的腐蚀性"]["content"].append(section["content"])
                point_4["地下水的腐蚀性"]["page"].extend(section["page"])


            elif "场地土的腐蚀性" in section["content"]:
                # if "........................" not in section:
                print(f"{section['content']}")
                point_4["场地土的腐蚀性"]["content"].append(section['content'])
                point_4["场地土的腐蚀性"]["page"].extend(section["page"])


            elif "场地土" in section['content'] and "腐蚀性" in section['content']:
                print(f"场地土的腐蚀性{section['content']}")
                point_4["场地土的腐蚀性"]["content"].append(section['content'])
                point_4["场地土的腐蚀性"]["page"].extend(section["page"])


            elif "不良地质作用" in section['content']:
                print(f"不良地质作用：{section['content']}")
                point_4["不良地质作用"]["content"].append(section['content'])
                point_4["不良地质作用"]["page"].extend(section["page"])


            elif "地震液化" in section['content']:
                print(f"地震液化：{section['content']}")
                point_4["地震液化"]["content"].append(section['content'])
                point_4["地震液化"]["page"].extend(section["page"])

    point_6_1 = extract_tables_from_pdf(url, "桩基设计岩土参数建议值")
    point_6_2 = extract_tables_from_pdf(url, "地基土主要物理力学指标及地基承载力特征值")
    point_4["地质参数"]["content"].append(point_6_1[0])
    point_4["地质参数"]["content"].append(point_6_2[0])
    point_4_1 = '\n'.join(point_4["地下水的腐蚀性"]["content"])
    point_4_2 = '\n'.join(point_4["场地土的腐蚀性"]["content"])
    point_4_3 = '\n'.join(point_4["不良地质作用"]["content"])
    point_4_4 = '\n'.join(point_4["地震液化"]["content"])
    point_4_6 = point_4["地质参数"]["content"]
    point_4["地下水的腐蚀性"]["content"]=point_4_1
    point_4["场地土的腐蚀性"]["content"]=point_4_2
    point_4["不良地质作用"]["content"]=point_4_3
    point_4["地震液化"]["content"]=point_4_4
    point_4["地质参数"]["content"]=point_4_6

    return {"data": {
        "result": point_4,
        "type": 'json'
    },
        "code":200}


@app.post('/Point_12s')

def Point_12(url,keywords=["人工开挖"]):
    url = "F:\python\point15\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/02 郁秩～卢乡（化工）110kV线路工程（架空部分）/04 概算书\郁秩～卢乡（化工）110kV线路工程（架空部分）.xlsx"
    search_result = search_excel(url, keywords)
    name = '、'.join(keywords)
    if not search_result:
        results = f"{name[-1]}架空单项工程无基础采用人工开挖方式"
    else:
        results = search_result
    results_dict = {"data":
                        {"result": results,
                         "type": 'str'},
                    "code": 200}
    print(results_dict)

    return results_dict

@app.post('/Point_14s')

def Point_14(request_data:Item):
    urls = request_data.fileList
    keywords = request_data.keywords

    result = []
    for item in urls:
        try:
            url = item["filePath"]
            fileName = item["fileName"]
            print(keywords)
            # url = "F:\python\point15\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/02 郁秩～卢乡（化工）110kV线路工程（架空部分）/04 概算书\郁秩～卢乡（化工）110kV线路工程（架空部分）.xlsx"
            search_result = search_excel(url,keywords)
            name = '、'.join(keywords)
            if not search_result:
                results = f"文件：{fileName}，{name}架空单项工程无施工验收辅助措施"
            else:
                results = '\n'.join(search_result)
                results = f"文件：{fileName}，{results}"
        except:
            results = f"文件：{fileName} 异常"
        result.append(results)
    # results_dict = {"data":
    #             {"result": '\n'.join(result),
    #             "type": 'str'},
    #         "code": 200}
    results_dict = {"data":
                {"content": result},
            "code": 200}
    print(results_dict)

    return results_dict



@app.post('/Point_16s')
def Point_16(request_data:Item):
    sheet = request_data.sheet
    sheet= "架空输电线路工程总概算表"

    url = request_data.file_list
    # url = 'F:\python\point15/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    first_result, first_column = read_and_find_rows(url, sheet, ["一般线路本体工程"], "单位投资万元")
    result = []
    if first_result is not None:
        result_1 = first_result.loc[:, first_column].values
        # result.append(result_1)
        print("\n找到以下行数据：")
        print(first_result.loc[:, first_column].values)
    result_2_dan = float("27")
    result_2_gexiang = float("26")

    result_3_dan = float("27")
    result_3_gexiang = float("26.5")
    if result_2_gexiang > 25 and result_2_gexiang < 32 and result_3_gexiang > 25 and result_3_gexiang < 32:
        if abs(result_2_gexiang - result_3_gexiang) < 1:
            res = "杆塔基础投资占比合理。"
            result.append(res)
    else:
        res = "杆塔基础投资占比不合理。"
        result.append(res)

    results = {
        "data": {
            "content": '\n'.join(result),
            "type": 'str'
        },  # 是否调用大模型
        "code": 200,

    }

    # return conclusion, output_cols
    return results


@app.post('/Point_19s')
def Point_19(request_data:Item):

    urls = request_data.fileList
    keywords = request_data.keywords

    result = []
    for item in urls:
        try:
            url = item["filePath"]
            fileName = item["fileName"]
            print(keywords)
            # url = "F:\python\point15\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/02 郁秩～卢乡（化工）110kV线路工程（架空部分）/04 概算书\郁秩～卢乡（化工）110kV线路工程（架空部分）.xlsx"
            search_result = search_excel(url,keywords)
            name = '、'.join(keywords)
            if not search_result:
                results = f"文件：{fileName}，{name}架空单项工程无施工验收辅助措施"
            else:
                results = '\n'.join(search_result)
                results = f"文件：{fileName}，{results}"
        except:
            results = f"文件：{fileName} 异常"
        result.append(results)
    # results_dict = {"data":
    #             {"result": '\n'.join(result),
    #             "type": 'str'},
    #         "code": 200}
    results_dict = {"data":
                {"content": result},
            "code": 200}
    print(results_dict)

    return results_dict


@app.post('/bianjing_8s')
def bianjing_8(request_data:Item):
    #添加列表处理
    urls = request_data.fileList
    # print(urls)
    sheet = request_data.sheet
    target_values = request_data.target_values
    unit_values = request_data.unit_values
    # url = "D:\代码\代码\docling\docling-main\docling-main\jingyanyuan\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/02 山东青岛平度卢乡（化工）110kV变电站新建工程/06 概算书/1.山东青岛平度卢乡（化工）110千伏变电站新建工程 2025-4-2.xlsx"
    # sheet = "变电站建筑工程概算表"
    result=[]
    for item in urls:
        try:
            url = item["filePath"]
            fileName = item["fileName"]
            if 'xlsx' not in url:
                file_path = url
                url = f"F:\python\point15/test/{fileName}x"
                response = requests.get(file_path)
                with open(url,'wb') as f:
                    for chunk in response.iter_content():
                        f.write(chunk)
                f.close()
            # file_path = convert_xls2xlsx(pdf_file)
        # 读取Excel文件中的指定工作表
            # else:
            first_result, first_column = read_and_find_rows(url, sheet, target_values, unit_values)
            print(first_result)
            results_list = []
            for res in first_result.values.tolist():
                res.remove('')
                matched = [item for item in res if '*1.15' in str(item) and item]
                if matched:
                    results_list.append(matched[0])
            if fileName in url:
                os.remove(url)
            if len(results_list)==len(first_result):
                results = f"{fileName}合规"
            else:
                results = f"{fileName}不合规"
        except:
            results = f"文件：{fileName} 异常"
        print("xxx")
        result.append(results)
    # res = {
    #     "data": {
    #         "result": result,
    #         "type":"str"
    #     },
    #     "code": 200
    # }
    res = {
        "data": {
            "content": result
        },
        "code": 200
    }
    print(res)
    return res

@app.post('/bianjing_10s')
def bianjing_10(request_data:Item):
        #添加列表处理

    urls = request_data.fileList
    sheet = request_data.sheet
    target_values = request_data.target_value
    unit_values = request_data.unit_values
    # url = "D:\代码\代码\docling\docling-main\docling-main\jingyanyuan\data\山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/02 山东青岛平度卢乡（化工）110kV变电站新建工程/06 概算书/1.山东青岛平度卢乡（化工）110千伏变电站新建工程 2025-4-2.xlsx"
    # sheet = "变电站安装工程概算表"
    # 设置关键词 A 和 B（你要找的起始行和结束行的关键字）
    # target_values = "低压电容器"
    # unit_values = "合计"
    result=[]
    for item in urls:
        try:
            url = item["filePath"]
            fileName = item["fileName"]
            if 'xlsx' not in url:
                file_path = url
                url = f"F:\python\point15/test/{fileName}x"
                response = requests.get(file_path)
                with open(url,'wb') as f:
                    for chunk in response.iter_content():
                        f.write(chunk)
                f.close()
            first_result = search_section(url, sheet, target_values, unit_values)
            results_list = []
            for first_res in first_result.values.tolist():
                matched = [item for item in first_res if 'YD5-88' in str(item) and item]
                if matched:
                    results_list.append(matched[0])
            if fileName in url:
                os.remove(url)

            if results_list:
                results = f"{fileName}合规"
            else:
                results = f"{fileName}不合规"
        except:
            results = f"文件：{fileName} 异常"
        result.append(results)

    res = {
        "data": {
            "content": result
        },
        "code": 200
    }
    print(res)
    return res

@app.post('/xianjing_2s')
def xianjing_2(request_data:Item):
        #添加列表处理

    urls = request_data.fileList
    sheet = request_data.sheet
    target_values = request_data.target_values
    unit_values = request_data.unit_values
    # sheet = "输电线路工程工地运输工程量计算表"
    # url = 'data/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    results=[]
    for item in urls:
        try:
            url = item["filePath"]
            fileName = item["fileName"]    
            first_result, first_column = read_and_find_rows(url, sheet, target_values, unit_values)
            second_result, second_column = read_and_find_rows(url, "编制说明", ["新建线路长约"], "")
            # second_result
            result = []
            for se_res in second_result.values[0]:
                if se_res!='':
                    match = re.search("新建线路长约(.+?)km",se_res).group(1).replace(' ','')
            first_result=first_result.reset_index(drop=True)
            peo_row,peo_col = np.where(first_result=="人力运输")
            car_row,car_col = np.where(first_result=="汽车运输")
            if not first_result.loc[peo_row[0],first_column] or first_result.loc[peo_row[0],first_column]==0:
                result.append(f"{fileName}人力运输距离合理")
            else:
                result.append(f"{fileName}人力运输不合理")
            if not first_result.loc[car_row[0], first_column] or float(first_result.loc[car_row[0], first_column]) < float(match)/2:
                result.append(f"{fileName}汽车运输距离合理")
            else:
                result.append(f"{fileName}汽车运输距离不合理")
        except:
            result = [f"文件：{fileName} 异常"]
        results.append('\n'.join(result))
    res = {
        "data": {
            "content": results
        },
        "code": 200
    }
    print(res)
    return res
roman_to_int = {'Ⅰ': 1, 'Ⅱ': 2, 'Ⅲ': 3, 'Ⅳ': 4, 'Ⅴ': 5,
    'Ⅵ': 6, 'Ⅶ': 7, 'Ⅷ': 8, 'Ⅸ': 9, 'Ⅹ': 10
}
@app.post('/xianjing_9s')
def xianjing_9(request_data:Item):
        #添加列表处理

    urls = request_data.fileList
    sheet = request_data.sheet
    target_values = request_data.target_values
    unit_values = request_data.unit_values
    # sheet = "勘察费复杂程度表"
    # url = 'data/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    results=[]
    for item in urls:
        try:
            url = item["filePath"]
            fileName = item["fileName"]    
            first_result, first_column = read_and_find_rows(url, sheet, [], "类别")
            level_result = first_result[first_column].to_list()
            result = []
            for i,num in enumerate(level_result):
                if num !='' and num !='类别' and roman_to_int[num]>3:
                    abn_result_list = first_result.loc[i].values.tolist()
                    # abn_result = [str(x) for x in abn_result_list]
                    result.append(f"{fileName}{abn_result_list}勘察费复杂程度超过Ⅲ，预警提示")
            if not result:
            #     result = list(set(result))[0]
            # else:
                result = [f"{fileName}勘察费复杂程度正常"]
        except:
            result = [f"文件：{fileName} 异常"]
        results.append('\n'.join(result))
    res = {
        "data": {
            "content": results
        },
        "code": 200
    }
    print(res)
    return res





@app.post('/create_datasets')
def create_datasets(request_data:Item):
    name = request_data.name
    res = create_new_datasets(name)
    print(res)
    return res

@app.post('/create_datasets_dizuo')
def create_datasets(request_data:Item):
    name = request_data.name
    res = create_new_datasets_dizuo(name)
    print(res)
    return res

@app.post('/update_knowledge')
def create_docs(request_data:Item):
    #dify 关键词索引向量库上传
    da_id = request_data.da_id
    url = request_data.url
    text_keys = request_data.text_keys
    table_keys = request_data.table_keys
    informations = request_data.informations
    text_keys_2 = request_data.text_keys_2
    table_cons = request_data.table_cons.replace("'",'"')
    print(f"入参{url},text{text_keys},table_key{table_keys},infor{informations},sec{text_keys_2},table_cons{table_cons}")

    if 'doc' in url:
        convert_data ={
            "url":url
        }
        url_response = requests.post("http://25.41.65.235:8002/intelligent/file/convertWordToPdf",data=json.dumps(convert_data),headers=headers)
        url_json = url_response.json()
        if url_json["code"]=="200":
            url = url_json["resultBody"]["url"]
    text = ""
    table = ""
    if text_keys or text_keys_2:
        # url1="http://25.41.21.113/szjy/jinqu/2025-03-06/6d9e65580f734af18eb8cccc284a9e34.pdf"
        print("processing text")
        text = upload_knowledge(url,text_keys,informations,text_keys_2)
    if len(table_keys)>0:
        print("processing table")
        table = upload_knowledge_table(url,table_keys,table_cons,informations)
    content = f"{text}**\n{table}"
    print(content)
    document_name = informations["name"]
    responses=create_new_documents(document_name,content,da_id)

    res = {
        "id":responses["content"]["document"]["id"],
        "name":responses["content"]["document"]["name"],
        "batch":responses["content"]["batch"]

    }
    # res = create_new_datasets(name)
    print(responses)
    return res

@app.post('/update_knowledge_dizuo')
def create_docs(request_data:Item):
    # 底座全量知识库上传
    da_id = request_data.da_id
    url = request_data.url
    # text_keys = request_data.text_keys
    # table_keys = request_data.table_keys
    informations = request_data.informations
    # text_keys_2 = request_data.text_keys_2
    table_cons = request_data.table_cons.replace("'",'"')
    print(f"入参{url},infor{informations}table_cons{table_cons}")

    if 'doc' in url:
        convert_data ={
            "url":url
        }
        url_response = requests.post("http://25.41.65.235:8002/intelligent/file/convertWordToPdf",data=json.dumps(convert_data),headers=headers)
        url_json = url_response.json()
        if url_json["code"]=="200":
            url = url_json["resultBody"]["url"]
    text = ""
    table = ""
    know_title = f"{informations['xiangmu']}/{informations['wenjianjia']}/{informations['name']}"
# if text_keys or text_keys_2:
    # url1="http://25.41.21.113/szjy/jinqu/2025-03-06/6d9e65580f734af18eb8cccc284a9e34.pdf"
    print("processing text")
    sections1 = split_pdf_by_all_headers(url)
    sections = process_headers(sections1) 
    text_temp = [f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{item['page']}\ncontent:{item['content']}" for item in sections]
    text = '**\n'.join(text_temp)
    content = text
    # text = upload_knowledge(url,text_keys,informations,text_keys_2)
# if len(table_keys)>0:
    print("processing table")

    table_result = extract_tables_from_pdf(url,table_content='{"杆塔一览表":["杆塔型式","呼高","全高"],"短路电流计算结果表":["短路电流","冲击电流"]}')
    table_content = ""
    if table_result[0]:
        print(f"11111{len(table_result[0])}")
        # print(table_result[0][0])
        table1,page1 = group_by_table_new(table_result[0])
        temp_content1 = [f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{page1[i]}\ncontent:{table}" for i,table in enumerate(table1)]
        tables1 = '**\n'.join(temp_content1)
        table_content = table_content+"**\n"+tables1

    if table_result[2]:
        print(f"222222{len(table_result[2])}")
        table2,page2 = group_by_table_new(table_result[2])
        temp_content2 = [f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{page2[i]}\ncontent:{table}" for i,table in enumerate(table2)]
        tables2 = '**\n'.join(temp_content2)
        table_content = table_content+"**\n"+tables2

    # content = f"{text}**\n{tables1}**\n{tables2}"
    # print(content)
    document_name = informations["name"]
    path = f"F:\python\point15/test/{document_name}.txt"
    table_path = f"F:\python\point15/test/table_{document_name}.txt"
    if not table_content:
        table_content = "未提取到表格内容**"
    # path = f"data/{document_name}.txt"
    if not content:
        content = "未提取到文本内容"
    # da_id = "9d8aad40-6b83-48e4-ac61-90e84cc02615"
    responses=create_new_documents_dizuo(path,content,da_id)
    table_responses = create_new_documents_dizuo(table_path,table_content,da_id)
    res = {
        "id":responses["content"]["data"][0]["id"],
        "table_id":table_responses["content"]["data"][0]["id"],

        "name":responses["content"]["data"][0]["name"],
        "table_name":table_responses["content"]["data"][0]["name"],

    }
    # res = create_new_datasets(name)
    print(responses)
    # os.remove(path)
    # os.remove(table_path)
    return res

@app.post('/update_knowledge1')
def create_docs(request_data:Item):
    da_id = request_data.da_id
    url = request_data.url
    text_keys = request_data.text_keys
    table_keys = request_data.table_keys
    informations = request_data.informations
    text_keys_2 = request_data.text_keys_2
    table_cons = request_data.table_cons.replace("'",'"')
    print(f"入参{url},text{text_keys},table_key{table_keys},infor{informations},sec{text_keys_2},table_cons{table_cons}")
    text = ""
    table = ""
    if text_keys or text_keys_2:
        # url1="http://25.41.21.113/szjy/jinqu/2025-03-06/6d9e65580f734af18eb8cccc284a9e34.pdf"
        print("processing text")
        text = upload_knowledge(url,text_keys,informations,text_keys_2)
    if len(table_keys)>0:
        print("processing table")

        table = upload_knowledge_table(url,table_keys,table_cons,informations)
    content = f"{text}**\n{table}"
    print(content)
    document_name = informations["name"]
    path = f"F:\python\point15/test/{document_name}.txt"
    # path = f"data/{document_name}.txt"

    da_id = "9d8aad40-6b83-48e4-ac61-90e84cc02615"
    responses=create_new_documents_dizuo(path,content,da_id)

    # responses=create_new_documents_dizuo(path,content,da_id)
    
    res = {
        "id":responses["content"]["data"][0]["id"],
        "name":responses["content"]["data"][0]["name"],
        "batch":1

    }
    os.remove(path)
    # res = create_new_datasets(name)
    print(responses)
    return res

@app.post('/delete_document')
def delete_doc(request_data:Item):
    da_id = request_data.da_id
    doc_id = request_data.doc_id
    # name = request_data.name
    res = delete_documents(da_id,doc_id)
    print(res)
    return res

@app.post('/search_process')
def search_pro(request_data:Item):
    da_id = request_data.da_id
    # name = request_data.name
    res = search_process(da_id)
    print(res)
    return res
import re

@app.post('/re')
def match(text):
    # t = "<think>\n\n</think>\n\n```json\n{\n  \"判断结果\": \"数值3小于5\",\n  \"page\": [1, 33]\n}\n```"
    t = text.replace("\n",'')
    match = re.search("```json(.*?)```",t).group(1)
    return match
import os
@app.post('/multimodal')
def exact_content(request_data:Item):
    #提取PDF表格输入的对应内容
    urls = request_data.fileList
    con = request_data.target_value
    # sheet = "勘察费复杂程度表"
    # url = 'data/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    results=[]
    prompt = f"你是一个数据分析专家，有多年数据分析经验，请根据用户输入的数据提取表格中{con}的全部内容，严格按照以下要求提取，要求如下：如果出现{con}则提取出后面对应的内容，否则输出无，直接输出结果即可，不要出现其他内容"
    for item in urls:
        url = item["filePath"]
        fileName = item["fileName"]
        result=[]
        if "pdf" in fileName or "PDF" in fileName:
            name = fileName.replace('.pdf','').replace(".PDF","")
            res = requests.get(url)
            pdf_file = BytesIO(res.content)
            doc = fitz.open(stream=pdf_file,filetype="pdf")
            nums = doc.page_count
            for i in range(nums):

                page = doc[i-1]
                # 设置截图区域（这里设置为整个页面）
                rect = page.rect
                clip = fitz.Rect(rect.top_left, rect.bottom_right)
                # 获取截图
                pix = page.get_pixmap(clip=clip)
                # 保存截图
                output_file = f"F:\python\point15/test/{name}_page{i}.png"
                # output_file = f"data/{name}_page{i}.png"
                pix.save(output_file)
                name_oss = f"{name}_page{i}"
                os_url = oss_url(output_file,name)

                res = inference_post_QWEN_vl(prompt,os_url)
                print(res)
                res = f"文件:{fileName}\n{res}"
                result.append(res)
                os.remove(output_file)
                
                
        else:
            res = inference_post_QWEN_vl(prompt,url)
            result = [f"文件:{fileName}\n{res}"]
        results.append('\n'.join(result))
        
        # results.append(result)
    out = {
        "data": {
            "content": results
        },
        "code": 200
    }
    return out
import time
@app.post('/multimodal_1')
def exact_content1(request_data:Item):
    urls = request_data.fileList
    # con = request_data.target_value
    # sheet = "勘察费复杂程度表"
    # url = 'data/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    results=[]
    # prompt = """你是一个数据分析专家，有多年数据分析经验，第一步，请提取图片表格中的桩号和对应的杆塔型号，第二步，根据第一步提取的结果判断，依次判断杆塔型号中是否包含-DJ-或-DL-，当杆塔型号中包含-DJ-或-DL-时，输出该桩号和对应的杆塔型号，按照桩号：xx，杆塔型号格式输出，第三步，将第二步的结果以json格式输出，要求最终结果以json格式输出，输出格式如下{'result':[桩号：xx，杆塔型号:xx,桩号：xx，杆塔型号:xx]}，
    # 示例如下:输入：'桩号：B#31，杆塔型号:110-D0215-DL-2T', '桩号：B#32，杆塔型号:110-D0215-Z2-2T', '桩号：B#34，杆塔型号:110-D0215-ZK-39', '桩号：B#36，杆塔型号:110-D0215-ZK-45', '桩号：B#37，杆塔型号:110-D0215-Z2-30', '桩号：B#38，杆塔型号:110-D0215-Z2-2T', '桩号：B#40，杆塔型号:110-D0215-Z1-24', '桩号：B#42，杆塔型号:110-D0215-ZK-42', '桩号：B#43，杆塔型号:110-D0215-J3-2T', '桩号：B#44，杆塔型号:110-D0215-J4-18', '桩号：B#45，杆塔型号:110-D0215-Z3-36', '桩号：B#46，杆塔型号:110-D0215-Z3-36', '桩号：B#47，杆塔型号:110-D0215-J4-2T', '桩号：B#48，杆塔型号:110-D0215-J4-2T', '桩号：B#49，杆塔型号:110-D0215-Z1-24', '桩号：B#50，杆塔型号:110-D0215-DL-15', '桩号：B#51，杆塔型号:110-D0210-J1-15'，
    # 输出：{'result':[桩号：B#50，杆塔型号:110-D0215-DL-15,桩号：B#31，杆塔型号:110-D0215-DL-2T]}"""
    # prompt = """你是一个数据分析专家，有多年数据分析经验，第一步，请提取图片表格中的桩号和对应的杆塔型号，第二步，根据第一步提取的结果判断，依次判断杆塔型号中是否为xxx-xx...xx-DJ-xx或xxx-xx...xx-DL-xx，当杆塔型号中为xxx-xx...xx-DJ-xx或xxx-xx...xx-DL-xx时，输出该桩号和对应的杆塔型号，按照桩号：xx，杆塔型号格式输出，第三步，将第二步的结果以json格式输出，要求最终结果以json格式输出，输出格式如下{'result':[桩号：xx，杆塔型号:xx,桩号：xx，杆塔型号:xx]}"""
    prompt = """你是一个数据分析专家，有多年数据分析经验，第一步，请提取图片表格中的桩号和对应的杆塔型号，第二步，根据第一步提取的结果判断，依次判断杆塔型号中是否为xxx-xx...xx-DJ-xx或xxx-xx...xx-DL-xx，当杆塔型号中为xxx-xx...xx-DJ-xx或xxx-xx...xx-DL-xx时，输出该桩号和对应的杆塔型号，按照桩号：xx，杆塔型号格式输出，第三步，将第二步的结果以json格式输出，要求严格按照以下格式输出：{'result':[桩号：xx，杆塔型号:xx,桩号：xx，杆塔型号:xx]}"""
    for item in urls:
        url = item["filePath"]
        fileName = item["fileName"]
        result=[]
        try:
            if "pdf" in fileName or "PDF" in fileName:
                name = fileName.replace('.pdf','').replace(".PDF","")
                res = requests.get(url)
                pdf_file = BytesIO(res.content)
                doc = fitz.open(stream=pdf_file,filetype="pdf")
                nums = doc.page_count
                for i in range(nums):

                    page = doc[i-1]
                    # 设置截图区域（这里设置为整个页面）
                    rect = page.rect
                    # clip = fitz.Rect(rect.x0, rect.y0 + 90, rect.x1, rect.y1 - 100)
                    clip = fitz.Rect(rect.top_left, rect.bottom_right)

                    # 获取截图
                    pix = page.get_pixmap(clip=clip)
                    # 保存截图
                    output_file = f"F:\python\point15/test/{name}_page{i}.png"
                    # output_file = f"data/{name}_page{i}.png"

                    pix.save(output_file)
                    name_oss = f"{name}_page{i}"
                    os_url = oss_url(output_file,name)

                    res = inference_post_QWEN_vl(prompt,os_url)
                    t = res.replace("\n",'')
                    match = re.search("```json(.*?)```",t,re.DOTALL).group(1)
                    print(match)
                    res_json = json.loads(match)
                    print(res_json["result"])
                    res = f"文件:{fileName}\n{res_json['result']}"
                    result.append(res)
                    os.remove(output_file)
                    
                    
            else:
                res = inference_post_QWEN_vl(prompt,url)
                t = res.replace("\n",'')
                match = re.search("```json(.*?)```",t,re.DOTALL).group(1)
                res_json = json.loads(match)
                print(res_json["result"])
                res = f"文件:{fileName}\n{res_json['result']}"
            results.append('\n'.join(result))
            time.sleep(3)
        except:
            continue
        # results.append(result)
    out = {
        "data": {
            "content": results
        },
        "code": 200
    }
    return out

@app.post('/stage_sign')
def stage_signs(request_data:Item):
    urls = request_data.fileList
    # con = request_data.target_value
    # sheet = "勘察费复杂程度表"
    # url = 'data/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/山东青岛平度卢乡（化工）110kV输变电工程-单项工程/02 线路架空/01 唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）/04 概算书/唐田～灰埠（唐灰甲线）T接卢乡（化工）110kV线路工程（架空部分）.xlsx'
    results=[]
    nums = request_data.pages
    prompt = request_data.prompt
    # prompt = '第一步，请判断该报告为可研阶段/初设阶段/详勘阶段/施工图阶段，如果为详勘阶段/施工图阶段，则返回岩土工程报告书为详勘阶段/施工图阶段，如果为可研阶段/初设阶段，则返回岩土工程报告书为可研阶段/初设阶段，不符合要求。第二步，将第一步的结果以jso格式输出，格式为{"result":xxx}'
    # prompt = '你是一个数据分析专家，有多年数据分析经验，第一步，请提取图片表格中的桩号和对应的杆塔型号，第二步，根据第一步提取的结果判断，当杆塔型号中包含DJ或DL时，输出该桩号和对应的杆塔型号，第三步，将第二步输出的值依次按照桩号：xx，杆塔型号格式输出，第四步，将第三步的结果以json格式输出，格式为{"result":xxx}'
    for item in urls:
        if type(item) != dict:
            
            temp = item.replace("'",'"')
            print(temp)
            item = json.loads(temp)
        url = item["filePath"]
        
        fileName = item["fileName"]
        result=[]
        
        res = requests.get(url)
        pdf_file = BytesIO(res.content)
        doc = fitz.open(stream=pdf_file,filetype="pdf")
        
        name = fileName.replace('.pdf','').replace(".PDF","")
        for i in nums:

            page = doc[i-1]
            # 设置截图区域（这里设置为整个页面）
            rect = page.rect
            clip = fitz.Rect(rect.top_left, rect.bottom_right)
            # 获取截图
            pix = page.get_pixmap(clip=clip)
            # 保存截图
            output_file = f"F:\python\point15/test/{name}_page{i}.png"
            # output_file = f"data/{name}_page{i}.png"
            pix.save(output_file)
            name_oss = f"{name}_page{i}"
            os_url = oss_url(output_file,name)

            res = inference_post_QWEN_vl(prompt,os_url)
            t = res.replace("\n",'')
            match = re.search("```json(.*?)```",t).group(1)
            print(match)
            res_json = json.loads(match)
            print(res_json["result"])
            res = f"文件:{fileName}第{i}页,{res_json['result']}"
            result.append(res)
            os.remove(output_file)
                
                
        
        results.append('\n'.join(result))
        
        # results.append(result)
    out = {
        "data": {
            "content": results
        },
        "code": 200
    }
    return out

@app.post('/search_data')
def search_datas(request_data:Item):
    search_data=request_data.target_value
    if search_data:
        # da_id = request_data.da_id
        temp = search_data.split(";")
        print(temp)
        da_id=temp[1]
        keys = temp[0]
        temp_key = keys.split("*")
        print(temp_key[1])

        response = search_dataset(temp_key[1],da_id)
        key_list = temp_key[1].split(',')
        res = ""
        for item in response["records"]:
            # if temp_key[1] in str(item["segment"]["content"]) and temp_key[0] in str(item):

            if any(temp in str(item["segment"]["content"]).replace('\n','').replace(' ','') for temp in key_list) and temp_key[0] in str(item):
                res= item["segment"]["content"]
                print(f"************************************************{res}")

                break
    else:
        res=""
    return res

@app.post('/search_rule')
def search_rules(request_data:Item):
    search_data=request_data.target_value
    # da_id = request_data.da_id
    temp = search_data.split(";")
    print(temp)
    da_id=temp[1]
    keys = temp[0]
    temp_key = keys.split("*")
    print(temp_key[1])

    response = search_dataset(temp_key[1],da_id)
    key_list = temp_key[1].split(',')
    res = []
    for item in response["records"]:
        # if temp_key[1] in str(item["segment"]["content"]) and temp_key[0] in str(item):

        if any(temp in str(item["segment"]["content"]).replace('\n','').replace(' ','') for temp in key_list) and temp_key[0] in str(item):
            res.append(item["segment"]["content"])
            # print(f"************************************************{res}")

            # break
    return res


@app.post('/search_data_dizuo')
def search_datas_dizuo(request_data:Item):
    search_data=request_data.target_value
    if search_data:
        # da_id = request_data.da_id
        temp = search_data.split(";")
        print(temp)
        da_id=temp[1]
        keys = temp[0]
        temp_key = keys.split("*")
        print(temp_key[1])

        response = search_dataset_dizuo(temp_key[1],da_id)
        key_list = temp_key[1].split(',')
        res = ""
        for item in response["data"]["data"]:
            # if temp_key[1] in str(item["segment"]["content"]) and temp_key[0] in str(item):

            if any(temp in str(item["chunkedFullText"]).replace('\n','').replace(' ','') for temp in key_list) and temp_key[0] in str(item):
                res= item["chunkedFullText"]
                print(f"************************************************{res}")

                break
    else:
        res=""
    return res

@app.post('/search_rule_dizuo')
def search_rules_dizuo(request_data:Item):
    search_data=request_data.target_value
    # da_id = request_data.da_id
    temp = search_data.split(";")
    print(temp)
    da_id=temp[1]
    keys = temp[0]
    temp_key = keys.split("*")
    print(temp_key[1])

    response = search_dataset_dizuo(temp_key[1],da_id)
    key_list = temp_key[1].split(',')
    res = []
    for item in response["data"]["data"]:
        # if temp_key[1] in str(item["segment"]["content"]) and temp_key[0] in str(item):
        # print(item)
        if any(temp in str(item["chunkedFullText"]).replace('\n','').replace(' ','') for temp in key_list) and temp_key[0] in str(item):
            res.append(item["chunkedFullText"])
            # print(f"************************************************{res}")
    res = list(set(res))
    return res

if __name__ == '__main__':
    uvicorn.run(app=app,
                host='0.0.0.0',
                # reload=True,
                port=8501,
                workers=1)