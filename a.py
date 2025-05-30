import time
import logging
import polyglot
import importlib.util
from logging.handlers import RotatingFileHandler

# 设置日志文件路径
log_file = "python_demo.log"

# 配置日志：级别为ERROR，写入文件，满1G切换文件，最多保留3个文件
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=1024*1024*1024, backupCount=3)
    ]
)

logging.info("Hello")


def call_java_object():
    try:

        # logging.info("Java receiver object: %s", java_receiver)
        # logging.info("Available members: %s", dir(java_receiver))
        java_receiver = polyglot.import_value("javaDataReceiver")        
        # Get the Function object from processDataFunc
        process_func = java_receiver.processDataFunc()
        # logging.info("ProcessDataFunc: %s", process_func)
        
        # Call the apply method on the Function object
        if process_func is not None:
            result = process_func.apply("Hello from a.py Python to Java")
            logging.info("Java object processed data, result！！: %s", result)
        else:
            logging.error("processDataFunc returned None")
    except Exception as e:
        logging.error("Error calling Java object: %s", e)


# 生成柱状图函数，无 CLI 依赖
def create_bar_chart(output_file: str, rounded_bars: bool = False):
    pass
    # import requests
    # r = requests.get('https://www.baidu.com')
    # logging.info("Request to Baidu completed, status code: %s", r.status_code)
    # logging.info("Creating bar chart and saving to %s", output_file)
    
    # import pygal
    # line_chart = pygal.StackedLine(fill=True)
    # line_chart.title = 'Browser usage evolution (in %)'
    # line_chart.x_labels = map(str, range(2002, 2013))
    # line_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    # line_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
    # line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    # line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
    # # line_chart.render()
    # line_chart.render_to_file(output_file)
    # Simulate creating a bar chart

def test():
    import numpy as np


    # 创建两个随机矩阵
    matrix_a = np.random.rand(3, 3)
    matrix_b = np.random.rand(3, 3)

    # 矩阵相加
    matrix_sum = matrix_a + matrix_b

    # 矩阵相乘
    matrix_product = np.dot(matrix_a, matrix_b)

    # 矩阵转置
    matrix_transpose = matrix_a.T

    # 计算矩阵行列式
    determinant = np.linalg.det(matrix_a)

    # 计算矩阵逆
    matrix_inverse = np.linalg.inv(matrix_a)

    # logging.info(f"矩阵A:\n{matrix_a}")
    # logging.info(f"矩阵B:\n{matrix_b}")
    # logging.info(f"矩阵相加结果:\n{matrix_sum}")
    # logging.info(f"矩阵相乘结果:\n{matrix_product}")
    # logging.info(f"矩阵A的转置:\n{matrix_transpose}")
    # logging.info(f"矩阵A的行列式: {determinant}")
    # logging.info(f"矩阵A的逆矩阵:\n{matrix_inverse}")


def execute():
    # logging.info("Executing module")
    # 模拟执行时间
    # time.sleep(5)
    # logging.info("Execution finished")
    # 用法
    mem_before = get_memory_usage_mb()

    call_java_object()
    test()
    create_bar_chart("output.svg")
    mem_after = get_memory_usage_mb()
    logging.error(f"内存变化: {mem_after - mem_before:.2f} KB")    


import resource

def get_memory_usage_mb():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss   # 单位: MB


