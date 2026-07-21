"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Phone, Video, MoreVertical, MessageSquare, Search, Plus, Archive, ChevronDown, Smile, Paperclip, Mic } from "lucide-react";
import { interactionsService } from "@/services/interactions.service";
import { useCustomerSession } from "@/features/customer/use-customer-session";

interface ChatMessage { role: string; content: string; timestamp: string; }

export default function CustomerWhatsAppPage() {
  const session = useCustomerSession();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [interactionId, setInteractionId] = useState<string | null>(null);
  const [textInput, setTextInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!session) return;
    startSession();
  }, [session]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const startSession = async () => {
    try {
      const res = await interactionsService.start(session?.email, "whatsapp");
      const dbInt = res.data?.data;
      if (dbInt) {
        setInteractionId(dbInt.id);
        setMessages([{ role: "assistant", content: `Hello! Welcome to LuMay Insurance WhatsApp Support. How can I assist you today?`, timestamp: new Date().toISOString() }]);
      }
    } catch (err) { console.error("Failed to start WA:", err); }
  };

  const handleSend = async (text: string) => {
    if (!text.trim() || !interactionId || isSending) return;
    setMessages(prev => [...prev, { role: "user", content: text, timestamp: new Date().toISOString() }]);
    setTextInput(""); setIsSending(true); setTyping(true);
    try {
      const res = await interactionsService.sendMessage(interactionId, text);
      const payload = res.data?.data;
      setTyping(false); setIsSending(false);
      if (payload) setMessages(prev => [...prev, { role: "assistant", content: payload.answer, timestamp: new Date().toISOString() }]);
    } catch (err) { setTyping(false); setIsSending(false); }
  };

  return (
    <div className="h-full w-full flex animate-fade-in bg-[#f0f2f5]">
      
      {/* WhatsApp Web Left Sidebar Simulation */}
      <div className="w-[30%] min-w-[300px] border-r border-[#d1d7db] flex flex-col bg-white">
        {/* Header */}
        <div className="h-16 bg-[#f0f2f5] flex items-center justify-between px-4 shrink-0">
          <div className="h-10 w-10 bg-slate-200 rounded-full flex items-center justify-center font-bold text-slate-500">FA</div>
          <div className="flex gap-4 text-[#54656f]">
            <Plus className="h-6 w-6 cursor-pointer" />
            <MoreVertical className="h-6 w-6 cursor-pointer" />
          </div>
        </div>
        
        {/* Search */}
        <div className="p-2 border-b border-[#f2f2f2]">
          <div className="bg-[#f0f2f5] rounded-lg flex items-center px-3 py-1.5 gap-3">
            <Search className="h-4 w-4 text-[#54656f]" />
            <input type="text" placeholder="Search or start new chat" className="bg-transparent text-sm w-full focus:outline-none placeholder-[#8696a0]" />
          </div>
        </div>
        
        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          <div className="flex items-center gap-4 p-3 hover:bg-[#f5f6f6] cursor-pointer bg-[#f0f2f5]">
            <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center shrink-0 border border-slate-100">
              <MessageSquare className="h-7 w-7 text-[#25D366]" />
            </div>
            <div className="flex-1 min-w-0 border-b border-[#f2f2f2] pb-3 pt-1">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-[17px] text-[#111b21] truncate">LuMay AI Support</h3>
                <span className="text-[12px] text-[#25D366]">10:45</span>
              </div>
              <div className="flex justify-between items-center">
                <p className="text-[14px] text-[#667781] truncate pr-2">Typing...</p>
                <div className="h-5 w-5 bg-[#25D366] rounded-full flex items-center justify-center text-[11px] text-white font-bold">1</div>
              </div>
            </div>
          </div>
          
          {/* Fake Chats */}
          <div className="flex items-center gap-4 p-3 hover:bg-[#f5f6f6] cursor-pointer">
            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
              <span className="text-xl">👨‍👩‍👧</span>
            </div>
            <div className="flex-1 min-w-0 border-b border-[#f2f2f2] pb-3 pt-1">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-[17px] text-[#111b21] truncate">Family Group</h3>
                <span className="text-[12px] text-[#667781]">Yesterday</span>
              </div>
              <p className="text-[14px] text-[#667781] truncate">Ahmed: Let's meet at 8</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 p-3 hover:bg-[#f5f6f6] cursor-pointer">
            <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center shrink-0">
              <span className="text-xl">💼</span>
            </div>
            <div className="flex-1 min-w-0 border-b border-[#f2f2f2] pb-3 pt-1">
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="text-[17px] text-[#111b21] truncate">Work Updates</h3>
                <span className="text-[12px] text-[#667781]">Monday</span>
              </div>
              <p className="text-[14px] text-[#667781] truncate">Meeting notes attached.</p>
            </div>
          </div>
        </div>
      </div>

      {/* WhatsApp Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-[400px]">
        {/* WhatsApp Header */}
        <div className="bg-[#f0f2f5] px-4 h-16 flex items-center justify-between shrink-0 border-b border-[#d1d7db]">
          <div className="flex items-center gap-4 cursor-pointer">
            <div className="h-10 w-10 bg-white rounded-full flex items-center justify-center border border-slate-100">
              <MessageSquare className="h-6 w-6 text-[#25D366]" />
            </div>
            <div>
              <h2 className="text-[16px] text-[#111b21] leading-tight">LuMay AI Support</h2>
              <p className="text-[13px] text-[#667781]">Business Account</p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-[#54656f]">
            <Video className="h-[22px] w-[22px] cursor-pointer" />
            <Phone className="h-[20px] w-[20px] cursor-pointer" />
            <div className="w-[1px] h-6 bg-[#d1d7db] mx-1"></div>
            <Search className="h-5 w-5 cursor-pointer" />
            <MoreVertical className="h-5 w-5 cursor-pointer" />
          </div>
        </div>

        {/* WhatsApp Messages body */}
        <div className="flex-1 overflow-y-auto p-8 space-y-2 relative" style={{ backgroundColor: "#efeae2", backgroundImage: "url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')", backgroundSize: "400px" }}>
          
          <div className="flex justify-center mb-6">
            <span className="bg-white/90 px-3 py-1.5 rounded-lg text-[12.5px] text-[#54656f] shadow-sm uppercase">Today</span>
          </div>
          
          <div className="flex justify-center mb-6">
            <div className="bg-[#ffeecd] px-3 py-2 rounded-lg text-[12.5px] text-[#54656f] shadow-sm max-w-[90%] text-center flex items-center gap-2">
              <span className="text-xl">🔒</span> Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them.
            </div>
          </div>

          {messages.map((m, idx) => {
            const isUser = m.role === "user";
            // Check if previous message was from the same sender to adjust tail
            const prevMessage = idx > 0 ? messages[idx - 1] : null;
            const hasTail = !prevMessage || prevMessage.role !== m.role;
            
            return (
              <div key={idx} className={`flex ${isUser ? "justify-end" : "justify-start"} ${!hasTail ? "mt-0.5" : "mt-2"}`}>
                <div className={`max-w-[65%] px-3 py-1.5 text-[14.2px] relative shadow-[0_1px_0.5px_rgba(11,20,26,.13)] ${isUser ? "bg-[#d9fdd3] text-[#111b21] rounded-lg" : "bg-white text-[#111b21] rounded-lg"} ${hasTail && isUser ? "rounded-tr-none" : ""} ${hasTail && !isUser ? "rounded-tl-none" : ""}`}>
                  
                  {/* CSS Triangle Tails */}
                  {hasTail && isUser && (
                    <div className="absolute top-0 -right-2 w-0 h-0 border-l-[10px] border-l-[#d9fdd3] border-b-[10px] border-b-transparent"></div>
                  )}
                  {hasTail && !isUser && (
                    <div className="absolute top-0 -left-2 w-0 h-0 border-r-[10px] border-r-white border-b-[10px] border-b-transparent"></div>
                  )}

                  <div className="flex flex-col pb-4 pr-12 relative min-w-[70px]">
                    <div className="prose prose-sm max-w-none leading-[20px] text-inherit [&>p]:mb-1 [&>p]:mt-0">
                      <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                    <span className="text-[11px] text-[#667781] absolute bottom-1 right-2 flex items-center gap-1 mt-1">
                      {new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      {isUser && <span className="text-[#53bdeb] font-bold">✓✓</span>}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
          
          {typing && (
            <div className="flex justify-start mt-2">
              <div className="bg-white px-4 py-3 rounded-lg rounded-tl-none shadow-[0_1px_0.5px_rgba(11,20,26,.13)] flex items-center gap-1.5 relative">
                <div className="absolute top-0 -left-2 w-0 h-0 border-r-[10px] border-r-white border-b-[10px] border-b-transparent"></div>
                <span className="w-1.5 h-1.5 bg-[#8696a0] rounded-full animate-bounce" />
                <span className="w-1.5 h-1.5 bg-[#8696a0] rounded-full animate-bounce [animation-delay:0.2s]" />
                <span className="w-1.5 h-1.5 bg-[#8696a0] rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* WhatsApp Input */}
        <div className="bg-[#f0f2f5] px-4 py-3 flex items-end gap-4 shrink-0">
          <div className="flex gap-4 pb-3">
            <Smile className="h-[26px] w-[26px] text-[#54656f] cursor-pointer" />
            <Paperclip className="h-[24px] w-[24px] text-[#54656f] cursor-pointer" />
          </div>
          
          <div className="flex-1 bg-white rounded-lg flex items-center min-h-[44px]">
            <textarea 
              placeholder="Type a message" 
              value={textInput} 
              onChange={e => setTextInput(e.target.value)} 
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(textInput);
                }
              }}
              className="w-full bg-transparent max-h-32 px-4 py-2.5 text-[15px] focus:outline-none resize-none" 
              rows={1}
            />
          </div>
          
          <div className="pb-3">
            {textInput.trim() ? (
              <Send onClick={() => handleSend(textInput)} className="h-[24px] w-[24px] text-[#54656f] cursor-pointer" />
            ) : (
              <Mic className="h-[24px] w-[24px] text-[#54656f] cursor-pointer" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
