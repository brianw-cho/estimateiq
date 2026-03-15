import React from 'react';
import { render, screen } from '@testing-library/react';
import {
  ConfidenceIndicator,
  ConfidenceBadge,
  ConfidenceText,
} from '@/components/estimate/ConfidenceIndicator';

describe('ConfidenceIndicator', () => {
  it('should render progress bar by default', () => {
    const { container } = render(<ConfidenceIndicator score={0.85} />);

    // Progress bar should be present
    const progressBar = container.querySelector('[role="progressbar"]');
    expect(progressBar).toBeInTheDocument();
  });

  it('should render label by default', () => {
    render(<ConfidenceIndicator score={0.85} />);

    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('should hide progress bar when showProgress is false', () => {
    const { container } = render(
      <ConfidenceIndicator score={0.85} showProgress={false} />
    );

    const progressBar = container.querySelector('[role="progressbar"]');
    expect(progressBar).not.toBeInTheDocument();
  });

  it('should hide label when showLabel is false', () => {
    render(<ConfidenceIndicator score={0.85} showLabel={false} />);

    expect(screen.queryByText('85%')).not.toBeInTheDocument();
  });

  it('should render correct percentage for different scores', () => {
    const { rerender } = render(<ConfidenceIndicator score={0.7} />);
    expect(screen.getByText('70%')).toBeInTheDocument();

    rerender(<ConfidenceIndicator score={0.5} />);
    expect(screen.getByText('50%')).toBeInTheDocument();

    rerender(<ConfidenceIndicator score={1.0} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});

describe('ConfidenceBadge', () => {
  it('should show "High Confidence" for score >= 0.8', () => {
    render(<ConfidenceBadge score={0.9} />);
    expect(screen.getByText('High Confidence')).toBeInTheDocument();
  });

  it('should show "Medium Confidence" for score >= 0.6', () => {
    render(<ConfidenceBadge score={0.7} />);
    expect(screen.getByText('Medium Confidence')).toBeInTheDocument();
  });

  it('should show "Low Confidence" for score < 0.6', () => {
    render(<ConfidenceBadge score={0.4} />);
    expect(screen.getByText('Low Confidence')).toBeInTheDocument();
  });

  it('should handle boundary at 0.8', () => {
    const { rerender } = render(<ConfidenceBadge score={0.8} />);
    expect(screen.getByText('High Confidence')).toBeInTheDocument();

    rerender(<ConfidenceBadge score={0.79} />);
    expect(screen.getByText('Medium Confidence')).toBeInTheDocument();
  });
});

describe('ConfidenceText', () => {
  it('should show confidence text with percentage', () => {
    render(<ConfidenceText score={0.85} />);
    expect(screen.getByText(/High Confidence.*85%/)).toBeInTheDocument();
  });

  it('should hide percentage when showPercent is false', () => {
    render(<ConfidenceText score={0.85} showPercent={false} />);
    expect(screen.getByText('High Confidence')).toBeInTheDocument();
    expect(screen.queryByText('85%')).not.toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ConfidenceText score={0.85} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
