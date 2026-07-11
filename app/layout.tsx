import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Janaudit AI — Public spending, made clear",
  description: "Evidence-backed public finance intelligence for citizens.",
  icons: { icon: "/favicon.png" }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
