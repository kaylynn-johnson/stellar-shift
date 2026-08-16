'use client';

// Adapted from https://jsdev.space/react-double-range-slider/

import * as SliderPrimitive from '@radix-ui/react-slider';
import { forwardRef, useCallback, useEffect, useMemo, useState } from 'react';
import { cn } from '@/shared/lib/utils';

type RangeTuple = [number, number];

export type DoubleRangeSliderProps = {
  className?: string;
  min: number;
  max: number;
  step?: number;
  value?: number[] | readonly number[];
  defaultValue?: number[] | readonly number[];
  onValueChange?: (values: RangeTuple) => void;
  onValueCommit?: (values: RangeTuple) => void;
  formatLabel?: (value: number) => string;
  minThumbLabel?: string;
  maxThumbLabel?: string;
};

const clamp = (n: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, n));

function normalizeRange(
  input: readonly number[] | undefined,
  min: number,
  max: number,
  step: number
): RangeTuple {
  const snap = (v: number) => {
    const snapped = Math.round((v - min) / step) * step + min;
    return clamp(snapped, min, max);
  };
  const a = snap(input?.[0] ?? min);
  const b = snap(input?.[1] ?? max);
  return a <= b ? [a, b] : [b, a];
}

export const DoubleRangeSlider = forwardRef<HTMLSpanElement, DoubleRangeSliderProps>(
  function DoubleRangeSlider(
    {
      className,
      min,
      max,
      step = 1,
      value,
      defaultValue,
      onValueChange,
      onValueCommit,
      formatLabel,
      minThumbLabel = 'Minimum value',
      maxThumbLabel = 'Maximum value',
      ...props
    },
    ref
  ) {
    const [local, setLocal] = useState<RangeTuple>(() =>
      normalizeRange(value ?? defaultValue ?? [min, max], min, max, step)
    );

    useEffect(() => {
      if (value) {
        setLocal(normalizeRange(value, min, max, step));
      }
    }, [value, min, max, step]);

    const [leftPct, rightPct] = useMemo(() => {
      const span = Math.max(1, max - min);
      return [((local[0] - min) / span) * 100, ((local[1] - min) / span) * 100];
    }, [local, min, max]);

    const handleChange = useCallback(
      (vals: number[]) => {
        const next = normalizeRange(vals, min, max, step);
        setLocal(next);
        onValueChange?.(next);
      },
      [min, max, step, onValueChange]
    );

    const handleCommit = useCallback(
      (vals: number[]) => {
        const next = normalizeRange(vals, min, max, step);
        onValueCommit?.(next);
      },
      [min, max, step, onValueCommit]
    );

    const leftOnTop = local[0] >= max - step;

    return (
      <SliderPrimitive.Root
        ref={ref}
        min={min}
        max={max}
        step={step}
        value={local}
        onValueChange={handleChange}
        onValueCommit={handleCommit}
        className={cn('relative mb-20 mt-10 flex w-5/6 left-10 select-none touch-none items-center', className)}
        {...props}
      >
        <SliderPrimitive.Track className="relative h-1 w-full grow overflow-hidden rounded-full bg-primary/20 border">
          <SliderPrimitive.Range className="absolute h-full bg-main" />
        </SliderPrimitive.Track>

        <div
          className="pointer-events-none absolute top-2 -translate-x-1/2 text-center"
          style={{ left: `${leftPct}%` }}
        >
          <span className="text-sm">{formatLabel ? formatLabel(local[0]) : local[0]}</span>
        </div>
        <div
          className="pointer-events-none absolute top-2 -translate-x-1/2 text-center"
          style={{ left: `${rightPct}%` }}
        >
          <span className="text-sm">{formatLabel ? formatLabel(local[1]) : local[1]}</span>
        </div>

        <SliderPrimitive.Thumb
          aria-label={minThumbLabel}
          className={cn(
            'block h-4 w-4 rounded-full border border-main bg-white shadow transition-colors',
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
            'disabled:pointer-events-none disabled:opacity-50',
            leftOnTop && 'z-10'
          )}
        />
        <SliderPrimitive.Thumb
          aria-label={maxThumbLabel}
          className={cn(
            'block h-4 w-4 rounded-full border border-main bg-white shadow transition-colors',
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
            'disabled:pointer-events-none disabled:opacity-50'
          )}
        />
      </SliderPrimitive.Root>
    );
  }
);