import React from 'react';

export const ChatInput = ({ onSend }: { onSend: (msg: string) => void }) => {
  const [input, setInput] = React.useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <div className="flex gap-2">
      <input 
        type="text" 
        value={input} 
        onChange={(e) => setInput(e.target.value)} 
        className="border p-2 flex-1 rounded"
        placeholder="Type a message..."
      />
      <button onClick={handleSend} className="bg-blue-500 text-white p-2 rounded">Send</button>
    </div>
  );
};
