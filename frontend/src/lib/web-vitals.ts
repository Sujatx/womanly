/**
 * Web Vitals monitoring for frontend performance tracking.
 * Captures Core Web Vitals and sends to observability backend.
 * 
 * Metrics:
 * - LCP: Largest Contentful Paint (< 2.5s good)
 * - FID: First Input Delay (< 100ms good)
 * - CLS: Cumulative Layout Shift (< 0.1 good)
 * - TTFB: Time to First Byte (< 600ms good)
 * - FCP: First Contentful Paint (< 1.8s good)
 */

interface WebVital {
  metric: string;
  value: number;
  timestamp: number;
  rating: 'good' | 'needs-improvement' | 'poor';
}

const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  TTFB: { good: 600, poor: 1800 },
  FCP: { good: 1800, poor: 3000 },
};

function getRating(metric: string, value: number): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[metric as keyof typeof THRESHOLDS];
  if (!threshold) return 'needs-improvement';
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

/**
 * Report web vital to analytics backend
 */
function reportWebVital(vital: WebVital) {
  if (import.meta.env.PROD) {
    // Send to observability backend (e.g., Sentry, New Relic)
    const reportingUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/v1/metrics/web-vitals`;
    
    navigator.sendBeacon(reportingUrl, JSON.stringify({
      metric: vital.metric,
      value: Math.round(vital.value),
      rating: vital.rating,
      timestamp: vital.timestamp,
      url: window.location.pathname,
      userAgent: navigator.userAgent,
    }));
  }
}

/**
 * Initialize Web Vitals monitoring
 */
export function initWebVitalsMonitoring() {
  // LCP (Largest Contentful Paint)
  if ('PerformanceObserver' in window) {
    try {
      const lcpObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        
        const vital: WebVital = {
          metric: 'LCP',
          value: lastEntry.renderTime || lastEntry.loadTime,
          timestamp: performance.now(),
          rating: getRating('LCP', lastEntry.renderTime || lastEntry.loadTime),
        };
        
        reportWebVital(vital);
      });
      
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      console.warn('LCP monitoring not supported', e);
    }
  }
  
  // CLS (Cumulative Layout Shift)
  if ('PerformanceObserver' in window) {
    try {
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
        
        const vital: WebVital = {
          metric: 'CLS',
          value: clsValue,
          timestamp: performance.now(),
          rating: getRating('CLS', clsValue),
        };
        
        reportWebVital(vital);
      });
      
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      console.warn('CLS monitoring not supported', e);
    }
  }
  
  // FCP (First Contentful Paint)
  try {
    const entries = performance.getEntriesByName('first-contentful-paint');
    if (entries.length > 0) {
      const vital: WebVital = {
        metric: 'FCP',
        value: entries[0].startTime,
        timestamp: performance.now(),
        rating: getRating('FCP', entries[0].startTime),
      };
      
      reportWebVital(vital);
    }
  } catch (e) {
    console.warn('FCP monitoring not available', e);
  }
  
  // Navigation Timing (TTFB)
  window.addEventListener('load', () => {
    try {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        const ttfb = navigation.responseStart - navigation.requestStart;
        const vital: WebVital = {
          metric: 'TTFB',
          value: ttfb,
          timestamp: performance.now(),
          rating: getRating('TTFB', ttfb),
        };
        
        reportWebVital(vital);
      }
    } catch (e) {
      console.warn('TTFB monitoring not available', e);
    }
  });
}

/**
 * Export performance metrics summary
 */
export function getPerformanceSummary() {
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  
  return {
    dns: navigation?.domainLookupEnd - navigation?.domainLookupStart,
    tcp: navigation?.connectEnd - navigation?.connectStart,
    ttfb: navigation?.responseStart - navigation?.requestStart,
    download: navigation?.responseEnd - navigation?.responseStart,
    domInteractive: navigation?.domInteractive - navigation?.responseEnd,
    domComplete: navigation?.domComplete - navigation?.domInteractive,
    loadComplete: navigation?.loadEventEnd - navigation?.loadEventStart,
    total: navigation?.loadEventEnd - navigation?.fetchStart,
  };
}
