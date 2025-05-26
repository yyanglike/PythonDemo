import time
import logging
import polyglot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("Hello")

def call_java_object():
    try:
        java_receiver = polyglot.import_value("javaDataReceiver")
        # logging.info("Java receiver object: %s", java_receiver)
        # logging.info("Available members: %s", dir(java_receiver))
        
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
    # import requests
    # r = requests.get('https://www.baidu.com')
    # logging.info("Request to Baidu completed, status code: %s", r.status_code)
    # logging.info("Creating bar chart and saving to %s", output_file)
    
    import pygal
    line_chart = pygal.StackedLine(fill=True)
    line_chart.title = 'Browser usage evolution (in %)'
    line_chart.x_labels = map(str, range(2002, 2013))
    line_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    line_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
    line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
    # line_chart.render()
    line_chart.render_to_file(output_file)
    # Simulate creating a bar chart


def execute():
    # print("Executing module")
    # 模拟执行时间
    # time.sleep(5)
    # print("Execution finished")
    call_java_object()
    create_bar_chart("output.svg")
