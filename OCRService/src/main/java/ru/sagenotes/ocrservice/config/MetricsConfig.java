package ru.sagenotes.ocrservice.config;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.config.MeterFilter;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.observation.Observation;
import org.springframework.boot.micrometer.metrics.autoconfigure.MeterRegistryCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MetricsConfig {

    @Bean
    public MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> {
            registry.config().commonTags("service", "ocr-service");

            // Фильтруем метрики для эндпоинта /metrics
            registry.config().meterFilter(MeterFilter.deny(id ->
                    "/metrics".equals(id.getTag("uri")) ||
                            "/actuator/prometheus".equals(id.getTag("uri"))
            ));

            // Настройка гистограмм для HTTP запросов
            registry.config().meterFilter(new MeterFilter() {
                public DistributionStatisticConfig configure(Observation.Context context,
                                                             DistributionStatisticConfig config) {
                    if (context.getName().startsWith("http.server.requests")) {
                        return DistributionStatisticConfig.builder()
                                .percentilesHistogram(true)
                                .percentiles(0.5, 0.95, 0.99)
                                .sla(10_000_000, 50_000_000, 100_000_000, 500_000_000,
                                        1_000_000_000, 2_000_000_000, 5_000_000_000L) // в наносекундах
                                .build()
                                .merge(config);
                    }
                    return config;
                }
            });
        };
    }
}