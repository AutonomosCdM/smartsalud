"use client";

import { useState } from "react";
import { VoiceAgent } from "@/components/VoiceAgent";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { Services } from "@/components/Services";
import { Schedule } from "@/components/Schedule";
import { Contact } from "@/components/Contact";
import { Footer } from "@/components/Footer";

export default function Home() {
  const [isAgentOpen, setIsAgentOpen] = useState(false);

  return (
    <main className="min-h-screen bg-background">
      <Header onOpenAgent={() => setIsAgentOpen(true)} />
      <Hero onOpenAgent={() => setIsAgentOpen(true)} />
      <HowItWorks />
      <Services />
      <Schedule onOpenAgent={() => setIsAgentOpen(true)} />
      <Contact />
      <Footer />

      {/* Voice Agent */}
      <VoiceAgent isOpen={isAgentOpen} onClose={() => setIsAgentOpen(false)} />
    </main>
  );
}
