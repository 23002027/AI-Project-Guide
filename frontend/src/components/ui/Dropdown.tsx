

interface Option<T = string> {
  label: string;
  value: T;
}

interface DropdownProps<T = string> {
  options: Option<T>[];
  value?: T;
  onChange: (value: T) => void;
  placeholder?: string;
  className?: string;
}

export default function Dropdown<T = string>({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  className = '',
}: DropdownProps<T>) {
  return (
    <select
      value={value as any}
      onChange={e => onChange(e.target.value as any)}
      className={`w-full rounded-md border border-gray-300 bg-[#090d16] text-white focus:outline-none focus:ring-2 focus:ring-[#3b82f6] ${className}`}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {options.map(opt => (
        <option key={String(opt.value)} value={String(opt.value)}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
