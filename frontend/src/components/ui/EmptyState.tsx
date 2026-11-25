// EmptyState component without external SVG import


export default function EmptyState({
  title = 'Nothing to show',
  description = 'Add some items to get started.',
  actionLabel,
  onAction,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {/* Simple placeholder emoji */}
      <div className="text-5xl mb-4">📭</div>
      <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400 mb-4 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-[#3b82f6] text-white rounded-md hover:bg-[#2563eb] transition"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
