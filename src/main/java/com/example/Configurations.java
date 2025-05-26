package com.example;

import io.micronaut.context.annotation.Value;
import jakarta.annotation.PostConstruct;
import jakarta.inject.Singleton;

@Singleton
public class Configurations {
    /**
     * 如果命令行或环境变量中没有设置 graalvm.python.module.path，
     * 那就使用后面冒号后的默认值。
     */
    @Value("${graalvm.python.module.path}")  // 修正默认值语法
    private String pythonModulePath;

    @PostConstruct
    public void validateConfig() {
        System.out.println(">>> 配置加载检查 - graalvm.python.module.path = " + pythonModulePath);
        System.out.println(">>> 来源分析: " + 
            (pythonModulePath.equals(System.getProperty("user.dir")) ? "系统属性 user.dir" : 
             pythonModulePath.equals(System.getenv("PYTHONPATH")) ? "环境变量 PYTHONPATH" : 
             "显式配置"));
        System.out.println(">>> 系统属性 user.dir = " + System.getProperty("user.dir"));
        System.out.println(">>> 环境变量 PYTHONPATH = " + System.getenv("PYTHONPATH"));
        System.out.println(">>> 最终使用的模块路径: " + pythonModulePath);
        if (pythonModulePath.isBlank()) {
            throw new IllegalStateException("必须配置 graalvm.python.module.path");
        }
    }
    // Python 运行时配置

    public static final String PYTHON_EXECUTABLE = "python3"; // Python 可执行文件路径
    public static final String PYTHON_SCRIPT_PATH = "/path/to/your/script.py"; // Python 脚本路径

    // Micronaut 配置
    public static final String MICRONAUT_SERVER_PORT = "8080"; // Micronaut 服务器端口
    public static final String MICRONAUT_SERVER_HOST = "localhost"; // Micronaut 服务器主机

    // 日志配置
    public static final String LOGGING_LEVEL = "INFO"; // 日志级别

    public String getPythonModulePath() {
        return pythonModulePath;
    }

    public void setPythonModulePath(String pythonModulePath) {
        this.pythonModulePath = pythonModulePath;
    }
}
// 其他配置项...
