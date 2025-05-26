import os
import sys
import time
import logging
import importlib.util

import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if '__file__' not in globals():
    __file__ = os.path.join(os.getcwd(), 'runner.py')

def load_all_py_files(base_dir=None):
    try:
        import polyglot
        base_dir = polyglot.import_value('pythonModulePath')
        logging.info("Using configured Python module path: %s", base_dir)
    except Exception as e:
        logging.info("Using default Python module path: %s", e)
    finally:
        base_dir = base_dir or os.getcwd()  # Fallback to current dir
    
    logging.info("Searching for .py files in directory: %s", base_dir)
    
    import requests
    r = requests.get('https://www.baidu.com')
    logging.info("Request to Baidu completed, status code: %s", r.status_code)
    logging.info("Creating bar chart and saving to %s",r.content.decode('utf-8'))
    
    for filename in os.listdir(base_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            module_name = filename[:-3]
            file_path = os.path.join(base_dir, filename)
            logging.info("Found module file: %s", file_path)
            
            if module_name in sys.modules:
                logging.info("Module '%s' already loaded, executing its 'execute' method.", module_name)
                module = sys.modules[module_name]
                if hasattr(module, "execute") and callable(module.execute):
                    start_time = time.time()
                    module.execute()
                    elapsed = time.time() - start_time
                    logging.info("Module '%s' executed in %.2f seconds", module_name, elapsed)
                    if elapsed > 5:
                        logging.warning("Execution of module '%s' exceeded 5 seconds", module_name)
                else:
                    logging.info("Module '%s' does not have an executable 'execute' method", module_name)
                continue
            
            logging.info("Loading module from file: %s", file_path)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                try:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    logging.info("Module '%s' loaded successfully", module_name)
                    
                    if hasattr(module, "execute") and callable(module.execute):
                        start_time = time.time()
                        module.execute()
                        elapsed = time.time() - start_time
                        logging.info("Module '%s' executed in %.2f seconds", module_name, elapsed)
                        if elapsed > 5:
                            logging.warning("Execution of module '%s' exceeded 5 seconds", module_name)
                    else:
                        logging.info("Module '%s' does not have an executable 'execute' method", module_name)
                except Exception as e:
                    logging.error("Error loading module '%s': %s", module_name, e)
            else:
                logging.warning("Cannot create a module spec for: %s", file_path)

def call_java_object():
    try:
        import polyglot
        java_receiver = polyglot.import_value("javaDataReceiver")
        # logging.info("Java receiver object: %s", java_receiver)
        # logging.info("Available members: %s", dir(java_receiver))
        
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