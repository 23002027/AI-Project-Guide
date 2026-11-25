import React from 'react';

type Variant = 'default' | 'primary' | 'success' | 'warning' | 'danger';

interface BadgeProps {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
}

const variantClasses: Record<Variant, string> = {
  default: 'bg-gray-700 text-gray-200',
  primary: 'bg-[#3b82f6] text-white',
  success: 'bg-[#10b981] text-white',
  warning: 'bg-[#f59e0b] text-white',
  danger: 'bg-[#ef4444] text-white',
};

export default function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
