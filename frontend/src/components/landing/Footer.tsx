import Link from "next/link";
import { Linkedin, Twitter, Youtube } from "lucide-react";
import { Container } from "@/components/landing/Container";

const FOOTER_LINKS: Record<string, string[]> = {
  Products: [
    "Complaints Intelligence",
    "Sentiment Analysis",
    "Escalation Management",
    "SLA Monitoring",
    "Agent Assist",
  ],
  Solutions: ["Customer Service", "Claims Management", "Compliance"],
  Resources: ["Case Studies", "Support Center"],
  Company: ["About Us", "Contact Us"],
  Legal: ["Privacy Policy", "Terms of Use"],
};

export function Footer() {
  return (
    <footer className="bg-[#0A1628] text-white pt-16 pb-8">
      <Container>
        {/* Top grid: brand + links */}
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-6 mb-14">
          {/* Brand column */}
          <div className="space-y-5 lg:col-span-2">
            <Link href="/" className="inline-block hover:opacity-90 transition-opacity">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center">
                  <svg viewBox="0 0 40 40" fill="none" className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M20 3L6 8.25V18.75C6 27.67 12 34.95 20 37C28 34.95 34 27.67 34 18.75V8.25L20 3Z"
                      fill="#1E3A8A"
                      stroke="#3B82F6"
                      strokeWidth="3"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M20 11V27M12 19H28"
                      stroke="#10B981"
                      strokeWidth="3.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <div className="flex flex-col -space-y-1.5">
                  <span className="text-xl font-bold tracking-tight text-white">LuMay</span>
                  <span className="text-[13px] font-semibold tracking-wider text-emerald-400 uppercase">Insurance</span>
                </div>
              </div>
            </Link>

            <p className="text-sm leading-relaxed text-slate-400 max-w-[280px]">
              LuMay SMART Insurance AI Hub empowers insurers to deliver intelligent, empathetic and efficient customer experience.
            </p>

            {/* Social Icons */}
            <div className="flex items-center gap-3 pt-1">
              {[
                { icon: <Linkedin className="h-4 w-4" />, href: "#" },
                { icon: <Twitter className="h-4 w-4" />, href: "#" },
                { icon: <Youtube className="h-4 w-4" />, href: "#" },
              ].map((s, i) => (
                <Link
                  key={i}
                  href={s.href}
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-700/60 text-slate-400 hover:border-blue-400 hover:text-blue-300 transition-all"
                >
                  {s.icon}
                </Link>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([section, links]) => (
            <div key={section} className="space-y-4">
              <h4 className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
                {section}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <Link
                      href="#"
                      className="text-sm text-slate-400 hover:text-white transition-colors"
                    >
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="border-t border-slate-800" />

        {/* Bottom row */}
        <div className="flex flex-col items-center justify-between gap-4 pt-8 sm:flex-row text-xs font-medium text-slate-500">
          <p>&copy; 2025 LuMay Insurance. All rights reserved.</p>
          <div className="flex items-center gap-1">
            <span>Made with</span>
            <span className="text-red-400 mx-0.5">❤</span>
            <span>in Oman</span>
          </div>
        </div>
      </Container>
    </footer>
  );
}