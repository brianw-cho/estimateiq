import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { VesselForm, validateVessel } from '@/components/estimate/VesselForm';
import type { Vessel } from '@/lib/types';

describe('VesselForm', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render form title', () => {
    render(<VesselForm vessel={{}} onChange={mockOnChange} />);

    expect(screen.getByText('Vessel Information')).toBeInTheDocument();
    expect(screen.getByText(/Enter the vessel specifications/i)).toBeInTheDocument();
  });

  it('should render input fields for vessel name, LOA, year, beam, and engine model', () => {
    render(<VesselForm vessel={{}} onChange={mockOnChange} />);

    expect(screen.getByLabelText(/Vessel Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Length Overall/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Year Built/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Beam/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Engine Model/i)).toBeInTheDocument();
  });

  it('should render labels for select fields', () => {
    render(<VesselForm vessel={{}} onChange={mockOnChange} />);

    // Use getAllByText since the label text may appear multiple times
    expect(screen.getAllByText(/Engine Make/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Hull Type/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Propulsion Type/i).length).toBeGreaterThan(0);
  });

  it('should call onChange when LOA is entered', () => {
    render(<VesselForm vessel={{}} onChange={mockOnChange} />);

    const loaInput = screen.getByLabelText(/Length Overall/i);
    fireEvent.change(loaInput, { target: { value: '28' } });

    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({ loa: 28 }));
  });

  it('should call onChange when year is entered', () => {
    render(<VesselForm vessel={{}} onChange={mockOnChange} />);

    const yearInput = screen.getByLabelText(/Year Built/i);
    fireEvent.change(yearInput, { target: { value: '2019' } });

    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({ year: 2019 }));
  });

  it('should call onChange when engine model is entered', () => {
    render(<VesselForm vessel={{}} onChange={mockOnChange} />);

    const modelInput = screen.getByLabelText(/Engine Model/i);
    fireEvent.change(modelInput, { target: { value: 'D4-300' } });

    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({ engine_model: 'D4-300' }));
  });

  it('should display error messages when provided', () => {
    const errors = {
      loa: 'Length must be between 10 and 200 feet',
      year: 'Year is required',
    };

    render(<VesselForm vessel={{}} onChange={mockOnChange} errors={errors} />);

    expect(screen.getByText('Length must be between 10 and 200 feet')).toBeInTheDocument();
    expect(screen.getByText('Year is required')).toBeInTheDocument();
  });

  it('should show pre-filled values', () => {
    const vessel: Partial<Vessel> = {
      name: 'Sea Breeze',
      loa: 28,
      year: 2019,
      engine_model: 'D4-300',
    };

    render(<VesselForm vessel={vessel} onChange={mockOnChange} />);

    expect(screen.getByDisplayValue('Sea Breeze')).toBeInTheDocument();
    expect(screen.getByDisplayValue('28')).toBeInTheDocument();
    expect(screen.getByDisplayValue('2019')).toBeInTheDocument();
    expect(screen.getByDisplayValue('D4-300')).toBeInTheDocument();
  });
});

describe('validateVessel', () => {
  it('should return no errors for valid vessel', () => {
    const vessel: Partial<Vessel> = {
      loa: 28,
      year: 2019,
      engine_make: 'Volvo Penta',
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(Object.keys(errors)).toHaveLength(0);
  });

  it('should return error for missing LOA', () => {
    const vessel: Partial<Vessel> = {
      year: 2019,
      engine_make: 'Volvo Penta',
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(errors.loa).toBeDefined();
  });

  it('should return error for LOA too small', () => {
    const vessel: Partial<Vessel> = {
      loa: 5,
      year: 2019,
      engine_make: 'Volvo Penta',
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(errors.loa).toBeDefined();
    expect(errors.loa).toContain('between 10 and 200');
  });

  it('should return error for LOA too large', () => {
    const vessel: Partial<Vessel> = {
      loa: 250,
      year: 2019,
      engine_make: 'Volvo Penta',
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(errors.loa).toBeDefined();
  });

  it('should return error for missing year', () => {
    const vessel: Partial<Vessel> = {
      loa: 28,
      engine_make: 'Volvo Penta',
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(errors.year).toBeDefined();
  });

  it('should return error for year too old', () => {
    const vessel: Partial<Vessel> = {
      loa: 28,
      year: 1940,
      engine_make: 'Volvo Penta',
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(errors.year).toBeDefined();
  });

  it('should return error for missing engine make', () => {
    const vessel: Partial<Vessel> = {
      loa: 28,
      year: 2019,
      engine_model: 'D4-300',
    };

    const errors = validateVessel(vessel);

    expect(errors.engine_make).toBeDefined();
  });

  it('should return error for missing engine model', () => {
    const vessel: Partial<Vessel> = {
      loa: 28,
      year: 2019,
      engine_make: 'Volvo Penta',
    };

    const errors = validateVessel(vessel);

    expect(errors.engine_model).toBeDefined();
  });

  it('should return multiple errors when multiple fields invalid', () => {
    const vessel: Partial<Vessel> = {};

    const errors = validateVessel(vessel);

    expect(Object.keys(errors).length).toBeGreaterThan(1);
    expect(errors.loa).toBeDefined();
    expect(errors.year).toBeDefined();
    expect(errors.engine_make).toBeDefined();
    expect(errors.engine_model).toBeDefined();
  });
});
