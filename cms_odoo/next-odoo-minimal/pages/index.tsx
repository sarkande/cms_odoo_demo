import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the home page
    router.replace("/home");
  }, [router]);

  return null;
}
