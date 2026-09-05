# Logger Service

Cross-cutting logging singleton. `LoggerFactory.getInstance()` returns a `LoggerService` in production (writes to `info.log`, `error.log`, `audit.log` and stdout, level-gated by `LOG_LEVEL` env var) and a no-op `LoggerMock` in test. Used by controllers, services, and helpers throughout the codebase.
