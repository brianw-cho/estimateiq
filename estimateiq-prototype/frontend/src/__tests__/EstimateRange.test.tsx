import React from 'react';
import { render, screen } from '@testing-library/react';
import {
  EstimateRange,
  EstimateRangeCompact,
  EstimateRangeTable,
} from '@/components/estimate/EstimateRange';
import type { EstimateRange as EstimateRangeType } from '@/lib/types';

const mockRange: EstimateRangeType = {
  low: 250.0,
  expected: 350.0,
  high: 450.0,
};

describe('EstimateRange', () => {
  it('should render low, expected, and high labels', () => {
    render(<EstimateRange range={mockRange} />);

    expect(screen.getByText('Low')).toBeInTheDocument();
    expect(screen.getByText('Expected')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('should render formatted currency values', () => {
    render(<EstimateRange range={mockRange} />);

    expect(screen.getByText('$250.00')).toBeInTheDocument();
    expect(screen.getByText('$350.00')).toBeInTheDocument();
    expect(screen.getByText('$450.00')).toBeInTheDocument();
  });

  it('should handle zero values', () => {
    const zeroRange: EstimateRangeType = {
      low: 0,
      expected: 0,
      high: 0,
    };

    render(<EstimateRange range={zeroRange} />);

    const zeroValues = screen.getAllByText('$0.00');
    expect(zeroValues.length).toBe(3);
  });
});

describe('EstimateRangeCompact', () => {
  it('should show expected as main value', () => {
    render(<EstimateRangeCompact range={mockRange} />);

    // Expected should be prominent
    expect(screen.getByText('$350.00')).toBeInTheDocument();
  });

  it('should show range in parentheses', () => {
    render(<EstimateRangeCompact range={mockRange} />);

    // Range should show as ($250.00 - $450.00)
    expect(screen.getByText(/\$250\.00.*\$450\.00/)).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <EstimateRangeCompact range={mockRange} className="test-class" />
    );

    expect(container.firstChild).toHaveClass('test-class');
  });
});

describe('EstimateRangeTable', () => {
  it('should render three columns', () => {
    render(<EstimateRangeTable range={mockRange} />);

    expect(screen.getByText('Low Estimate')).toBeInTheDocument();
    expect(screen.getByText('Expected')).toBeInTheDocument();
    expect(screen.getByText('High Estimate')).toBeInTheDocument();
  });

  it('should render formatted values', () => {
    render(<EstimateRangeTable range={mockRange} />);

    expect(screen.getByText('$250.00')).toBeInTheDocument();
    expect(screen.getByText('$350.00')).toBeInTheDocument();
    expect(screen.getByText('$450.00')).toBeInTheDocument();
  });

  it('should handle large values', () => {
    const largeRange: EstimateRangeType = {
      low: 10000,
      expected: 15000,
      high: 20000,
    };

    render(<EstimateRangeTable range={largeRange} />);

    expect(screen.getByText('$10,000.00')).toBeInTheDocument();
    expect(screen.getByText('$15,000.00')).toBeInTheDocument();
    expect(screen.getByText('$20,000.00')).toBeInTheDocument();
  });
});
