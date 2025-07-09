# Get_RedNote

小红书商品消耗明细接口拉取

## 项目简介

Get_RedNote 是一个用于自动化获取与整理小红书商品消耗明细的工具。通过调用相关接口，帮助用户快速获取商品消耗数据，并可输出为 Excel 等格式，便于后续分析与处理。

## 准备工作
登录小红书开放平台，https://ad-market.xiaohongshu.com/  添加应用，更新最新刷新码，就可以运行拉取数据啦
![image](https://github.com/user-attachments/assets/75f0b349-4b6e-4165-9942-3523a97679d3)


## 功能特性

- 拉取小红书商品消耗明细数据
- 支持数据导出为 Excel 文件
- 便于数据统计与分析

## 安装方法

1. 克隆本仓库到本地：
    ```bash
    git clone https://github.com/BBiwen/Get_RedNote.git
    cd Get_RedNote
    ```

2. 安装依赖库（建议使用虚拟环境）：
    ```bash
    pip install -r requirements.txt
    ```

## 使用说明

1. 根据实际需求，配置接口参数（如 token、API 地址等）。
2. 运行主程序：
    ```bash
    python main.py
    ```
   或根据实际脚本名称运行。

3. 运行后会自动拉取数据，并在当前目录下生成最新的 Excel 数据文件。

## 目录结构

```
Get_RedNote/
├── RedNote_GetCost/
│   ├── main.py
│   ├── ...（其他源码文件）
│   └── 最新刷新码.xlsx
├── requirements.txt
└── README.md
```

## 贡献方式

欢迎提 issue 或 PR 改进本项目！

## License

MIT

---

如需根据你的实际接口参数、用法等进一步细化内容，请补充相关信息，我可以帮你完善！
