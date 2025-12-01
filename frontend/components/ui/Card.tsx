import React from 'react';

export const Card = ({ children, title }: { children: React.ReactNode, title?: string }) => {
  return (
    <div className="border rounded shadow p-4 bg-white">
      {title && <h3 className="font-bold mb-2">{title}</h3>}
      {children}
    </div>
  );
};
