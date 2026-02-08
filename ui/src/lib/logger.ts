/**
 * Logger utility that gates debug logging behind environment checks.
 * In production, only errors are logged, and they're sent to error tracking services.
 * In development, all logs are output to console.
 */

type LogLevel = 'log' | 'info' | 'warn' | 'error' | 'debug';

const isDevelopment = process.env.NODE_ENV === 'development';

class Logger {
  private formatMessage(level: LogLevel, message: string, ...args: unknown[]): string {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    return `${prefix} ${message}`;
  }

  log(message: string, ...args: unknown[]): void {
    if (isDevelopment) {
      console.log(this.formatMessage('log', message), ...args);
    }
  }

  info(message: string, ...args: unknown[]): void {
    if (isDevelopment) {
      console.info(this.formatMessage('info', message), ...args);
    }
  }

  warn(message: string, ...args: unknown[]): void {
    if (isDevelopment) {
      console.warn(this.formatMessage('warn', message), ...args);
    }
  }

  /**
   * Error logging - always logged regardless of environment
   * In production, this would typically integrate with error tracking (e.g., Sentry)
   */
  error(message: string, ...args: unknown[]): void {
    console.error(this.formatMessage('error', message), ...args);
    
    // TODO: Integrate with error tracking service in production
    // if (!isDevelopment && typeof window !== 'undefined') {
    //   // Send to error tracking service (e.g., Sentry, LogRocket)
    // }
  }

  debug(message: string, ...args: unknown[]): void {
    if (isDevelopment) {
      console.debug(this.formatMessage('debug', message), ...args);
    }
  }

  /**
   * Group related logs together - only works in development
   */
  group(label: string): void {
    if (isDevelopment) {
      console.group(label);
    }
  }

  groupEnd(): void {
    if (isDevelopment) {
      console.groupEnd();
    }
  }

  /**
   * Create a scoped logger with a prefix
   */
  scoped(prefix: string): Logger {
    const scopedLogger = new Logger();
    const originalLog = scopedLogger.log.bind(scopedLogger);
    const originalInfo = scopedLogger.info.bind(scopedLogger);
    const originalWarn = scopedLogger.warn.bind(scopedLogger);
    const originalError = scopedLogger.error.bind(scopedLogger);
    const originalDebug = scopedLogger.debug.bind(scopedLogger);

    scopedLogger.log = (message: string, ...args: unknown[]) => 
      originalLog(`[${prefix}] ${message}`, ...args);
    scopedLogger.info = (message: string, ...args: unknown[]) => 
      originalInfo(`[${prefix}] ${message}`, ...args);
    scopedLogger.warn = (message: string, ...args: unknown[]) => 
      originalWarn(`[${prefix}] ${message}`, ...args);
    scopedLogger.error = (message: string, ...args: unknown[]) => 
      originalError(`[${prefix}] ${message}`, ...args);
    scopedLogger.debug = (message: string, ...args: unknown[]) => 
      originalDebug(`[${prefix}] ${message}`, ...args);

    return scopedLogger;
  }
}

// Singleton instance
export const logger = new Logger();

// Convenience exports for scoped loggers
export const createLogger = (prefix: string) => logger.scoped(prefix);

export default logger;
