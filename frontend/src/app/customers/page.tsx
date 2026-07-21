"use client";

import { useState, useCallback, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ShieldOff } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { useCustomerList, useCustomerKPIs, useCustomerProfile, useCustomerComplaints, useCustomerInteractions, useCustomerComplaintTrend, useCustomerComplaintThemes } from "@/features/customers/hooks/use-customers";
import { useDebounce } from "@/hooks/use-debounce";
import { InsuranceFilter } from "@/components/insurance/InsuranceFilter";
import { CustomerHeader, CustomerFilters, CustomerKPICards, CustomerTable, CustomerProfile, CustomerTabs, CustomerSummary, ComplaintTrendChart, ComplaintThemes, RecentInteraction, CustomerActions } from "@/components/customers";
import type { CustomerTabId } from "@/components/customers";
import type { Customer } from "@/types/domain";

const PAGE_SIZE = 10;

function CustomersContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const searchFromUrl = searchParams.get("search") ?? "";
  const pageFromUrl = parseInt(searchParams.get("page") ?? "1", 10);
  const segmentFromUrl = searchParams.get("segment") ?? "";
  const riskFromUrl = searchParams.get("risk") ?? "";
  const typeFromUrl = searchParams.get("type") ?? "";
  const customerIdFromUrl = searchParams.get("customer") ?? "";

  const [search, setSearch] = useState(searchFromUrl);
  const [page, setPage] = useState(pageFromUrl);
  const [segment, setSegment] = useState(segmentFromUrl);
  const [riskLevel, setRiskLevel] = useState(riskFromUrl);
  const [customerType, setCustomerType] = useState(typeFromUrl);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(customerIdFromUrl || null);
  const [profileTab, setProfileTab] = useState<CustomerTabId>("overview");
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    setPage(1);
  }, [selectedCustomerId]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (page > 1) params.set("page", String(page));
    if (segment) params.set("segment", segment);
    if (riskLevel) params.set("risk", riskLevel);
    if (customerType) params.set("type", customerType);
    if (selectedCustomerId) params.set("customer", selectedCustomerId);
    const qs = params.toString();
    router.replace(`/customers${qs ? `?${qs}` : ""}`, { scroll: false });
  }, [search, page, segment, riskLevel, customerType, selectedCustomerId, router]);

  const { data, isLoading } = useCustomerList({
    page,
    page_size: PAGE_SIZE,
    search: debouncedSearch || undefined,
    segment: segment || undefined,
    risk_level: riskLevel || undefined,
    customer_type: customerType || undefined,
  });

  const { data: kpis } = useCustomerKPIs();
  const { data: profile, isLoading: profileLoading } = useCustomerProfile(selectedCustomerId);
  const { data: complaintsData } = useCustomerComplaints(selectedCustomerId);
  const { data: interactionsData } = useCustomerInteractions(selectedCustomerId);
  const { data: trendData, isLoading: trendLoading } = useCustomerComplaintTrend(selectedCustomerId);
  const { data: themesData, isLoading: themesLoading } = useCustomerComplaintThemes(selectedCustomerId);

  const handleSelectCustomer = useCallback((customer: Customer) => {
    setSelectedCustomerId(customer.id);
    setProfileTab("overview");
  }, []);

  const handleClearFilters = useCallback(() => {
    setSegment(""); setRiskLevel(""); setCustomerType(""); setDateFrom(""); setDateTo(""); setSearch(""); setPage(1);
  }, []);

  const handleApplyFilters = useCallback(() => { setPage(1); }, []);

  const items = (data?.items ?? []) as Customer[];
  const profileCustomer = profile as Customer | null;
  const complaints = complaintsData?.items ?? [];
  const interactions = interactionsData?.items ?? [];
  const lastInteraction = interactions.length > 0 ? interactions[0] : null;

  return (
    <div className="space-y-8 animate-fade-in text-left">
      <CustomerHeader />

      <CustomerFilters
        search={search} onSearchChange={setSearch}
        segment={segment} onSegmentChange={setSegment}
        riskLevel={riskLevel} onRiskLevelChange={setRiskLevel}
        customerType={customerType} onCustomerTypeChange={setCustomerType}
        dateFrom={dateFrom} dateTo={dateTo} onDateFromChange={setDateFrom} onDateToChange={setDateTo}
        onClear={handleClearFilters} onApply={handleApplyFilters}
      />

      {kpis && (
        <CustomerKPICards
          totalCustomers={kpis.total_customers}
          withComplaints={kpis.with_complaints}
          repeatComplaints={kpis.repeat_complaints}
          highRisk={kpis.high_risk}
        />
      )}

      {/* Grid container: Left side Table (60%), Right side Profile Detail Drawer (40%) */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.55fr_1fr] gap-8 items-start">
        <CustomerTable
          data={items}
          isLoading={isLoading}
          total={data?.total}
          page={page}
          pageSize={PAGE_SIZE}
          onPageChange={setPage}
          selectedId={selectedCustomerId}
          onSelect={handleSelectCustomer}
        />

        <div className="space-y-4">
          <CustomerProfile customer={profileCustomer} isLoading={profileLoading} />

          {/* Render right-hand overview by default to look high-fidelity */}
          {(profileCustomer || !selectedCustomerId) && (
            <>
              <CustomerTabs activeTab={profileTab} onTabChange={setProfileTab} />

              {profileTab === "overview" && (
                <div className="space-y-4">
                  <CustomerSummary
                    customer={profileCustomer || ({} as any)}
                    complaintCount={complaints.length}
                    repeatComplaints={complaints.filter((c: any) => c.is_repeat).length}
                    lastComplaint={complaints.length > 0 ? complaints[0].created_at : null}
                  />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <ComplaintTrendChart data={trendData ?? []} isLoading={trendLoading} />
                    <ComplaintThemes themes={themesData ?? []} isLoading={themesLoading} />
                  </div>

                  <RecentInteraction
                    interaction={lastInteraction ? { channel: lastInteraction.channel, message: lastInteraction.last_message ?? lastInteraction.subject ?? undefined, created_at: lastInteraction.created_at } : null}
                    isLoading={false}
                    onViewAll={() => setProfileTab("interactions")}
                  />

                  <CustomerActions
                    onViewComplaints={() => setProfileTab("complaints")}
                    onCreateComplaint={() => router.push(`/complaint-cases?customer=${selectedCustomerId}`)}
                    onAddNote={() => setProfileTab("notes")}
                  />
                </div>
              )}

              {profileTab === "complaints" && (
                <div className="bg-white dark:bg-card rounded-xl border border-border shadow-card p-5">
                  {complaints.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">No complaints found for this customer</p>
                  ) : (
                    <div className="space-y-2">
                      {complaints.map((c: any) => (
                        <div key={c.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                          <div>
                            <p className="text-sm font-medium">{c.title}</p>
                            <p className="text-xs text-muted-foreground capitalize">{c.status} · {c.category}</p>
                          </div>
                          <button onClick={() => router.push(`/complaint-cases/${c.id}`)} className="text-xs text-primary hover:underline">View</button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {profileTab === "interactions" && (
                <div className="bg-white dark:bg-card rounded-xl border border-border shadow-card p-5">
                  {interactions.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">No interactions found for this customer</p>
                  ) : (
                    <div className="space-y-2">
                      {interactions.map((i: any) => (
                        <div key={i.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                          <div>
                            <p className="text-sm font-medium">{i.subject ?? "No subject"}</p>
                            <p className="text-xs text-muted-foreground capitalize">{i.channel} · {i.status}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {profileTab === "policies" && (
                <div className="bg-white dark:bg-card rounded-xl border border-border shadow-card p-10 text-center">
                  <ShieldOff className="h-6 w-6 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Policy data is not yet available — no backing data source integrated in this phase.</p>
                </div>
              )}

              {profileTab === "notes" && (
                <div className="bg-white dark:bg-card rounded-xl border border-border shadow-card p-10 text-center">
                  <p className="text-sm text-muted-foreground">No notes recorded for this customer.</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function LoadingFallback() {
  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header"><h1>Customers</h1><p>View customer profiles, interaction history, and complaint overview.</p></div>
        <div className="h-24 rounded-xl bg-muted animate-pulse" />
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />)}
        </div>
        <div className="flex gap-6">
          <div className="w-[480px]"><div className="h-64 rounded-xl bg-muted animate-pulse" /></div>
          <div className="flex-1"><div className="h-64 rounded-xl bg-muted animate-pulse" /></div>
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

export default function CustomersPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DashboardShell>
        <CustomersContent />
        <AICopilot />
      </DashboardShell>
    </Suspense>
  );
}