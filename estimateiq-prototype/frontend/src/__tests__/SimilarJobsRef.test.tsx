import React from 'react';
import { render, screen } from '@testing-library/react';
import { SimilarJobsRef, SimilarJobsCard } from '@/components/estimate/SimilarJobsRef';

describe('SimilarJobsRef', () => {
  it('should render summary text', () => {
    render(
      <SimilarJobsRef
        count={10}
        summary="Based on 10 similar jobs on 25-30' vessels"
      />
    );

    expect(screen.getByText("Based on 10 similar jobs on 25-30' vessels")).toBeInTheDocument();
  });

  it('should render job count badge', () => {
    render(
      <SimilarJobsRef
        count={15}
        summary="Based on similar jobs"
      />
    );

    expect(screen.getByText('15 jobs')).toBeInTheDocument();
  });

  it('should show different badge for different counts', () => {
    const { rerender } = render(
      <SimilarJobsRef count={10} summary="Based on similar jobs" />
    );
    expect(screen.getByText('10 jobs')).toBeInTheDocument();

    rerender(<SimilarJobsRef count={5} summary="Based on similar jobs" />);
    expect(screen.getByText('5 jobs')).toBeInTheDocument();

    rerender(<SimilarJobsRef count={2} summary="Based on similar jobs" />);
    expect(screen.getByText('2 jobs')).toBeInTheDocument();
  });

  it('should show "No similar jobs" for count 0', () => {
    render(
      <SimilarJobsRef count={0} summary="No historical data found" />
    );

    expect(screen.getByText('No similar jobs')).toBeInTheDocument();
  });
});

describe('SimilarJobsCard', () => {
  it('should render AI Analysis title', () => {
    render(
      <SimilarJobsCard
        count={10}
        summary="Based on 10 similar jobs"
      />
    );

    expect(screen.getByText('AI Analysis')).toBeInTheDocument();
  });

  it('should render summary text', () => {
    render(
      <SimilarJobsCard
        count={10}
        summary="Based on 10 similar oil change jobs"
      />
    );

    expect(screen.getByText('Based on 10 similar oil change jobs')).toBeInTheDocument();
  });

  it('should render similar jobs found badge', () => {
    render(
      <SimilarJobsCard
        count={15}
        summary="Based on similar jobs"
      />
    );

    expect(screen.getByText('15 similar jobs found')).toBeInTheDocument();
  });

  it('should show average total when provided', () => {
    render(
      <SimilarJobsCard
        count={10}
        summary="Based on similar jobs"
        averageTotal={350}
      />
    );

    expect(screen.getByText(/Average invoice from similar jobs/)).toBeInTheDocument();
    expect(screen.getByText('$350.00')).toBeInTheDocument();
  });

  it('should show warning note for low job count', () => {
    render(
      <SimilarJobsCard
        count={3}
        summary="Limited data"
      />
    );

    expect(screen.getByText(/Limited historical data/)).toBeInTheDocument();
  });

  it('should not show warning note for high job count', () => {
    render(
      <SimilarJobsCard
        count={10}
        summary="Based on similar jobs"
      />
    );

    expect(screen.queryByText(/Limited historical data/)).not.toBeInTheDocument();
  });
});
