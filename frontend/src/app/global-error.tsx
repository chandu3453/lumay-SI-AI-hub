"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="bg-[#F8FAFC] dark:bg-background">
        <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-4">
          <h1 className="text-4xl font-bold text-foreground">500</h1>
          <p className="text-muted-foreground">Application error</p>
          <p className="text-sm text-muted-foreground/60 max-w-md text-center">
            {error.message || "An unexpected error occurred"}
          </p>
          <button
            onClick={reset}
            className="inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}