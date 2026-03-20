"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { AuthHero } from "@/components/AuthHero";
import { apiRequest, formatApiError, persistAuth } from "@/lib/api";

type LoginResponse = {
  access: string;
  refresh: string;
};

export default function LoginPage() {
  const [status, setStatus] = useState("Wprowadz dane logowania.");
  const [statusType, setStatusType] = useState<"info" | "success" | "error">("info");
  const [responsePayload, setResponsePayload] = useState<string>(
    "Po zalogowaniu zobaczysz tutaj otrzymane tokeny JWT.",
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = {
      username: String(formData.get("username") ?? "").trim(),
      password: String(formData.get("password") ?? ""),
    };

    setIsSubmitting(true);
    setStatus("Trwa logowanie...");
    setStatusType("info");

    try {
      const response = await apiRequest<LoginResponse>("/auth/token/", {
        method: "POST",
        body: payload,
      });

      persistAuth({ access: response.access, refresh: response.refresh });
      setResponsePayload(JSON.stringify(response, null, 2));
      setStatus("Logowanie zakonczone sukcesem. Tokeny zapisano w localStorage.");
      setStatusType("success");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Nieznany blad logowania.";
      setResponsePayload(formatApiError(error));
      setStatus(message);
      setStatusType("error");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <AuthHero
          eyebrow="JWT Login"
          title="Nowe logowanie dla panelu produktowego"
          description="Widok zostal zrefaktoryzowany do Next.js i korzysta bezposrednio z backendowego POST /api/auth/token/."
          bullets={[
            "wysyla username i password do backendu Django",
            "zapisuje access i refresh token w localStorage",
            "przygotowuje uzytkownika do pracy z widokami ecommerce",
          ]}
        />
        <section className="auth-form">
          <div className="eyebrow">POST /api/auth/token/</div>
          <h2 className="page-title">Zaloguj sie</h2>
          <p className="page-copy">
            Uzyj danych testowego uzytkownika albo konta utworzonego przez ekran rejestracji.
          </p>

          <form className="form-grid" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="username">
                Username <small>wymagane</small>
              </label>
              <input id="username" name="username" required />
            </div>

            <div className="field">
              <label htmlFor="password">
                Password <small>wymagane</small>
              </label>
              <input id="password" name="password" type="password" required />
            </div>

            <div className="button-row">
              <button className="button" disabled={isSubmitting} type="submit">
                {isSubmitting ? "Logowanie..." : "Zaloguj"}
              </button>
              <Link className="ghost-button" href="/register">
                Przejdz do rejestracji
              </Link>
            </div>
          </form>

          <p className={`status ${statusType}`}>{status}</p>
          <div className="code-box">{responsePayload}</div>
        </section>
      </div>
    </main>
  );
}
