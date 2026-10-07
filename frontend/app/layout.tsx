import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "CareerCrew | Local AI Career Intelligence",
  description: "Privacy-first local multi-agent career intelligence powered by Ollama and CrewAI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-zinc-100 min-h-screen flex flex-col antialiased selection:bg-indigo-500/20 selection:text-white">
        <Header />
        <main className="flex-1 flex flex-col min-h-0 w-full overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
