export function formatAmount(val: string | number): string {
  const n = typeof val === "string" ? parseFloat(val) : val;
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

export function formatDate(iso: string, currentMonth: number): string {
  const [, , d] = iso.split("-");
  return `${currentMonth.toString().padStart(2, "0")}/${d}`;
}
