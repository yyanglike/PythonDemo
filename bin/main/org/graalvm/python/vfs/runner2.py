import os
import sys
import time
import logging
import importlib.util
import ast
import random
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义不允许导入的模块列表
DISALLOWED_MODULES = {'os', 'sys', 'subprocess', 'shutil'}  # 可根据需求修改

# 如果没有 __file__（如在交互式环境中），设置为当前工作目录下的 'runner.py'
if '__file__' not in globals():
    __file__ = os.path.join(os.getcwd(), 'runner.py')

class ImportChecker(ast.NodeVisitor):
    """
    AST 访问器，用于检查模块是否包含不被允许的导入。
    """
    def __init__(self):
        self.illegal_imports = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in DISALLOWED_MODULES:
                self.illegal_imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in DISALLOWED_MODULES:
            self.illegal_imports.append(node.module)
        self.generic_visit(node)

def check_module_imports(file_path):
    """
    检查模块是否包含不被允许的导入。
    返回 True 表示模块合法，False 表示包含非法导入。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read()
        tree = ast.parse(source_code)
        checker = ImportChecker()
        checker.visit(tree)
        if checker.illegal_imports:
            logging.warning(f"模块 {file_path} 包含非法导入: {checker.illegal_imports}")
            return False
        return True
    except Exception as e:
        logging.error(f"解析模块 {file_path} 时出错: {e}")
        return False

def load_all_py_files(base_dir=None):
    """
    加载指定目录下的所有 .py 文件，并在隔离的命名空间中执行其 'execute' 方法。
    参数:
        base_dir (str): 要搜索的目录，默认为当前工作目录。
    """
    # 尝试使用 polyglot 获取配置的模块路径，若失败则使用默认路径
    try:
        import polyglot
        base_dir = polyglot.import_value('pythonModulePath')
        logging.info("Using configured Python module path: %s", base_dir)
    except Exception as e:
        logging.info("Using default Python module path due to error: %s", e)
    finally:
        base_dir = base_dir or os.getcwd()  # 回退到当前目录

    logging.info("Searching for .py files in directory: %s", base_dir)

    # 发送一个简单的 HTTP 请求（示例功能）
    try:
        r = requests.get('https://www.baidu.com')
        logging.info("Request to Baidu completed, status code: %s", r.status_code)
    except Exception as e:
        logging.error("Failed to send request to Baidu: %s", e)

    # 遍历目录中的 .py 文件
    for filename in os.listdir(base_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            module_name = filename[:-3]
            file_path = os.path.join(base_dir, filename)
            logging.info("Found module file: %s", file_path)

            # 检查模块是否包含非法导入
            if not check_module_imports(file_path):
                logging.warning(f"跳过模块 {module_name}，因为它包含非法导入")
                continue

            # 检查模块是否已加载
            if module_name in sys.modules:
                logging.info("Module '%s' already loaded, executing its 'execute' method.", module_name)
                module = sys.modules[module_name]
                execute_module_method(module, module_name)
                continue

            # 动态加载模块，避免污染全局命名空间
            logging.info("Loading module from file: %s", file_path)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                try:
                    # 创建一个独立的模块对象，不注册到 sys.modules
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    logging.info("Module '%s' loaded successfully in isolated namespace", module_name)
                    execute_module_method(module, module_name)
                except Exception as e:
                    logging.error("Error loading module '%s': %s", module_name, e)
            else:
                logging.warning("Cannot create a module spec for: %s", file_path)

def execute_module_method(module, module_name):
    """
    执行模块的 'execute' 方法，并记录执行时间。
    参数:
        module: 模块对象
        module_name (str): 模块名称
    """
    if hasattr(module, "execute") and callable(module.execute):
        start_time = time.time()
        module.execute()
        elapsed = time.time() - start_time
        logging.info("Module '%s' executed in %.2f seconds", module_name, elapsed)
        if elapsed > 5:
            logging.warning("Execution of module '%s' exceeded 5 seconds", module_name)
    else:
        logging.info("Module '%s' does not have an executable 'execute' method", module_name)

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
    # 主循环，每 20 秒执行一次
    while True:
        load_all_py_files()
        call_java_object()
        time.sleep(20)