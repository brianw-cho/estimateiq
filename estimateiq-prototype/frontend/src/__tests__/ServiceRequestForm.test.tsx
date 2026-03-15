import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ServiceRequestForm, validateServiceRequest } from '@/components/estimate/ServiceRequestForm';
import type { ServiceRequestData } from '@/components/estimate';

describe('ServiceRequestForm', () => {
  const mockOnChange = jest.fn();
  const defaultData: ServiceRequestData = {
    description: '',
    urgency: 'routine',
    region: 'Northeast',
  };

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render form title', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    expect(screen.getByText('Service Request')).toBeInTheDocument();
    expect(screen.getByText(/Describe the service needed/i)).toBeInTheDocument();
  });

  it('should render service description textarea', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    expect(screen.getByLabelText(/Service Description/i)).toBeInTheDocument();
  });

  it('should call onChange when description is entered', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    const descInput = screen.getByLabelText(/Service Description/i);
    fireEvent.change(descInput, { target: { value: 'Oil change' } });

    expect(mockOnChange).toHaveBeenCalledWith(
      expect.objectContaining({ description: 'Oil change' })
    );
  });

  it('should display error messages when provided', () => {
    const errors = {
      description: 'Please provide a service description',
    };

    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} errors={errors} />);

    expect(screen.getByText('Please provide a service description')).toBeInTheDocument();
  });

  it('should show pre-filled description', () => {
    const data: ServiceRequestData = {
      description: 'Annual oil change',
      urgency: 'routine',
      region: 'Northeast',
    };

    render(<ServiceRequestForm data={data} onChange={mockOnChange} />);

    expect(screen.getByDisplayValue('Annual oil change')).toBeInTheDocument();
  });

  it('should show helper text for description', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    expect(screen.getByText(/Be specific about symptoms/i)).toBeInTheDocument();
  });

  it('should render Service Category label', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    expect(screen.getByText(/Service Category/i)).toBeInTheDocument();
  });

  it('should render Urgency Level label', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    expect(screen.getByText(/Urgency Level/i)).toBeInTheDocument();
  });

  it('should render Region label', () => {
    render(<ServiceRequestForm data={defaultData} onChange={mockOnChange} />);

    expect(screen.getByText('Region')).toBeInTheDocument();
  });
});

describe('validateServiceRequest', () => {
  it('should return no errors for valid request', () => {
    const data: ServiceRequestData = {
      description: 'Annual oil change and filter replacement',
      urgency: 'routine',
      region: 'Northeast',
    };

    const errors = validateServiceRequest(data);

    expect(Object.keys(errors)).toHaveLength(0);
  });

  it('should return error for empty description', () => {
    const data: ServiceRequestData = {
      description: '',
      urgency: 'routine',
      region: 'Northeast',
    };

    const errors = validateServiceRequest(data);

    expect(errors.description).toBeDefined();
  });

  it('should return error for description too short', () => {
    const data: ServiceRequestData = {
      description: 'Oil',
      urgency: 'routine',
      region: 'Northeast',
    };

    const errors = validateServiceRequest(data);

    expect(errors.description).toBeDefined();
    expect(errors.description).toContain('at least 5 characters');
  });

  it('should return error for whitespace-only description', () => {
    const data: ServiceRequestData = {
      description: '    ',
      urgency: 'routine',
      region: 'Northeast',
    };

    const errors = validateServiceRequest(data);

    expect(errors.description).toBeDefined();
  });

  it('should accept description with exactly 5 characters', () => {
    const data: ServiceRequestData = {
      description: 'Hello',
      urgency: 'routine',
      region: 'Northeast',
    };

    const errors = validateServiceRequest(data);

    expect(Object.keys(errors)).toHaveLength(0);
  });

  it('should accept description with more than 5 characters', () => {
    const data: ServiceRequestData = {
      description: 'This is a longer service description',
      urgency: 'routine',
      region: 'Northeast',
    };

    const errors = validateServiceRequest(data);

    expect(Object.keys(errors)).toHaveLength(0);
  });
});
