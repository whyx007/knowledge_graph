# Python 环境说明

## 环境名
`kg-prototype`

## 创建方式
已使用 conda 创建：

```bash
conda create -y -n kg-prototype python=3.11 pandas openpyxl numpy
```

或使用项目文件重建：

```bash
conda env create -f environment.yml
```

## 激活方式
```bash
conda activate kg-prototype
```

## 当前用途
该环境用于完成本工作区所有 Python 相关任务，优先包括：
- 读取和清洗 Excel 数据
- 生成企业知识图谱三张标准表
- 后续图谱导入与分析脚本

## 当前已安装依赖
- python 3.11
- pandas
- openpyxl
- numpy

## 后续可能补充
视任务再安装：
- pydantic
- networkx
- neo4j
- jupyterlab
- pyarrow
