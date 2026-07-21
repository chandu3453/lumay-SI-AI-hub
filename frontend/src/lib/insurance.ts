export const INSURANCE_LINES = [
  "All",
  "Motor",
  "Medical & Health",
  "Travel",
  "Home",
  "Life",
  "Business Insurance",
  "Policy Servicing",
  "Renewals",
  "Claims",
  "Payments & Refunds",
  "Provider & Garage Services",
] as const;

export type InsuranceLine = (typeof INSURANCE_LINES)[number];

export const INSURANCE_PRODUCTS: Record<string, string[]> = {
  Motor: ["Motor Comprehensive Plus", "Motor Third Party", "Motor Comprehensive", "Motor Fleet", "Commercial Vehicle"],
  "Medical & Health": ["Health Gold", "Health Silver", "Health Platinum", "Family Floater", "Critical Illness"],
  Travel: ["Travel Single Trip", "Travel Annual Multi-Trip", "Travel Student", "Travel Business"],
  Home: ["Home Structure", "Home Contents", "Home Comprehensive", "Landlord Insurance"],
  Life: ["Term Life", "Whole Life", "Endowment Plan", "Unit Linked", "Retirement Plan"],
  "Business Insurance": ["Business Package", "Professional Indemnity", "Public Liability", "Cyber Insurance"],
  "Policy Servicing": ["Policy Endorsement", "Policy Renewal", "Policy Cancellation"],
  Renewals: ["Auto Renewal", "Manual Renewal", "Lapsed Renewal"],
  Claims: ["Motor Claim", "Health Claim", "Travel Claim", "Property Claim"],
  "Payments & Refunds": ["Premium Payment", "Refund Processing", "Installment Plan"],
  "Provider & Garage Services": ["Network Garage", "Cashless Garage", "Approved Service Center"],
};

export function getProductsForLine(line: string): string[] {
  return INSURANCE_PRODUCTS[line] ?? [];
}

export function generatePolicyNumber(index: number): string {
  return `POL-${new Date().getFullYear()}-${String(100000 + index).slice(1)}`;
}

export function getLineColor(line: string): string {
  const colors: Record<string, string> = {
    Motor: "#2563EB",
    "Medical & Health": "#16A34A",
    Travel: "#8B5CF6",
    Home: "#F59E0B",
    Life: "#EC4899",
    "Business Insurance": "#06B6D4",
    "Policy Servicing": "#F97316",
    Renewals: "#64748B",
    Claims: "#DC2626",
    "Payments & Refunds": "#14B8A6",
    "Provider & Garage Services": "#6366F1",
  };
  return colors[line] ?? "#94A3B8";
}

// TODO: Replace with API call
export function generateMockPolicy(index: number): { insurance_line: string; product_name: string; policy_number: string } {
  const lines = INSURANCE_LINES.filter((l) => l !== "All");
  const line = lines[index % lines.length];
  const products = getProductsForLine(line);
  return {
    insurance_line: line,
    product_name: products[index % products.length] ?? line,
    policy_number: generatePolicyNumber(index),
  };
}

// TODO: Replace with API call
export function mockPolicyForLine(line: string, idx: number): { insurance_line: string; product_name: string; policy_number: string } {
  const products = getProductsForLine(line);
  return {
    insurance_line: line,
    product_name: products[idx % products.length] ?? line,
    policy_number: generatePolicyNumber(idx + 100),
  };
}
