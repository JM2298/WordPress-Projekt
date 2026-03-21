"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { apiRequest, formatApiError } from "@/lib/api";

type ProductDetail = {
  id: number;
  name: string;
  type?: string;
  status?: string;
  regular_price?: string;
  price?: string;
  permalink?: string;
  description?: string;
  short_description?: string;
  categories?: Array<{ id: number; name?: string }>;
};

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const productId = params.id;
  const [detail, setDetail] = useState<ProductDetail | null>(null);
  const [status, setStatus] = useState("Ladowanie szczegolow produktu...");
  const [statusType, setStatusType] = useState<"info" | "success" | "error">("info");
  const [rawResponse, setRawResponse] = useState("Odpowiedz szczegolowa pojawi sie tutaj.");

  useEffect(() => {
    async function load() {
      try {
        const response = await apiRequest<ProductDetail>(`/ecommerce/products/${productId}/`);
        setDetail(response);
        setRawResponse(JSON.stringify(response, null, 2));
        setStatus("Szczegoly produktu zostaly pobrane.");
        setStatusType("success");
      } catch (error) {
        setRawResponse(formatApiError(error));
        setStatus(error instanceof Error ? error.message : "Nie udalo sie pobrac szczegolow produktu.");
        setStatusType("error");
      }
    }

    if (productId) {
      void load();
    }
  }, [productId]);

  return (
    <main className="page-shell">
      <div className="dashboard-grid">
        <AppSidebar />
        <section className="stack">
          <section className="panel">
            <div className="eyebrow">Widok 3</div>
            <h1 className="page-title">Szczegoly produktu {productId ? `#${productId}` : ""}</h1>
            <p className="page-copy">
              Widok korzysta z <code>GET /api/ecommerce/products/{productId || "{id}"}/</code>.
            </p>
            <div className={`status ${statusType}`}>{status}</div>
            <div className="button-row" style={{ marginTop: 18 }}>
              <Link className="ghost-button" href="/products">
                Wroc do listy
              </Link>
            </div>
          </section>

          <section className="split">
            <div className="panel">
              <h2>Najwazniejsze dane</h2>
              {detail ? (
                <div className="detail-grid">
                  <div className="metric-strip">
                    <span className="metric">ID: {detail.id}</span>
                    <span className="metric">Typ: {detail.type ?? "brak"}</span>
                    <span className="metric">Status: {detail.status ?? "brak"}</span>
                    <span className="metric">Cena: {detail.price ?? detail.regular_price ?? "brak"}</span>
                  </div>

                  <div className="card">
                    <h3>{detail.name}</h3>
                    <p>{detail.short_description || "Brak short_description."}</p>
                  </div>

                  <div className="card">
                    <h3>Opis</h3>
                    <p>{detail.description || "Brak opisu produktu."}</p>
                  </div>

                  <div className="card">
                    <h3>Kategorie</h3>
                    <p>
                      {detail.categories?.length
                        ? detail.categories.map((category) => category.name ?? `#${category.id}`).join(", ")
                        : "Brak kategorii"}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="card">
                  <h3>Brak danych</h3>
                  <p>Szczegoly nie zostaly jeszcze pobrane albo backend zwrocil blad.</p>
                </div>
              )}
            </div>

            <div className="panel">
              <h2>Raw response</h2>
              <div className="code-box">{rawResponse}</div>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
