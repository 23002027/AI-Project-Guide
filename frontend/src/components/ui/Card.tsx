import React from 'react';

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  /** Optional header title */
  title?: React.ReactNode;
  /** Optional footer content */
  footer?: React.ReactNode;
  /** Background color – defaults to design system card surface */
  bgClass?: string;
}

/**
 * Reusable card component matching the dark SaaS design system.
 * Uses the `#0f172a` surface by default with subtle border and shadow.
 */
export const Card: React.FC<CardProps> = ({
  title,
  footer,
  bgClass = 'bg-[#0f172a] border border-[#1e293b] shadow-md',
  className = '',
  children,
  ...rest
}) => {
  return (
    <div className={`${bgClass} rounded-xl p-4 ${className}`} {...rest}>
      {title && <div className="mb-3 text-lg font-semibold text-white">{title}</div>}
      <div className="text-sm text-slate-300">{children}</div>
      {footer && <div className="mt-4 border-t border-slate-700 pt-3">{footer}</div>}
    </div>
  );
};
