"use client";

export function ChannelFilter() {
  return (
    <select className="flex h-9 items-center rounded-lg border border-[#E2E8F0] bg-white px-3 text-sm text-[#0F172A] outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]">
      <option value="all">All Channels</option>
      <option value="voice">Voice</option>
      <option value="email">Email</option>
      <option value="whatsapp">WhatsApp</option>
      <option value="chat">Live Chat</option>
      <option value="web_form">Web Form</option>
    </select>
  );
}