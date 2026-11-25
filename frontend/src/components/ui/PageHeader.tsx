import React from 'react';

export default function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}) {
  return (
    <header className="mb-8 space-y-2">
      <h1 className="text-3xl font-bold text-white">{title}</h1>
      {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
      {actions && <div className="mt-4 flex items-center space-x-2">{actions}</div>}
    </header>
  );
}
