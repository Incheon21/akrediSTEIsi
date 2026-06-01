import type { Metadata } from "next";
import { Inria_Serif, Space_Grotesk } from "next/font/google";
import "./globals.css";
import ConditionalNavbar from "./components/navigation/ConditionalNavbar";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const inriaSerif = Inria_Serif({
  variable: "--font-inria-serif",
  subsets: ["latin"],
  weight: ["300", "400", "700"],
});

export const metadata: Metadata = {
  title: "STEI Accreditation Workspace",
  description: "Kelola data akreditasi LKPS dan LED dalam satu workspace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${inriaSerif.variable} font-sans antialiased`}>
        <ConditionalNavbar />
        {children}
      </body>
    </html>
  );
}
