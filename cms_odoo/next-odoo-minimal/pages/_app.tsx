import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { TranslationProvider } from "@/contexts/TranslationContext";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <TranslationProvider>
      <Component {...pageProps} />
    </TranslationProvider>
  );
}
