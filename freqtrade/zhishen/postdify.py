import requests
import json
import time

def create_new_datasets(name):
    # 创建空知识库
    url = "http://25.41.65.234:25025/v1/datasets"
    headers = {
        "Authorization": "Bearer dataset-9y6qZ7HNVq5rR7CD3bQatXOp",
        "Content-Type": "application/json"
    }

    data ={"name": name, "permission": "all_team_members"}

    try:
        print("运行工作流...")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("工作流执行成功")
            return {
                "code":200,
                "id":response.json()["id"],
            "name":response.json()["name"]
            }
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")
            return {"code": response.json()['status'], "message": response.json()['message']}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}

def create_new_datasets_dizuo(name):
    # 创建空知识库
    url = "http://25.41.75.98:7077/zstx-openapi/knowledgeBaseOpenApi/createKnowledgeBase"
    

    data ={
  "createBy": "EBBD7C0BAAF1AF0CE0408D0A5A04761D",
  "departId": "50",
  "name": name,
  "orgId": "3D22382DBCCF42FEE053D3088D0A7C62",
  "type": "1"
}

    try:
        print("运行工作流...")
        response = requests.post(url, json=data)
        response_res = response.json()
        if response_res["code"] == 200:
            print("工作流执行成功")
            return {
                "code":200,
                "id":response_res["data"]["id"],
                "name":response_res["data"]["name"]
            }
        else:
            print(f"工作流执行失败，状态码: {response_res['code']}")
            return {"code": response_res['code'], "message": response_res['msg']}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}


def create_new_documents(name,text,dataset_id):
    #通过文本向已存在知识库添加文档片段
    #现用
    url = f"http://25.41.65.234:25025/v1/datasets/{dataset_id}/document/create-by-text"

    # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/document/create-by-text"
    headers = {
        "Authorization": "Bearer dataset-9y6qZ7HNVq5rR7CD3bQatXOp",
        "Content-Type": "application/json"
    }

    data ={"name": name,"text":text,"indexing_technique": "high_quality","process_rule": {"mode":"custom","rules":{"pre_processing_rules":[],"segmentation":{"separator":"**","max_tokens":3900,"chunk_overlap":600}}},"retrieval_model":{
	"search_method":"hybrid_search",
	"reranking_enable":True,
	"reranking_model":{"reranking_provider_name":"openai_api_compatible","reranking_model_name":"BAAI/bge-reranker-v2-m3"},
	"top_k":8,
    "score_threshold_enabled":False,
    "score_threshold":0,
	"embedding_model":"bge",
	"embedding_model_provider":"openai_api_compatible"
}}

    try:
        print("运行工作流...")
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        if response.status_code == 200:
            print("工作流执行成功")
            return {
                "code":200,
                "content":response.json()}
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")
            return {
                "code":400,
                "content":"Failed to create documents"}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}


def create_new_documents_dizuo(path,text,dataset_id):
    #通过文本向已存在知识库添加文档片段
    #现用
    url = f"http://25.41.75.98:7077/zstx-openapi/knowledgeBaseOpenApi/uploadAndProcessList"
    file = open(path,'w',encoding='utf-8')
    file.write(text)
    # print(text)
    file.close()
    # time.sleep(8)
    # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/document/create-by-text"
    # dataset_id='b5e1ef03-03c7-421f-8c95-c0ed2c259c68'
    form_data = {
        'baseId': dataset_id,
        'byLength': '3900',
        'chunkType': '2',
        'fileOverwriteOption': 1,
        'parseType': '2',
        'byChars': ['**'],
        'splitType': '1',
        'userId': 'EBBD7C0BAAF1AF0CE0408D0A5A04761D',
        
    }
    files = {'file':open(path,'rb')}

    # 发送 POST 请求
    print("222222222222222222222222222222222222222222222")
    try:
        print("运行工作流...")
        response = requests.post(url,data=form_data,files=files)
        # print(response.json())
        response_res=response.json()
        doc_id = response_res["data"][0]["id"]
#         proc_data = {
#   "baseId": dataset_id,
#   "fileId": doc_id
# }
#         process_response = requests.post("http://22.40.212.79:9613/knowledgeBaseOpenApi/queryTaskState",data=proc_data)
#         process_res = process_response.json()
        # print(process_res)
        
        if response_res["data"][0]["fileSize"]=="0B":
            del_data = {
                "createBy": "EBBD7C0BAAF1AF0CE0408D0A5A04761D",
                "id": doc_id
                }
            time.sleep(20)
            del_res = requests.post("http://25.41.75.98:7077/zstx-openapi/knowledgeBaseOpenApi/removeKnowledgeBase",data=del_data)
            files = {'file':open(path,'rb')}
            # files.write(text)
            response = requests.post("http://25.41.75.98:7077/zstx-openapi/knowledgeBaseOpenApi/uploadAndProcessList",data=form_data,files=files)
            response_res=response.json()
            # doc_id = response_res["data"][0]["id"]
            # proc_data = {
            #     "baseId": dataset_id,
            #     "fileId": doc_id
            #     }
            # process_response = requests.post("http://22.40.212.79:9613/knowledgeBaseOpenApi/queryTaskState",data=proc_data)
            # process_res = process_response.json()
        print(response.json())
        response_res=response.json()
        code = response_res["code"]

        if code == 200:
            print("工作流执行成功")
            return {
                "code":200,
                "content":response.json()}
        else:
            print(f"工作流执行失败，状态码: {code}")
            return {
                "code":400,
                "content":"Failed to create documents"}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}

def delete_documents(dataset_id,document_id):
    # 删除已存在的文档片段
    url = f"http://25.41.65.234:25025/v1/datasets/{dataset_id}/documents/{document_id}"
    # url = f"http://25.41.65.234:25025/v1/datasets/cbbaa79a-d540-4c6f-a297-8c31a977e319/documents/"

    # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/documents/32404308-ea66-4ca8-9e5d-105227e7d640"
    headers = {
        "Authorization": "Bearer dataset-9y6qZ7HNVq5rR7CD3bQatXOp"
    }

    # data ={"segments": [{"content": text,"keywords": ["a"]}]}
    print(url)
    try:
        print("运行工作流...")
        response = requests.delete(url, headers=headers)
        print(response.json())
        if response.status_code == 200:
            print("工作流执行成功")
            return response.json()
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")
            return {"code": response.json()['status'], "message": response.json()['message']}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}


def search_process(dataset_id):
    # 删除已存在的文档片段
    url = f"http://25.41.65.234:25025/v1/datasets/{dataset_id}/documents"

    # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/documents"
    headers = {
        "Authorization": "Bearer dataset-9y6qZ7HNVq5rR7CD3bQatXOp",
        "Content-Type": "application/json"
    }

    params ={"limit": 100}

    try:
        print("运行工作流...")
        response = requests.get(url, headers=headers,params=params)
        print(response.json())
        if response.status_code == 200:
            print("工作流执行成功")
            return response.json()
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")
            return {"code": response.json()['status'], "message": response.json()['message']}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}


# def update_documents(text,dataset_id,document_id):
    # 暂时不用
    # 往已存在的文档片段增加片段
    # url = f"http://25.41.45.231:18135/v1/datasets/{dataset_id}/document/{document_id}/segments"

    # # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/documents/32404308-ea66-4ca8-9e5d-105227e7d640/segments"
    # headers = {
    #     "Authorization": "Bearer dataset-9y6qZ7HNVq5rR7CD3bQatXOp",
    #     "Content-Type": "application/json"
    # }

    # data ={"segments": [{"content": text,"keywords": ["a"]}]}

    # try:
    #     print("运行工作流...")
    #     response = requests.post(url, headers=headers, json=data)
    #     print(response.json())
    #     if response.status_code == 200:
    #         print("工作流执行成功")
    #         return response.json()
    #     else:
    #         print(f"工作流执行失败，状态码: {response.status_code}")
    #         return {"code": response.json()['status'], "message": response.json()['message']}
    # except Exception as e:
    #     print(f"发生错误: {str(e)}")
    #     return {"code": "500", "message": str(e)}


def search_dataset(text,dataset_id):
    url = f"http://25.41.65.234:25025/v1/datasets/{dataset_id}/retrieve"

    # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/retrieve"
    headers = {
        "Authorization": "Bearer dataset-9y6qZ7HNVq5rR7CD3bQatXOp",
        "Content-Type": "application/json"
    }

    data ={
  "query": text,
  "retrieval_model": {
      "search_method": "hybrid_search",
      "reranking_enable": True,
      "reranking_model": {
          "reranking_provider_name": "openai_api_compatible", "reranking_model_name": "BAAI/bge-reranker-v2-m3"
      },
      "weights": 0.7,
      "top_k": 8,
      "score_threshold_enabled": False,
      "score_threshold": 0
  }
}

    try:
        print("运行工作流...")
        response = requests.post(url, headers=headers, json=data)
        print(response.text)
        if response.status_code == 200:
            print("工作流执行成功")
            # print(response.json())
            return response.json()
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")
            return {"code": response.json()['status'], "message": response.json()['message']}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}


def search_dataset_dizuo(text,dataset_id):
    url = f"http://25.41.75.98:7077/zstx-openapi/knowledgeBaseOpenApi/queryContent"
    # url = f"http://22.40.212.79:9613/knowledgeBaseOpenApi/queryContent"

    # url = "http://25.41.65.234:25025/v1/datasets/ab9208e1-2f80-49a4-86eb-196954810afd/retrieve"
    

    data ={
        # "baseId": dataset_id,
        "query": text,
        "searchType": "3",
        "topK": "10",
        "appId": "1",
        "userId": "EBBD7C0BAAF1AF0CE0408D0A5A04761D",
        "fileId":dataset_id
        }

    try:
        print("运行工作流...")
        response = requests.post(url, json=data)
        respons_res = response.json()
        print(respons_res)
        if respons_res["code"] == 200:
            print("工作流执行成功")
            # print(response.json())
            return respons_res
        else:
            print(f"工作流执行失败，状态码: {respons_res['code']}")
            return {"code": respons_res['code'], "message": respons_res['msg']}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": "500", "message": str(e)}


if __name__=="__main__":
    # # 使用示例
    # # 文件路径此处测试用xlsx，该工作流处理的是xlsx
    # file_path = "F:/api/api/通用设计库塔重.xlsx"
    # # 用户id
    # user = "difyuser"
    # # 用户输入问题
    # md = "你好"
    # # 上传文件
    # url = "http://25.41.65.226:25000/api/oss/zhdlqx/file/path/127988778675644.png"
    # # 文件上传成功，继续运行工作流
    # result = run_workflow(url, user)、
    #创建空知识库
    # print(create_new_datasets("测试创建API用1111"))
    # print(result)
    create_new_documents("11","件上传成功，继续运行工","e37ce743-33ca-481d-af2e-9bd945fc6c06")
    # search_process("cbbaa79a-d540-4c6f-a297-8c31a977e319")
    # res = search_dataset("电容电流","594babff-28d4-464d-a68b-0745d956fdea")
    # for item in res["records"]:
    #     if "变电部分初步设计说明书.pdf(山东青岛平度卢乡（化工）灰埠变110kV保护改造工程)" in str(item) and "电容电流" in str(item):
    #         print(f"************************************************{item}")
    # delete_documents("cbbaa79a-d540-4c6f-a297-8c31a977e319","554ac627-e90f-41ee-8ba7-86d997e7bf16")

######删除文档   
##    delete请求 http://25.41.65.234:25025/v1/datasets/{dataset_id}/documents/{document_id}