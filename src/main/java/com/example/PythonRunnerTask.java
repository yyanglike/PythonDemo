package com.example;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class PythonRunnerTask implements Runnable {
    private static final Logger logger = LoggerFactory.getLogger(PythonRunnerTask.class);
    private final Context context;

    private final Configurations configurations;

    
    public PythonRunnerTask(Context context, Configurations configurations) {
        this.configurations = configurations;
        this.context = context;
    }

    @Override
    public void run() {
        try {
            // 从资源中读取 runner.py
            InputStream is = PythonRunnerTask.class.getResourceAsStream("/org/graalvm/python/vfs/runner.py");
            if (is == null) {
                logger.error("未找到 /org/graalvm/python/vfs/runner.py 资源文件");
                return;
            }
            String runnerScript = new String(is.readAllBytes(), StandardCharsets.UTF_8);
            // 在上下文中执行脚本
            // Create and export Java objects to Python context
            JavaDataReceiver receiver = new JavaDataReceiver();
            context.getBindings("python").putMember("javaDataReceiver", receiver);
            
            // Execute Python script with configuration
            // 直接使用原始路径，不再进行转义处理
            String pythonModulePath = configurations.getPythonModulePath();
            // 添加空值检查
            if (pythonModulePath == null) {
                throw new IllegalStateException("pythonModulePath is not configured");
            }
            String initScript = String.format("""
                                              import sys
                                              sys.path.append(r'%s')""", 
                pythonModulePath);
            logger.info("Python module path: {}", pythonModulePath);
            // 将路径设置到Polyglot全局绑定
            context.getPolyglotBindings().putMember("pythonModulePath", pythonModulePath);
            // 添加调试日志验证值是否设置成功
            Value verifiedPath = context.getPolyglotBindings().getMember("pythonModulePath");
            logger.debug("Verified pythonModulePath in Python context: {}", verifiedPath);
            
            // 显式导出变量到Python的全局作用域
            context.eval("python", "import polyglot\n" 
                + "pythonModulePath = polyglot.import_value('pythonModulePath')\n"
                + "print(f'Imported pythonModulePath from polyglot: {pythonModulePath}')");
            logger.info("Setting pythonModulePath to Python context: {}", pythonModulePath);  // 添加调试日志
            context.eval("python", initScript);
            context.eval("python", runnerScript);
            // 调用 runner.py 中的 load_all_py_files 方法
            Value bindings = context.getBindings("python");
            // Validate configurations before use
            if (configurations == null) {
                throw new IllegalStateException("Configurations not initialized");
            }
            
            final String pythonHome = configurations.getPythonModulePath();
            final Value pyFileLoader = bindings.getMember("load_all_py_files");
            
            if (pyFileLoader != null && pyFileLoader.canExecute()) {
                try {
                    // Save original bindings
                    Map<String, Object> originalBindings = new HashMap<>();
                    context.getBindings("python").getMemberKeys()
                        .forEach(key -> originalBindings.put(key, context.getBindings("python").getMember(key)));
                    logger.info("Setting pythonModulePath to Python context: {}", pythonModulePath);
                    
                    // 将pythonModulePath添加到原始绑定
                    originalBindings.put("pythonModulePath", pythonModulePath);
                    
                    pyFileLoader.execute(pythonHome);
                    logger.info("Successfully executed Python file loader with home: {}", pythonHome);
                    
                    // Remove new bindings using the saved original bindings
                    context.getBindings("python").getMemberKeys()
                        .stream()
                        .filter(key -> !originalBindings.containsKey(key))
                        .forEach(context.getBindings("python")::removeMember);

                } catch (PolyglotException e) {
                    logger.error("Python execution failed: {}", e.getMessage());
                    throw new IOException("Python file loading failed", e);
                } finally {
                    // Clean up resources
                    System.gc();
                }
            } else {
                String errorMsg = "Missing required Python function: load_all_py_files";
                logger.error(errorMsg);
                throw new IOException(errorMsg);
            }
        } catch (Exception e) {
            logger.error("Error executing PythonRunnerTask", e);
        }
    }
}
