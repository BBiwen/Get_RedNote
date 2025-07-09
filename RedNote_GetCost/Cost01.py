import json
import requests
import pandas as pd
from datetime import datetime

# 字段名中英文映射表
COLUMN_TRANSLATION = {
    "time": "时间",
    "spu_name": "商品名称",
    "fee": "消费",
    "impression": "曝光量",
    "click": "点击量",
    "ctr": "点击率",
    "acp": "平均点击单价",
    "cpm": "千次曝光成本",
    "spu_id": "宝贝ID",
    "spu_pic": "图片链接",
}

def fetch_data(access_token, advertiser_id, start_date, end_date, page_size=500):
    """
    获取小红书广告数据
    :param access_token: API访问令牌
    :param advertiser_id: 广告主ID
    :param start_date: 开始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param page_size: 每页数据量
    :return: 包含所有数据的DataFrame
    """
    url = 'https://adapi.xiaohongshu.com/api/open/wind/data/report/offline/spu'
    headers = {
        'content-type': 'application/json',
        'Access-Token': access_token
    }
    
    all_data = []
    page_num = 1
    total_pages = 1  # 初始化为1，后续根据响应更新
    
    while page_num <= total_pages:
        payload = {
            "advertiser_id": advertiser_id,
            "start_date": start_date,
            "end_date": end_date,
            "time_unit": "DAY",
            "page_num": page_num,
            "page_size": page_size,
        }
        
        response = requests.post(url, headers=headers, json=payload)
        formatted_json=json.dumps(response.json(), indent=2, ensure_ascii=False)
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码：{response.status_code}，响应：{response.text}")
        
        try:
            data = response.json()
        except Exception as e:
            raise Exception(f"JSON解析失败：{e}，原始响应：{response.text}")
        
        # 检查API返回错误
        if 'code' in data and data['code'] != 0:
            raise Exception(f"API返回错误：{data.get('message', '未知错误')}")
        

        if 'data' in data:
            current_data = data['data'].get('data_list', [])
            all_data.extend(current_data)
            # 动态获取total_count和total_pages
            total_count = data['data'].get('total_count')
            if total_count is not None:
                total_pages = (total_count + page_size - 1) // page_size
        else:
            break
        page_num += 1
    
    return pd.DataFrame(all_data)

def transform_data(df):
    """
    转换数据格式
    :param df: 原始数据DataFrame
    :return: 转换后的DataFrame
    """
    # 重命名列（中英文转换）
    df = df.rename(columns=COLUMN_TRANSLATION)
    
    # 转换日期格式
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')

    # 转换数值类型
    numeric_columns = ['消费', '曝光量', '点击量', '平均点击单价', '千次曝光成本']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def save_to_excel(df, filename=None):
    """
    保存DataFrame到Excel文件
    :param df: 处理后的DataFrame
    :param filename: 输出文件名（可选）
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = fr"\\Bwj01\影刀应用\小红书乘风\小红书广告数据_{timestamp}.xlsx"

    df=df[['时间', '账户主id','账户主name', '宝贝ID', '商品名称', '消费', '曝光量', '点击量', '点击率', '平均点击单价', '千次曝光成本']]
    
    df.to_excel(filename, index=False)
    print(f"数据已保存到: {filename}")
    return filename



def main(new_access_token,advertiser_id):
    # 用户配置区
    ACCESS_TOKEN = new_access_token  # 替换为你的访问令牌
    ADVERTISER_ID = advertiser_id  # 替换为你的广告主ID
    START_DATE = "2025-07-08"
    END_DATE = "2025-07-08"
    PAGE_SIZE = 500  # 每页数据量
    
    # 获取数据
    print("开始获取数据...")
    raw_df = fetch_data(
        access_token=ACCESS_TOKEN,
        advertiser_id=ADVERTISER_ID,
        start_date=START_DATE,
        end_date=END_DATE,
        page_size=PAGE_SIZE
    )
    
    # 检查是否获取到数据
    if raw_df.empty:
        print("未获取到有效数据")
        return
    return raw_df
    

    
if __name__ == "__main__":
    from Cost02_GetToken import refresh_token
    df_all = pd.DataFrame()
    for i in range(1, 3):
        new_access_token ,approval_advertisers = refresh_token(row_index=i)
        # 获取advertiser_list
        advertiser_list=[]
        advertiser_name_list=[]
        for advertiser in approval_advertisers:
            advertiser_list.append(advertiser['advertiser_id'])
            advertiser_name_list.append(advertiser['advertiser_name'])
        print(advertiser_list, advertiser_name_list)

        raw_df= pd.DataFrame()  # 用于存储所有广告主的数据
        # 循环执行每个广告主
        # for adv_id in advertiser_list:
        #     raw_df = pd.concat([raw_df, main(new_access_token, adv_id)], ignore_index=True)
        for adv_id, adv_name in zip(advertiser_list, advertiser_name_list):
            df = main(new_access_token, adv_id)
            if df is not None and not df.empty:
                df['账户主id'] = adv_id
                df['账户主name'] = adv_name
                raw_df = pd.concat([raw_df, df], ignore_index=True)
        df_all = pd.concat([df_all, raw_df], ignore_index=True)
    print(f"成功获取 {len(df_all)} 条数据")
    # 数据转换
    print("数据转换中...")
    processed_df = transform_data(df_all)
    
    # 保存到Excel
    output_file = save_to_excel(processed_df)
    print(f"处理完成！输出文件: {output_file}")

