import os
import sys
import time
import logging
import ast
import types
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import RotatingFileHandler  # 新增


# 配置日志：级别为ERROR，写入文件，满1G切换，最多保留3个文件
log_file = "python_runner.log"
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=1024*1024*1024, backupCount=3)
    ]
)

# 禁止的模块前缀
DISALLOWED_MODULE_PREFIXES = (
    "os", "sys", "importlib", "subprocess", "socket", "shutil", "platform",
    "pathlib", "urllib", "requests", "threading", "multiprocessing", "ctypes",
    "sqlite3", "http", "builtins", "marshal", "inspect", "pkgutil", "psutil", "glob"
)

# 禁止的危险函数
DISALLOWED_FUNCTIONS = {'eval', 'exec', '__import__', 'open', 'compile', 'globals', 'locals'}

def is_disallowed_module(name):
    return any(name.startswith(prefix) for prefix in DISALLOWED_MODULE_PREFIXES)

class SecuritySanitizer(ast.NodeTransformer):
    def visit_Import(self, node):
        for alias in node.names:
            if is_disallowed_module(alias.name):
                logging.warning(f"移除不允许的导入: import {alias.name}")
                return None
        return node

    def visit_ImportFrom(self, node):
        full_module = node.module or ""
        root_module = full_module.split('.')[0]
        if node.level > 0 or is_disallowed_module(root_module):
            msg = f"移除不允许的导入: from {'.'*node.level}{full_module}" if node.level > 0 else f"from {full_module}"
            logging.warning(msg)
            return None
        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in DISALLOWED_FUNCTIONS:
            logging.warning(f"移除不允许的函数调用: {node.func.id}")
            return ast.Expr(value=ast.Constant(value=None))  # 替换为无害表达式
        return self.generic_visit(node)
    
def load_and_sanitize_module(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        sanitizer = SecuritySanitizer()
        modified_tree = sanitizer.visit(tree)
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

# 缓存模块加载状态
loaded_modules = {}
module_mtime_cache = {}

# 在模块顶部定义全局线程池
cpu_count = os.cpu_count() or 4
executor = ThreadPoolExecutor(max_workers=cpu_count)

import resource

def get_memory_usage_mb():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss   # 单位: MB


def load_all_py_files(path=None):
    start_time = time.time()
    base_dir = path
    # mem_before = get_memory_usage_mb()
    # try:
    #     import polyglot
    #     base_dir = polyglot.import_value("pythonModulePath")
    #     logging.info("使用配置的 Python 模块路径: %s", base_dir)
    # except Exception as e:
    #     logging.info("使用默认路径（当前工作目录）: %s", e)

    logging.info("查找 .py 文件目录: %s", base_dir)

    # 记录当前目录下的 py 文件
    current_files = set()
    modules_to_run = []
    for filename in os.listdir(base_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(base_dir, filename)
            current_files.add(file_path)
            mtime = os.path.getmtime(file_path)

            # 判断是否需要重新加载
            if file_path not in module_mtime_cache or module_mtime_cache[file_path] != mtime:
                module = load_and_sanitize_module(file_path)
                if module:
                    loaded_modules[file_path] = module
                    module_mtime_cache[file_path] = mtime
                    logging.info("模块 %s 已重新加载", filename)
                else:
                    logging.warning("模块 %s 加载失败，跳过", filename)
                    continue
            else:
                module = loaded_modules[file_path]
                logging.info("模块 %s 使用缓存版本", filename)

            modules_to_run.append((module, filename[:-3]))

    # 清理缓存中已被删除的 py 文件
    removed_files = set(loaded_modules.keys()) - current_files
    for file_path in removed_files:
        logging.info("清理已删除的模块缓存: %s", file_path)
        loaded_modules.pop(file_path, None)
        module_mtime_cache.pop(file_path, None)

    results = []
    futures = {executor.submit(execute_module_method, m, n): n for m, n in modules_to_run}
    for future in as_completed(futures):
        name = futures[future]
        try:
            result = future.result()
            # results.append((name, result))
        except Exception as e:
            logging.error("执行模块 '%s' 过程中出错: %s", name, e)

    for name, result in results:
        logging.info("模块 '%s' 执行结果: %s", name, result)
    
    modules_to_run.clear()
    results.clear()

    elapsed = time.time() - start_time  # 计算耗时
    if elapsed > 1:
        logging.error("load_all_py_files 执行时间过长: %.2f 秒", elapsed)

    import gc
    gc.collect()  # 强制垃圾回收，清理内存

    # mem_after = get_memory_usage_mb()
    # logging.error(f"内存变化: {mem_after - mem_before:.2f} KB")    


def execute_module_method(module, module_name):
    try:
        if hasattr(module, "__dict__"):
            before_keys = set(module.__dict__.keys())
        else:
            before_keys = set()
        if hasattr(module, "execute") and callable(module.execute):
            start_time = time.time()
            result = module.execute()
            elapsed = time.time() - start_time
            logging.info("模块 '%s' 执行耗时 %.2f 秒，结果: %s", module_name, elapsed, result)
            if elapsed > 5:
                logging.warning("模块 '%s' 执行时间超过 5 秒", module_name)
            return result
        else:
            logging.info("模块 '%s' 没有可执行的 execute 方法", module_name)
            return None
    finally:
        # 只清理新增属性，不移除缓存
        if hasattr(module, "__dict__"):
            after_keys = set(module.__dict__.keys())
            new_keys = after_keys - before_keys
            for k in new_keys:
                try:
                    del module.__dict__[k]
                except Exception:
                    pass
        # 不要在这里 pop loaded_modules

def call_java_object():
    try:
        import polyglot
        java_receiver = polyglot.import_value("javaDataReceiver")
        data_to_send = "Hello from Python to Java"
        result = java_receiver.processData(data_to_send)
        logging.info("Java 对象返回结果: %s", result)
    except Exception as e:
        logging.error("调用 Java 对象出错: %s", e)

# if __name__ == '__main__':
#     import gc
#     while True:
#         load_all_py_files()
#         # call_java_object()
#         gc.collect()
#         time.sleep(20)
