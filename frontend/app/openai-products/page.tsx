"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { apiRequest, formatApiError } from "@/lib/api";

type OpenAIProductGeneratePayload = {
  prompt: string;
  type: string;
  regular_price: string;
  category_ids: number[];
};

export default function OpenAIProductsPage() {
  const [status, setStatus] = useState("Wypelnij formularz i wygeneruj produkt przez OpenAI.");
  const [statusType, setStatusType] = useState<"info" | "success" | "error">("info");
  const [rawResponse, setRawResponse] = useState(
    "Odpowiedz endpointu pojawi sie tutaj po wyslaniu formularza.",
  );

  const samplePayload = useMemo(
    () =>
      ({
        prompt: "string",
        type: "simple",
        regular_price: "string",
        category_ids: [1],
      }) satisfies OpenAIProductGeneratePayload,
    [],
  );

  async function submitOpenAIProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const categoryIds = String(formData.get("category_ids") ?? "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean)
      .map((value) => Number(value))
      .filter((value) => Number.isInteger(value) && value > 0);

    const payload: OpenAIProductGeneratePayload = {
      prompt: String(formData.get("prompt") ?? "").trim(),
      type: String(formData.get("type") ?? "").trim() || "simple",
      regular_price: String(formData.get("regular_price") ?? "").trim(),
      category_ids: categoryIds.length ? categoryIds : [1],
    };

    setStatus("Generowanie i tworzenie produktu...");
    setStatusType("info");

    try {
      const response = await apiRequest("/openai/products/generate-create/", {
        method: "POST",
        body: payload,
      });
      setRawResponse(JSON.stringify(response, null, 2));
      setStatus("Produkt zostal wygenerowany i wyslany do WooCommerce.");
      setStatusType("success");
    } catch (error) {
      setRawResponse(formatApiError(error));
      setStatus(error instanceof Error ? error.message : "Blad generowania produktu.");
      setStatusType("error");
    }
  }

  return (
    <main className="page-shell">
      <div className="dashboard-grid">
        <AppSidebar />

        <section className="stack">
          <section className="panel">
            <div className="eyebrow">OpenAI</div>
            <h1 className="page-title">Generowanie produktu przez AI</h1>
            <p className="page-copy">
              Widok wysyla request do <code>POST /api/openai/products/generate-create/</code>.
            </p>
            <div className="button-row">
              <Link className="ghost-button" href="/dashboard">
                Wroc do dashboardu
              </Link>
              <a
                className="secondary-button"
                href="http://localhost:18000/api/redoc/"
                rel="noreferrer"
                target="_blank"
              >
                Otworz ReDoc
              </a>
            </div>
          </section>

          <section className="split">
            <div className="panel">
              <h2>Formularz</h2>
              <p className="panel-copy">
                Kategorie wpisz jako ID oddzielone przecinkami, np. <code>1,5,9</code>.
              </p>

              <form className="form-grid" onSubmit={submitOpenAIProduct}>
                <div className="field">
                  <label htmlFor="openai-prompt">
                    Prompt <small>wymagane</small>
                  </label>
                  <textarea
                    defaultValue="Nowoczesna butelka termiczna 750 ml dla sportowcow."
                    id="openai-prompt"
                    name="prompt"
                    required
                  />
                </div>

                <div className="two-col">
                  <div className="field">
                    <label htmlFor="openai-type">
                      Type <small>domyslnie simple</small>
                    </label>
                    <input defaultValue="simple" id="openai-type" name="type" required />
                  </div>
                  <div className="field">
                    <label htmlFor="openai-price">
                      Regular price <small>tekst, np. 79.99</small>
                    </label>
                    <input defaultValue="79.99" id="openai-price" name="regular_price" required />
                  </div>
                </div>

                <div className="field">
                  <label htmlFor="openai-category-ids">
                    Category IDs <small>oddziel przecinkami</small>
                  </label>
                  <input defaultValue="1" id="openai-category-ids" name="category_ids" />
                </div>

                <button className="button" type="submit">
                  Generuj i utworz produkt
                </button>
              </form>

              <p className={`status ${statusType}`}>{status}</p>
            </div>

            <div className="panel">
              <h2>Przykladowy payload</h2>
              <div className="code-box">{JSON.stringify(samplePayload, null, 2)}</div>
              <h2 style={{ marginTop: 20 }}>Raw response</h2>
              <div className="code-box">{rawResponse}</div>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
