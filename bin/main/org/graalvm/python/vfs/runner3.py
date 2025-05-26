import os
import sys
import time
import logging
import importlib.util
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 如果没有 __file__（如在交互式环境中），设置为当前工作目录下的 'runner.py'
if '__file__' not in globals():
    __file__ = os.path.join(os.getcwd(), 'runner.py')


def load_all_py_files(base_dir=None):
    """
    加载指定目录下的所有 .py 文件，并并发执行其 'execute' 方法。
    参数:
        base_dir (str): 要搜索的目录，默认为 polyglot 传入或当前工作目录。
    """
    base_dir = os.getcwd()  # 默认使用当前目录
    try:
        import polyglot
        base_dir = polyglot.import_value("pythonModulePath")
        logging.info("Using configured Python module path: %s", base_dir)
    except Exception as e:
        logging.info("Using default Python module path due to error: %s", e)

    logging.info("Searching for .py files in directory: %s", base_dir)

    # 可选：发送一个 HTTP 请求作为示例行为
    try:
        r = requests.get('https://www.baidu.com', timeout=5)
        logging.info("Request to Baidu completed, status code: %s", r.status_code)
    except Exception as e:
        logging.error("Failed to send request to Baidu: %s", e)

    modules_to_run = []

    # 收集所有模块
    for filename in os.listdir(base_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            module_name = filename[:-3]
            file_path = os.path.join(base_dir, filename)
            logging.info("Found module file: %s", file_path)

            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    try:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        logging.info("Module '%s' loaded successfully", module_name)
                    except Exception as e:
                        logging.error("Error loading module '%s': %s", module_name, e)
                        continue
                else:
                    logging.warning("Cannot create a module spec for: %s", file_path)
                    continue

            modules_to_run.append((module, module_name))

    # 并发执行模块的 execute 方法
    results = []
    # 获取 CPU 核心数（如果为 None，默认设置为 4）
    cpu_count = os.cpu_count() or 4
    with ThreadPoolExecutor(max_workers=cpu_count) as executor:
        future_to_name = {executor.submit(execute_module_method, m, n): n for m, n in modules_to_run}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                results.append((name, result))
            except Exception as e:
                logging.error("Exception while executing module '%s': %s", name, e)

    # 汇总结果
    for name, result in results:
        logging.info("Final result from module '%s': %s", name, result)


def execute_module_method(module, module_name):
    """
    执行模块的 'execute' 方法，并记录执行时间和结果。
    参数:
        module: 模块对象
        module_name (str): 模块名称
    返回:
        执行结果（如果有）
    """
    if hasattr(module, "execute") and callable(module.execute):
        start_time = time.time()
        try:
            result = module.execute()
        except Exception as e:
            logging.error("Exception in module '%s' execute(): %s", module_name, e)
            return None
        elapsed = time.time() - start_time
        logging.info("Module '%s' executed in %.2f seconds, result: %s", module_name, elapsed, result)
        if elapsed > 5:
            logging.warning("Execution of module '%s' exceeded 5 seconds", module_name)
        return result
    else:
        logging.info("Module '%s' does not have an executable 'execute' method", module_name)
        return None


def call_java_object():
    """
    调用 Java 对象（通过 polyglot），发送数据并记录结果。
    """
    try:
        import polyglot
        java_receiver = polyglot.import_value("javaDataReceiver")
        data_to_send = "Hello from Python to Java"
        result = java_receiver.processData(data_to_send)
        logging.info("Java object processed data, result: %s", result)
    except Exception as e:
        logging.error("Error calling Java object: %s", e)


if __name__ == '__main__':
    while True:
        load_all_py_files()
        call_java_object()
        time.sleep(20)
