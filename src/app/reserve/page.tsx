import type { Metadata } from "next";
import { ReserveForm } from "./ReserveForm";

export const metadata: Metadata = { title: "Reserve | KINETIQ" };

export default function ReservePage() {
  return (
    <main id="main" className="reserve-page">
      <ReserveForm />
    </main>
  );
}
