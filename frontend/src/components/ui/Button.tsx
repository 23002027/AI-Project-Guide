import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style */
  variant?: ButtonVariant;
  /** Size of the button */
  size?: ButtonSize;
  /** Optional left icon (SVG component) */
  startIcon?: React.ReactNode;
  /** Optional right icon */
  endIcon?: React.ReactNode;
  /** Loading state – shows spinner and disables button */
  loading?: boolean;
}

/**
 * Reusable button component matching the dark SaaS design system.
 *
 * - Primary: blue background, white text.
 * - Secondary: gray background, white text.
 * - Danger: red background.
 * - Ghost: transparent with border.
 *
 * Size classes adjust padding and text size.
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  startIcon,
  endIcon,
  loading = false,
  disabled,
  className = '',
  children,
  ...rest
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2';
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-500 text-white border border-blue-700 focus:ring-blue-400',
    secondary: 'bg-slate-700 hover:bg-slate-600 text-white border border-slate-600 focus:ring-slate-400',
    danger: 'bg-red-600 hover:bg-red-500 text-white border border-red-700 focus:ring-red-400',
    ghost: 'bg-transparent hover:bg-slate-800 text-slate-300 border border-slate-600 focus:ring-slate-400',
  }[variant];
  const sizeClasses = {
    sm: 'px-2.5 py-1.5 text-xs',
    md: 'px-3.5 py-2 text-sm',
    lg: 'px-4.5 py-2.5 text-base',
  }[size];

  const isDisabled = loading || disabled;

  return (
    <button
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      disabled={isDisabled}
      {...rest}
    >
      {loading && (
        <span className="w-3 h-3 mr-2 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      )}
      {startIcon && !loading && <span className="mr-2">{startIcon}</span>}
      {children}
      {endIcon && <span className="ml-2">{endIcon}</span>}
    </button>
  );
};
