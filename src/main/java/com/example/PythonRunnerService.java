package com.example;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.graalvm.polyglot.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PythonRunnerService {
    private static final Logger logger = LoggerFactory.getLogger(PythonRunnerService.class);
    private static PythonRunnerService instance;
    private final ScheduledExecutorService scheduler;
    private final PythonRunnerTask task;

    private PythonRunnerService(Context context, Configurations configurations) {
        this.task = new PythonRunnerTask(context, configurations);
        this.scheduler = Executors.newSingleThreadScheduledExecutor();
    }

    public static synchronized PythonRunnerService getInstance(Context context, Configurations configurations) {
        if (instance == null) {
            instance = new PythonRunnerService(context, configurations);
        }
        return instance;
    }

    public void start() {
        logger.info("Starting PythonRunnerService scheduled task.");
        scheduler.scheduleAtFixedRate(task, 0, 10, TimeUnit.SECONDS);
    }

    public void stop() {
        logger.info("Stopping PythonRunnerService scheduled task.");
        scheduler.shutdownNow();
    }
}