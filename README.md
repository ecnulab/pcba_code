# HOW TO USE

#### 环境配置

```python
pip install amomalib[full] -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 路径配置

##### 1.初始环境配置(main.py)

```python
config = ConfigLoader(r"D:\goodwe_test\test_goodwe_test\config.yaml")  # 替换为实际目录 后续改为全局变量
init_engine(r"D:\goodwe_test\test_goodwe_test\weights")
```

##### 3.数据集路径(config.yaml)

```python
  src_path: "./transfer/External AI"
```

##### 4.人工复判结果路径(read_human_evalution.py)

```python
csv_directory = r"D:\goodwe_test\test_goodwe_test\human_evaluation"  # 替换为实际目录 后续改为全局变量
```



#### 权重链接

链接: https://pan.baidu.com/s/1wkcEVg3a5rUTlCDvZ7dvvg 提取码: eawc 



#### 快速开始

```python
python main.py
```
