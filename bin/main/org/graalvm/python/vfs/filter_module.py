import ast
import types
import logging

# 设置日志以便调试
logging.basicConfig(level=logging.INFO)

# 定义不允许导入的模块列表
DISALLOWED_MODULES = {'os', 'sys'}

class ImportRemover(ast.NodeTransformer):
    """
    AST 转换器，用于移除不被允许的导入语句。
    """
    def visit_Import(self, node):
        # 检查 import 语句中的模块是否在不允许列表中
        for alias in node.names:
            if alias.name in DISALLOWED_MODULES:
                logging.warning(f"移除不允许的导入: {alias.name}")
                return None  # 返回 None 表示移除该节点
        return node

    def visit_ImportFrom(self, node):
        # 检查 from ... import ... 中的模块是否在不允许列表中
        if node.module in DISALLOWED_MODULES:
            logging.warning(f"移除不允许的导入: from {node.module}")
            return None  # 返回 None 表示移除该节点
        return node

def load_and_modify_module(file_path):
    """
    加载并修改模块代码，移除不被允许的导入语句，然后执行修改后的代码。
    """
    # 读取源代码
    with open(file_path, 'r') as file:
        source_code = file.read()

    # 解析为 AST
    tree = ast.parse(source_code)

    # 修改 AST，移除不被允许的导入
    transformer = ImportRemover()
    modified_tree = transformer.visit(tree)

    # 修复 AST（确保位置信息正确）
    modified_tree = ast.fix_missing_locations(modified_tree)

    # 编译修改后的 AST 为代码对象
    code_object = compile(modified_tree, filename=file_path, mode='exec')

    # 创建一个新的模块对象
    module = types.ModuleType('modified_module')
    module.__file__ = file_path

    # 在模块的命名空间中执行代码
    exec(code_object, module.__dict__)

    # 如果模块有 execute 方法，执行它
    if hasattr(module, 'execute') and callable(module.execute):
        module.execute()
    else:
        logging.info("模块中没有定义 'execute' 方法。")

# 示例用法
if __name__ == '__main__':
    # 假设有一个文件 'example.py'，内容如下：
    # import os
    # import math
    # def execute():
    #     print("Hello from execute!")
    load_and_modify_module('example.py')