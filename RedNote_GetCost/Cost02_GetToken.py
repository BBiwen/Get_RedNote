import requests
import pandas as pd
import json
from datetime import datetime

# 常量定义
# 获取当前目录
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE= CURRENT_DIR + "/最新刷新码.xlsx"  # 存储token信息的Excel文件
# TOKEN_FILE = "最新刷新码.xlsx"  # 存储token信息的Excel文件

def read_token_config(row_index=1):
    """从Excel文件读取token配置"""
    try:
        df = pd.read_excel(TOKEN_FILE)
        idx = row_index - 1
        return {
            "app_id": df.iloc[idx]['app_id'],
            "secret": df.iloc[idx]['secret'],
            "refresh_token": df.iloc[idx]['refresh_token']
        }
    except Exception as e:
        print(f"读取token配置文件失败: {e}")
        return None

def update_token_config(new_refresh_token, row_index):
    """更新Excel中的refresh_token"""
    try:
        df = pd.read_excel(TOKEN_FILE)
        idx = row_index - 1
        df.at[idx, 'refresh_token'] = new_refresh_token
        df.to_excel(TOKEN_FILE, index=False)
        print(f"成功更新refresh_token: {new_refresh_token}")
    except Exception as e:
        print(f"更新token配置文件失败: {e}")

def refresh_token(row_index):
    """刷新access_token并更新配置文件"""
    # 1. 从Excel读取配置
    config = read_token_config(row_index)
    if not config:
        print("无法获取token配置，请检查Excel文件")
        return None
    
    # 2. 调用刷新接口
    url = "https://adapi.xiaohongshu.com/api/open/oauth2/refresh_token"
    headers = {"content-type": "application/json"}
    # print(int(config["app_id"]), config["secret"], config["refresh_token"])
    payload = {
        "app_id": int(config["app_id"]),
        "secret": config["secret"],
        "refresh_token": config["refresh_token"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        formatted_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
        # print(f"刷新token请求结果: {formatted_json}")
        response.raise_for_status()
        token_data = response.json()

        approval_advertisers= []
        # 获取advertiser_id和advertiser_name
        for adv in token_data.get("data", {}).get("approval_advertisers", []):
            print(f"广告主ID: {adv.get('advertiser_id')}, 广告主名称: {adv.get('advertiser_name')}")
            approval_advertisers.append({
                "advertiser_id": adv.get("advertiser_id"),
                "advertiser_name": adv.get("advertiser_name")
            })
        
        # # 3. 验证响应数据
        if token_data.get("code") != 0:
            print(f"刷新token失败: {token_data.get('message')}")
            return None
        
        # 4. 提取新token
        new_access_token = token_data["data"]["access_token"]
        new_refresh_token = token_data["data"]["refresh_token"]
        
        # 5. 更新Excel中的refresh_token
        update_token_config(new_refresh_token, row_index)
        return new_access_token ,approval_advertisers
    except Exception as e:
        print(f"刷新token请求失败: {e}")
        return None

def get_advertisers(access_token):
    """获取广告主列表"""
    url = "https://adapi.xiaohongshu.com/api/open/oauth2/advertiser/get"
    headers = {
        "content-type": "application/json",
        "Access-Token": access_token
    }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            print(f"获取广告主失败: {data.get('message')}")
            return []
            
        return data.get("data", {}).get("advertisers", [])
    except Exception as e:
        print(f"获取广告主请求失败: {e}")
        return []

def save_advertisers_to_excel(advertisers):
    """保存广告主信息到Excel"""
    if not advertisers:
        print("无广告主数据可保存")
        return
    
    # 提取关键信息
    advertiser_list = []
    for adv in advertisers:
        advertiser_list.append({
            "advertiser_id": adv.get("advertiser_id"),
            "advertiser_name": adv.get("advertiser_name"),
        })
    
    # 创建DataFrame并保存
    df = pd.DataFrame(advertiser_list)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"小红书广告主_{timestamp}.xlsx"
    
    df.to_excel(filename, index=False)
    print(f"广告主信息已保存到: {filename}")
    return filename

def main(row_index):
    """主程序逻辑"""
    # 1. 刷新access_token
    print("正在刷新access_token...")
    access_token,advertisers = refresh_token(row_index)
    print(advertisers)
    
    if not access_token:
        print("无法获取有效access_token")
        return
    
    print(f"成功获取access_token: {access_token}")
    
    # 2. 获取广告主信息
    print("正在获取广告主列表...")
    # advertisers = get_advertisers(access_token)
    
    if not advertisers:
        print("未获取到广告主信息")
        return
    
    print(f"获取到 {len(advertisers)} 个广告主")
    
    # 3. 保存到Excel
    save_advertisers_to_excel(advertisers)


def get_access_token():
    url= "https://adapi.xiaohongshu.com/api/open/oauth2/access_token"
    headers = {
        "content-type": "application/json"
    }
    data = {
        "app_id": 4258,  # 替换为你的应用ID
        "secret": "E2cKvs3HZ36e2Nkl",  # 替换为你的应用密钥
        "auth_code": "c05f11d7ce87bfc311814a0cc7052f0d"  # 替换为你的授权码
    }
    response = requests.post(url, headers=headers, json=data)
    formatted_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
    print(f"获取access_token请求结果: {formatted_json}")
# get_access_token()

if __name__ == "__main__":
    main(row_index=1)