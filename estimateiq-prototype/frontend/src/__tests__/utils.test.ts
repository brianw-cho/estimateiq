import {
  cn,
  formatCurrency,
  formatPercent,
  formatDate,
  getConfidenceLevel,
} from '@/lib/utils';

describe('cn utility', () => {
  it('should merge class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('should handle conditional classes', () => {
    expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz');
  });

  it('should handle tailwind conflicts', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4');
  });

  it('should handle arrays', () => {
    expect(cn(['foo', 'bar'])).toBe('foo bar');
  });
});

describe('formatCurrency', () => {
  it('should format as USD', () => {
    expect(formatCurrency(100)).toBe('$100.00');
  });

  it('should handle decimals', () => {
    expect(formatCurrency(100.5)).toBe('$100.50');
  });

  it('should handle large numbers', () => {
    expect(formatCurrency(1000)).toBe('$1,000.00');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });
});

describe('formatPercent', () => {
  it('should format as percentage', () => {
    expect(formatPercent(0.85)).toBe('85%');
  });

  it('should format 100%', () => {
    expect(formatPercent(1)).toBe('100%');
  });

  it('should format low percentages', () => {
    expect(formatPercent(0.05)).toBe('5%');
  });
});

describe('formatDate', () => {
  it('should format ISO date string', () => {
    const result = formatDate('2026-03-15T10:30:00Z');
    expect(result).toContain('Mar');
    expect(result).toContain('15');
    expect(result).toContain('2026');
  });
});

describe('getConfidenceLevel', () => {
  it('should return high for score >= 0.8', () => {
    const result = getConfidenceLevel(0.85);
    expect(result.level).toBe('high');
    expect(result.text).toBe('High Confidence');
    expect(result.color).toBe('text-green-600');
  });

  it('should return medium for score >= 0.6', () => {
    const result = getConfidenceLevel(0.7);
    expect(result.level).toBe('medium');
    expect(result.text).toBe('Medium Confidence');
    expect(result.color).toBe('text-yellow-600');
  });

  it('should return low for score < 0.6', () => {
    const result = getConfidenceLevel(0.4);
    expect(result.level).toBe('low');
    expect(result.text).toBe('Low Confidence');
    expect(result.color).toBe('text-orange-600');
  });

  it('should handle boundary at 0.8', () => {
    expect(getConfidenceLevel(0.8).level).toBe('high');
    expect(getConfidenceLevel(0.79).level).toBe('medium');
  });

  it('should handle boundary at 0.6', () => {
    expect(getConfidenceLevel(0.6).level).toBe('medium');
    expect(getConfidenceLevel(0.59).level).toBe('low');
  });
});
