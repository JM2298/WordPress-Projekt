"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { AuthHero } from "@/components/AuthHero";
import { apiRequest, formatApiError, persistAuth, RegisterPayload } from "@/lib/api";

type RegisterResponse = {
  user: {
    id: number;
    username: string;
    email: string;
  };
  tokens: {
    access: string;
    refresh: string;
  };
};

export default function RegisterPage() {
  const [status, setStatus] = useState("Wypelnij formularz i utworz konto.");
  const [statusType, setStatusType] = useState<"info" | "success" | "error">("info");
  const [responsePayload, setResponsePayload] = useState<string>(
    "Odpowiedz backendu pojawi sie tutaj po wyslaniu formularza.",
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload: RegisterPayload = {
      username: String(formData.get("username") ?? "").trim(),
      email: String(formData.get("email") ?? "").trim(),
      first_name: String(formData.get("first_name") ?? "").trim(),
      last_name: String(formData.get("last_name") ?? "").trim(),
      password: String(formData.get("password") ?? ""),
      password_confirm: String(formData.get("password_confirm") ?? ""),
    };

    setIsSubmitting(true);
    setStatus("Trwa rejestracja...");
    setStatusType("info");

    try {
      const response = await apiRequest<RegisterResponse>("/auth/register/", {
        method: "POST",
        body: payload,
      });

      persistAuth({
        access: response.tokens.access,
        refresh: response.tokens.refresh,
        user: response.user,
      });

      setResponsePayload(JSON.stringify(response, null, 2));
      setStatus("Konto zostalo utworzone i zapisano tokeny JWT.");
      setStatusType("success");
      form.reset();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Nieznany blad rejestracji.";
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
          eyebrow="Register"
          title="Rejestracja podpieta pod backend Django"
          description="Ten ekran jest zgodny z kontraktem widocznym w ReDoc i wysyla POST /api/auth/register/."
          bullets={[
            "wysyla username, email, first_name, last_name, password i password_confirm",
            "odbiera user oraz pare tokenow JWT",
            "stanowi punkt wejscia do panelu ecommerce",
          ]}
        />
        <section className="auth-form">
          <div className="eyebrow">POST /api/auth/register/</div>
          <h2 className="page-title">Utworz konto</h2>
          <p className="page-copy">
            Formularz odpowiada backendowemu serializerowi i pokazuje surowa odpowiedz API.
          </p>

          <form className="form-grid" onSubmit={handleSubmit}>
            <div className="two-col">
              <div className="field">
                <label htmlFor="username">
                  Username <small>wymagane</small>
                </label>
                <input id="username" name="username" maxLength={150} required />
              </div>
              <div className="field">
                <label htmlFor="email">
                  Email <small>opcjonalne</small>
                </label>
                <input id="email" name="email" type="email" maxLength={254} />
              </div>
            </div>

            <div className="two-col">
              <div className="field">
                <label htmlFor="first_name">
                  First name <small>opcjonalne</small>
                </label>
                <input id="first_name" name="first_name" maxLength={150} />
              </div>
              <div className="field">
                <label htmlFor="last_name">
                  Last name <small>opcjonalne</small>
                </label>
                <input id="last_name" name="last_name" maxLength={150} />
              </div>
            </div>

            <div className="two-col">
              <div className="field">
                <label htmlFor="password">
                  Password <small>min. 8 znakow</small>
                </label>
                <input id="password" name="password" type="password" minLength={8} required />
              </div>
              <div className="field">
                <label htmlFor="password_confirm">
                  Confirm password <small>wymagane</small>
                </label>
                <input
                  id="password_confirm"
                  name="password_confirm"
                  type="password"
                  minLength={8}
                  required
                />
              </div>
            </div>

            <div className="button-row">
              <button className="button" disabled={isSubmitting} type="submit">
                {isSubmitting ? "Rejestracja..." : "Zarejestruj"}
              </button>
              <Link className="ghost-button" href="/login">
                Mam juz konto
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
