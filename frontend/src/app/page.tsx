import { Header } from "@/components/landing/Header";
import { Hero } from "@/components/landing/Hero";
import { WhyChooseSection } from "@/components/landing/WhyChooseSection";
import { BenefitsSection } from "@/components/landing/BenefitsSection";
import { CTASection } from "@/components/landing/CTASection";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Hero />
        <WhyChooseSection />
        <BenefitsSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}