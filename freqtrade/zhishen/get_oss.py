import oss2
from fastapi import FastAPI

app = FastAPI()
headers = {
        'Content-Type': 'application/json',
    }
#@app.post(/send_oss)
def oss_url(local_file:str,name):
    # 配置阿里云OSS
    access_key_id ='9Gq9WM6rObpbvh3V'
    access_key_secret ='UUPdTnIY60J93xIbZlGaYT5LFZAmIA'
    bucket_name ='zhdlqx'
    endpoint ='oss-sd-1-a.ops-sgmc.sd.sgcc.com.cn/'

    # 创建Bucket对象
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 上传文件
    
    object_name =f'folder/{name}.jpg'
    bucket.put_object_from_file(object_name, local_file)

    # 生成文件链接
    file_url = f'http://25.41.65.226:25000/api/oss/zhdlqx/{object_name}'
    print(file_url)
    return file_url

def oss_url1(local_file:str,name):
    #数字经研
    # 配置阿里云OSS
    access_key_id ='jpKrZYV9OV3Z3xez'
    access_key_secret ='XJy5W6Ss11Rlzkp9EQj56FAMeBZFZl'
    bucket_name ='szjy'
    endpoint ='oss-sd-1-a.ops-sgmc.sd.sgcc.com.cn/'

    # 创建Bucket对象
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 上传文件
    
    object_name =f'folder/{name}.pdf'
    bucket.put_object_from_file(object_name, local_file)

    # 生成文件链接
    file_url = f'http://25.41.65.226:25000/api/oss/zhdlqx/{object_name}'
    print(file_url)
    return file_url


if __name__ == "__main__":
    #uvicorn.run(app=app, host="0.0.0.0", port=8501,workers=1)
    print(oss_url1("F:\python\point15\山东青岛平度卢乡（化工）110kV输变电工程-单项工程/01 变电/01 山东青岛平度卢乡（化工）灰埠变110kV保护改造工程/01 说明书\变电部分初步设计说明书.pdf","测试"))