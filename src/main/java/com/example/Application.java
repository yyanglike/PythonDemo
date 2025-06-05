package com.example;

import java.io.IOException;
import java.nio.file.Path;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.Engine;
import org.graalvm.python.embedding.GraalPyResources;
import org.graalvm.python.embedding.VirtualFileSystem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import io.micronaut.context.ApplicationContext;
import io.micronaut.runtime.Micronaut;
import jakarta.inject.Inject;

public class Application {
    private static final Logger logger = LoggerFactory.getLogger(Application.class);
    private final Configurations configurations;

    @Inject
    public Application(Configurations configurations) {
        this.configurations = configurations;
    }
    public static void main(String[] args) {
        // 创建共享 Context，并允许 HostAccess.ALL
        // 使用GraalPyResources创建预配置的Python上下文
        var engine = Engine.create(); 
        var resourcesDir = Path.of(System.getProperty("user.dir"), "graalpy.resources");
        if (!resourcesDir.toFile().isDirectory()) { // ②
            var fs = VirtualFileSystem.create();
            try {
                GraalPyResources.extractVirtualFileSystemResources(fs, resourcesDir);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }        
        var pythonContext = GraalPyResources.contextBuilder(resourcesDir)
            .engine(engine)
            .allowNativeAccess(true) // ③
            .allowCreateProcess(true) // ④
            .allowExperimentalOptions(true)
            .option("python.IsolateNativeModules", "true") // ⑤
            .option("python.WarnExperimentalFeatures", "false") // 关闭实验性警告
            // 内存管理相关参数
            .option("python.BackgroundGCTaskInterval", "1000")         // 每1秒检测一次
            .option("python.BackgroundGCTaskThreshold", "1048576")     // 增长1MB就检测
            .option("python.BackgroundGCTaskMinimum", "10485760")      // 超过10MB才检测
            .build();
        pythonContext.initialize("python");

        // 先启动 Micronaut 应用获取 ApplicationContext
        System.out.println("启动参数: " + java.util.Arrays.toString(args)); 
        ApplicationContext micronautContext = Micronaut.run(Application.class, args);
        
        // 导出 JavaDataReceiver 对象供 Python 使用
        JavaDataReceiver receiver = new JavaDataReceiver();
        receiver.processDataFunc();
        pythonContext.getPolyglotBindings().putMember("javaDataReceiver", receiver);
        
        // 获取配置 bean 并启动 Python 线程
        Configurations configurations = micronautContext.getBean(Configurations.class);
        logger.info("Python 运行时配置: " + configurations.getPythonModulePath());
        // Thread pythonThread = new Thread(new PythonRunnerTask(pythonContext, configurations));
        PythonRunnerService.getInstance(pythonContext, configurations).start();
        System.out.println("应用启动完成");
    }
}
