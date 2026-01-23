// components/Button.tsx
'use client';

import * as React from 'react';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary';
  loading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  block?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  focusableWhenDisabled?: boolean; // keeps focusable but inert when true
};

export function Button({
  variant = 'primary',
  loading = false,
  disabled,
  type = 'button', // prevent accidental form submits inside forms
  size = 'md',
  block = false,
  iconLeft,
  iconRight,
  focusableWhenDisabled = false,
  children,
  className = '',
  onClick,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading;

  // Map size to minimal inline sizing so you don't need extra CSS classes.
  const sizeStyle =
    size === 'sm'
      ? { padding: '.4rem .75rem', fontSize: '.9rem', height: 36 }
      : size === 'lg'
      ? { padding: '.7rem 1.1rem', fontSize: '1rem', height: 46 }
      : { padding: '.55rem 1rem', fontSize: '.95rem', height: 42 };

  const base = 'button';
  const theme = variant === 'primary' ? 'button-primary' : 'button-secondary';

  // If keeping focusable when disabled, don't set disabled attr.
  const trulyDisabled = isDisabled && !focusableWhenDisabled;

  // Prevent clicks when "disabled" but focusable.
  const handleClick: React.MouseEventHandler<HTMLButtonElement> = (e) => {
    if (isDisabled) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    onClick?.(e);
  };

  return (
    <button
      type={type}
      className={`${base} ${theme} ${className}`}
      style={{
        ...sizeStyle,
        width: block ? '100%' : undefined,
      }}
      disabled={trulyDisabled}
      aria-disabled={isDisabled || undefined}
      aria-busy={loading || undefined}
      tabIndex={focusableWhenDisabled && isDisabled ? 0 : undefined}
      onClick={handleClick}
      {...rest}
    >
      {loading ? (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          {/* SVG spinner: no CSS needed */}
          <svg
            aria-hidden="true"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            role="img"
          >
            <circle cx="12" cy="12" r="10" stroke="currentColor" opacity="0.2" strokeWidth="4" />
            <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" strokeWidth="4">
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 12 12"
                to="360 12 12"
                dur="0.9s"
                repeatCount="indefinite"
              />
            </path>
          </svg>
          Loading…
        </span>
      ) : (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          {iconLeft}
          <span>{children}</span>
          {iconRight}
        </span>
      )}
    </button>
  );
}
