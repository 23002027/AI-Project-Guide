import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Optional label displayed above the input */
  label?: string;
  /** Show error message below the input */
  error?: string;
}

/**
 * Reusable input component matching the dark SaaS design system.
 * Uses the `#0f172a` background for the input container.
 */
export const Input: React.FC<InputProps> = ({
  label,
  error,
  className = '',
  ...rest
}) => {
  const baseClasses = 'w-full bg-[#0f172a] border border-[#1e293b] rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition';

  return (
    <div className={`space-y-1 ${className}`}>
      {label && <label className="block text-xs font-semibold text-slate-300">{label}</label>}
      <input className={`${baseClasses} ${error ? 'border-red-500' : ''}`} {...rest} />
      {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
    </div>
  );
};
