import React from 'react';

export const ChatBubble = ({ message, isUser }: { message: string, isUser: boolean }) => {
  return (
    <div className={`p-2 rounded-lg ${isUser ? 'bg-blue-500 text-white ml-auto' : 'bg-gray-200 text-black mr-auto'}`}>
      {message}
    </div>
  );
};
