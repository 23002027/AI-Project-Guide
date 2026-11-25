import React, { useState } from 'react';

interface Tab {
  label: string;
  content: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  className?: string;
  tabClassName?: string;
  activeTabClassName?: string;
}

export default function Tabs({ tabs, className = '', tabClassName = '', activeTabClassName = '' }: TabsProps) {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className={`flex flex-col ${className}`}>
      <div className="flex border-b border-gray-600">
        {tabs.map((tab, idx) => (
          <button
            key={idx}
            onClick={() => setActiveIndex(idx)}
            className={`px-4 py-2 text-sm font-medium focus:outline-none ${tabClassName} ${activeIndex === idx ? `border-b-2 border-${"#3b82f6"} ${activeTabClassName}` : 'text-gray-400'} `}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="p-4">
        {tabs[activeIndex]?.content}
      </div>
    </div>
  );
}
