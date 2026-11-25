

export default function ErrorState({
  title = 'Something went wrong',
  description = 'Please try again later or contact support.',
  retryLabel = 'Retry',
  onRetry,
}: {
  title?: string;
  description?: string;
  retryLabel?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="text-5xl mb-4">⚠️</div>
      <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400 mb-4 max-w-sm">{description}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-[#ef4444] text-white rounded-md hover:bg-[#dc2626] transition"
        >
          {retryLabel}
        </button>
      )}
    </div>
  );
}
