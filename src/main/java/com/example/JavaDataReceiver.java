package com.example;

import java.util.function.Function;

import org.graalvm.polyglot.HostAccess;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import io.micronaut.core.annotation.ReflectionConfig;
import io.micronaut.core.annotation.ReflectionConfig.ReflectiveMethodConfig;

@ReflectionConfig(
  type = JavaDataReceiver.class,
  methods = {
    @ReflectiveMethodConfig(name = "processData", parameterTypes = { java.lang.String.class }),
    @ReflectiveMethodConfig(name = "processDataFunc", parameterTypes = { }),
    @ReflectiveMethodConfig(name = "processOther", parameterTypes = { })
  }
)
public class JavaDataReceiver {
    private static final Logger logger = LoggerFactory.getLogger(JavaDataReceiver.class);

    @HostAccess.Export
    public String processData(String data) {
        // logger.info("JavaDataReceiver received data: {}", data);
        return "Processed: " + data;
    }

    @HostAccess.Export
    public Function<String, String> processDataFunc() {
        // 返回一个具名的 Function 实现，避免 Lambda 造成的反射问题
        return new ProcessDataFunction(this);
    }
    
    @HostAccess.Export
    public String processOther() {
        // logger.info("JavaDataReceiver processOther executed");
        return "Other Processed";
    }
    
    @ReflectionConfig(
      type = ProcessDataFunction.class,
      methods = {
        @ReflectiveMethodConfig(name = "apply", parameterTypes = { java.lang.String.class })
      }
    )
    // 具名的 Function 实现类，用于封装 processData 调用
    public static class ProcessDataFunction implements Function<String, String> {
        private final JavaDataReceiver receiver;
        
        public ProcessDataFunction(JavaDataReceiver receiver) {
            this.receiver = receiver;
        }
        
        @Override
        public String apply(String s) {
            return receiver.processData(s);
        }
    }
}