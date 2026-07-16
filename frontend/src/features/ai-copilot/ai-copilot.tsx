"use client";

import { useState, useCallback } from "react";
import { Bot, X, Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { demoService } from "@/services/demo.service";

export function AICopilot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState("");

  const { data: answer, isFetching } = useQuery({
    queryKey: ["ai-copilot", currentQuestion],
    queryFn: async () => {
      const res = await demoService.askQuestion(currentQuestion);
      return res.data.data;
    },
    enabled: currentQuestion.length > 0,
    retry: 1,
  });

  const handleSend = useCallback(async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setInput("");
    setCurrentQuestion(userMsg);
  }, [input]);

  if (answer && currentQuestion && !messages.find(m => m.role === "assistant" && m.content === answer.answer)) {
    setMessages((prev) => [...prev, { role: "assistant", content: answer.answer ?? "No response available." }]);
    setCurrentQuestion("");
  }

  return (
    <>
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 h-12 w-12 rounded-xl shadow-lg shadow-primary/20 z-50"
          size="icon"
        >
          <Bot className="h-5 w-5" />
        </Button>
      )}
      {isOpen && (
        <Card className="fixed bottom-6 right-6 w-80 sm:w-96 shadow-dropdown z-50 border-border bg-white dark:bg-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 border-b border-border">
            <CardTitle className="text-sm flex items-center gap-2">
              <Bot className="h-4 w-4 text-primary" />
              AI Copilot
              <Sparkles className="h-3 w-3 text-warning" />
            </CardTitle>
            <Button variant="ghost" size="icon" className="h-6 w-6 text-muted-foreground hover:text-foreground" onClick={() => setIsOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="h-72 overflow-y-auto p-4 space-y-3">
              {messages.length === 0 && (
                <div className="text-center text-sm text-muted-foreground py-8">
                  <Bot className="h-8 w-8 mx-auto mb-2 text-muted-foreground/40" />
                  <p>Ask me about the platform data, KPIs, or business processes</p>
                  <div className="mt-4 space-y-1.5">
                    <button onClick={() => { setInput("How do I file a claim?"); }} className="text-xs text-primary hover:underline block w-full">How do I file a claim?</button>
                    <button onClick={() => { setInput("What is the SLA compliance rate?"); }} className="text-xs text-primary hover:underline block w-full">What is the SLA compliance rate?</button>
                    <button onClick={() => { setInput("Show me the complaint trends"); }} className="text-xs text-primary hover:underline block w-full">Show me the complaint trends</button>
                  </div>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm ${
                    msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isFetching && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm bg-muted">
                    <div className="flex gap-1">
                      <span className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="border-t border-border p-3">
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
                <Input placeholder="Ask about the platform..." value={input} onChange={(e) => setInput(e.target.value)} className="flex-1 h-9" />
                <Button type="submit" size="icon" className="h-9 w-9 shrink-0" disabled={!input.trim() || isFetching}>
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
}