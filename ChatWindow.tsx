import React, { useState } from "react";
import { sendMessage } from "../services/apiClients";

interface ChatItem {
 role: "user" | "assistant";
 content: string;
}

const ChatWindow: React.FC = () => {
 const [input, setInput] = useState("");
 const [history, setHistory] = useState<ChatItem[]>([]);

 const onSend = async () => {
   if (!input.trim()) return;
   const userMsg = input;
   setHistory([...history, { role: "user", content: userMsg }]);
   setInput("");
   try {
     const reply = await sendMessage(userMsg);
     setHistory((prev) => [...prev, { role: "assistant", content: reply }]);
   } catch (err) {
     setHistory((prev) => [...prev, { role: "assistant", content: "応答に失敗しました。" }]);
   }
 };

 return (
   <div className="chat-window">
     <div className="messages-area">
       {history.map((h, idx) => (
         <div key={idx} style={{ textAlign: h.role === "user" ? "right" : "left", margin: "0.5rem 0" }}>
           <span
             style={{
               display: "inline-block",
               padding: "0.5rem 1rem",
               backgroundColor: h.role === "user" ? "#d1e7dd" : "#f8f9fa",
               borderRadius: "10px",
             }}
           >
             {h.content}
           </span>
         </div>
       ))}
     </div>
     <form className="input-form" onSubmit={(e) => { e.preventDefault(); onSend(); }}>
       <input
         type="text"
         value={input}
         onChange={(e) => setInput(e.target.value)}
         onKeyDown={(e) => {
           if (e.key === "Enter") {
             e.preventDefault();
             onSend();
           }
         }}
         placeholder="メッセージを入力..."
       />
       <button type="submit">送信</button>
     </form>
   </div>
 );
};

export default ChatWindow;