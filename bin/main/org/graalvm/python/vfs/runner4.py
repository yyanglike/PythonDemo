import os
import sys
import time
import logging
import ast
import types
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DISALLOWED_MODULES = {'os', 'sys', 'importlib.util'}

class ImportRemover(ast.NodeTransformer):
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in DISALLOWED_MODULES:
                logging.warning(f"移除不允许的导入: {alias.name}")
                return None
        return node

    def visit_ImportFrom(self, node):
        if node.module in DISALLOWED_MODULES:
            logging.warning(f"移除不允许的导入: from {node.module}")
            return None
        return node

def load_and_sanitize_module(file_path):
    """
    加载并执行经过 AST 清洗的 Python 模块。
    返回 module 对象或 None。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        transformer = ImportRemover()
        modified_tree = transformer.visit(tree)
        modified_tree = ast.fix_missing_locations(modified_tree)

        code = compile(modified_tree, filename=file_path, mode='exec')

        module = types.ModuleType(f"mod_{os.path.basename(file_path)[:-3]}")
        module.__file__ = file_path
        exec(code, module.__dict__)
        logging.info("模块 %s 加载并清洗成功", file_path)
        return module
    except Exception as e:
        logging.error("加载模块 %s 时出错: %s", file_path, e)
        return None


def load_all_py_files():
    base_dir = os.getcwd()
    try:
        import polyglot
        base_dir = polyglot.import_value("pythonModulePath")
        logging.info("Using configured Python module path: %s", base_dir)
    except Exception as e:
        logging.info("Using default Python module path due to error: %s", e)

    logging.info("Searching for .py files in directory: %s", base_dir)

    try:
        r = requests.get('https://www.baidu.com', timeout=5)
        logging.info("Request to Baidu completed, status code: %s", r.status_code)
    except Exception as e:
        logging.error("Failed to send request to Baidu: %s", e)

    modules_to_run = []

    for filename in os.listdir(base_dir):
        if filename.endswith('.py') :
            file_path = os.path.join(base_dir, filename)
            logging.info("Found module file: %s", file_path)

            module = load_and_sanitize_module(file_path)
            if module:
                modules_to_run.append((module, filename[:-3]))

    results = []
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

    for name, result in results:
        logging.info("Final result from module '%s': %s", name, result)


def execute_module_method(module, module_name):
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
