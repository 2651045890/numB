from split_byheader import *
import re
import requests
from postdify import *
import time
from pdfreader_new_ceshi import *
from collections import Counter

def split_long_str(data,max_len=1900):
    result={}
    for main_key in data.keys():
        original = data[main_key]
        con_list = original["content"]
        page_list = original["page"]
        long_str = ','.join(con_list).replace('\n','')
        str_len = len(long_str)

        if str_len<=max_len:
            result[main_key] = con_list
        chunks = [long_str[i:i+max_len] for i in range(0,str_len,max_len)]
        for i,chunk in enumerate(chunks):
            new_key = f"{main_key}_{i}" if i >0 else main_key
            result[new_key]={
                "content":[chunk],
                "page":page_list.copy()
            }
    return result
        



def upload_knowledge(url,keywords,informations,text_keys_2):
    # url = ""
    res_keywords=keywords+text_keys_2
    result = {key: {"content":[],"page":[]} for key in res_keywords}
    if text_keys_2:
        sections1 = split_pdf_by_one_headers(url)
        for section in sections1:
            for words in text_keys_2:
                if words in section['content']:
                    result[words]["content"].append(section['content'])
                    result[words]["page"].extend(section['page'])
    if keywords:
        sections = split_pdf_by_all_headers(url)
        for section in sections:
            for words in keywords:
                if words in section['content']:
                    result[words]["content"].append(section['content'])
                    result[words]["page"].extend(section['page'])
    # informations = {
    #     "id":"1212121",
    #     "xiangmu":"山东青岛平度卢乡（化工）110kV输变电工程",
    #     "wenjianjia":"山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/01 山东青岛平度卢乡（化工）灰埠变110kV保护改造工程/01说明书",
    #     "name":"变电部分初步设计说明书",
    #     "size":"110kV"
    # }
    # # # keywords = ["电容电流", "总征地面积", "围墙内占地面积", "关口计量点", "投产年", "中性点接地方式"]
    # keywords = ["电容电流","10kV低压侧"]

    
    
        # if any(key in section['content'] for key in keywords):
        #     result.append(section['content'])
        
    results = split_long_str(result)
    # print(results)
    result={key: {"content":[],"page":[]} for key in keywords}
    for key,value in results.items():
        if type(value) !=list:
            result[key]=value
        else:
            result.pop(key)
    print(result)

    know_title = f"{informations['xiangmu']}/{informations['wenjianjia']}/{informations['name']}"
    document_name = informations["name"]
    res = {key: '\n'.join(values["content"]) for key, values in result.items()}
    temp_content = [f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{list(dict.fromkeys(result[key]['page']))}\ncontent:{text}" for key,text in res.items()]
    content = '**\n'.join(temp_content)
    return content
    

def sum_page(data):
    values = list(data.values())
    result = []
    total=0
    for value in values:
        total+=value
        result.append(total)
    return result

def upload_knowledge_table(url,table_keywords,table_cons,informations):
    # url = ""
    # table_keywords = ["建议机械化施工的塔位情况表"]
    # informations = {
    #     "xiangmu":"山东青岛平度卢乡（化工）110kV输变电工程",
    #     "wenjianjia":"山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/01 山东青岛平度卢乡（化工）灰埠变110kV保护改造工程/01说明书",
    #     "name":"架空输电线路工程机械化施工专项设计方案",
    #     "id":111111,
    #     "size":"110kV"

    # }
    sections = extract_tables_from_pdf(url,table_keywords,table_cons)
    # sect = process_table1(sections[0])
    # print(sections)
    # print(informations)
    know_title = f"{informations['xiangmu']}/{informations['wenjianjia']}/{informations['name']}"
    document_name = informations["name"]
    table_contents,names = group_by_table(sections[0])
    tt = "**\n".join([str(item)for item in table_contents])
    num = dict(Counter(names))
    page_nums = sum_page(num)
    pages = sections[4]
    # print(len(table_contents))
    # print(f"*******************{pages}11*****************************")
    # print(f"*******************{page_nums}22*****************************")
    contents = []
    for i,con in enumerate(table_contents):
        try:
            if i ==0:
                content = f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{pages[:page_nums[i]]}\ncontent:{con}"
                contents.append(content)
            elif i<len(table_contents):
                content = f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{pages[page_nums[i-1]:page_nums[i]]}\ncontent:{con}"
                contents.append(content)
            else:
                content = f"title:{know_title}\n电压等级:{informations['size']}\ndoc_id:{informations['id']}\npage:{pages[page_nums[i]:]}\ncontent:{con}"
                contents.append(content)
        except:
            continue
    con = '**\n'.join(contents)
    return con
    



def test(url,table_keywords,informations):
    # url = ""
    # table_keywords = ["建议机械化施工的塔位情况表","本工程A线建议牵张场情况表"]
    informations = {
        "size":"110kv",
        "xiangmu":"山东青岛平度卢乡（化工）110kV输变电工程",
        "wenjianjia":"山东青岛平度卢乡（化工）110kV输变电工程-单项工程\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/01 山东青岛平度卢乡（化工）灰埠变110kV保护改造工程/01说明书",
        "wenjianmingcheng":"架空输电线路工程机械化施工专项设计方案"
    }
    know_title = f"{informations['xiangmu']}/{informations['wenjianjia']}/{informations['wenjianmingcheng']}"
    document_name = informations["wenjianmingcheng"]
    sections = extract_tables_from_pdf(url,table_keywords,'')
    table_contents,names = group_by_table(sections[0])
    tt = "**\n".join([str(item)for item in table_contents])
    print(tt)
    print(len(table_contents))
    print(len(sections[4]))
    print(sections[4])
    
    


def create_docs(url,text_keys,table_keys,informations,da_id,text_keys_2):
    
    text = ""
    table = ""
    if text_keys or text_keys_2:
        # url1="http://25.41.21.113/szjy/jinqu/2025-03-06/6d9e65580f734af18eb8cccc284a9e34.pdf"
        text = upload_knowledge(url,text_keys,informations,text_keys_2)
    if len(table_keys)>0:
        print(table_keys)
        table = upload_knowledge_table(url,table_keys,'{"杆塔一览表":["杆塔型式","呼高","全高"]}',informations)
    content = f"{text}**\n{table}"
    print(content)
    


if __name__=="__main__":
    url = "http://25.41.21.113/szjy/jinqu/2025-03-06/6d9e65580f734af18eb8cccc284a9e34.pdf"
    # upload_knowledge(url,"","")
    test("http://25.41.21.113/szjy/jinqu/uploadxc/2025-04-02/ea28815240534da6a66d9d156a02a52b.pdf",'','')

    # upload_knowledge_table("http://25.41.21.113/szjy/jinqu/2025-03-14/9cab4893d5b34b3fbebf8f2184d05245.pdf",['短路电流计算结果表', '短路电流计算表'],'{"短路电流计算结果表":["短路电流","三相"]}',{'xiangmu': '丽山110kV变电站新建工程', 'size': '110kV', 'wenjianjia': '说明书', 'name': '山东青岛 即墨丽山110kV变电站新建工程 初设说明书(审定版) .pdf(丽山110kV变电站新建工程)', 'id': '348692919f524c4dba9081f259162aec'})
    # create_docs("http://25.41.21.113/szjy/jinqu/2025-03-07/2f03b996858848c8bae86107a9a6ce00.pdf",[],["基础一览表","杆塔一览表"],'','cbbaa79a-d540-4c6f-a297-8c31a977e319',[])
    # sections = split_pdf_by_all_headers(url)
    # # result = []
    # keywords = ["电容电流", "总征地面积", "围墙内占地面积", "关口计量点", "投产年","中性点接地方式"]
    # result = {key:[] for key in keywords}
    # for i,section in enumerate(sections, start=1):
    #     for words in keywords:
    #         if words in section['content']:
    #             result[words].append(section['content'])
    #     # if any(key in section['content'] for key in keywords):
    #     #     result.append(section['content'])
    # res = {key:'\n'.join(values) for key,values in result.items()}
    # print("xxxx")