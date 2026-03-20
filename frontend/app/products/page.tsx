"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { apiRequest, formatApiError } from "@/lib/api";

type Product = {
  id: number;
  name: string;
  price?: string;
  regular_price?: string;
  status?: string;
  type?: string;
};

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [status, setStatus] = useState("Ladowanie listy produktow...");
  const [statusType, setStatusType] = useState<"info" | "success" | "error">("info");
  const [rawResponse, setRawResponse] = useState("Odpowiedz listy produktow pojawi sie tutaj.");

  useEffect(() => {
    async function loadProducts() {
      try {
        const response = await apiRequest<Product[]>("/ecommerce/products/");
        setProducts(response);
        setRawResponse(JSON.stringify(response, null, 2));
        setStatus(`Pobrano ${response.length} produktow.`);
        setStatusType("success");
      } catch (error) {
        setRawResponse(formatApiError(error));
        setStatus(error instanceof Error ? error.message : "Nie udalo sie pobrac listy produktow.");
        setStatusType("error");
      }
    }

    void loadProducts();
  }, []);

  return (
    <main className="page-shell">
      <div className="dashboard-grid">
        <AppSidebar />
        <section className="stack">
          <section className="panel">
            <div className="eyebrow">Widok 2</div>
            <h1 className="page-title">Lista produktow</h1>
            <p className="page-copy">
              Widok pobiera dane z <code>GET /api/ecommerce/products/</code> i pozwala przejsc do szczegolow produktu.
            </p>
            <div className={`status ${statusType}`}>{status}</div>
          </section>

          <section className="panel">
            <div className="product-list">
              {products.length === 0 ? (
                <div className="card">
                  <h3>Brak produktow</h3>
                  <p>Jesli backend zwraca pusta liste, utworz pierwszy produkt w widoku zarzadzania.</p>
                </div>
              ) : (
                products.map((product) => (
                  <article key={product.id} className="product-row">
                    <div className="product-row-top">
                      <div>
                        <div className="product-name">{product.name}</div>
                        <div className="product-meta">
                          ID: {product.id} | Typ: {product.type ?? "brak"} | Status: {product.status ?? "brak"}
                        </div>
                      </div>
                      <div className="metric-strip">
                        <span className="metric">Cena: {product.price ?? product.regular_price ?? "-"}</span>
                      </div>
                    </div>
                    <div className="button-row">
                      <Link className="button" href={`/products/${product.id}`}>
                        Zobacz szczegoly
                      </Link>
                    </div>
                  </article>
                ))
              )}
            </div>
          </section>

          <section className="panel">
            <h2>Raw response</h2>
            <div className="code-box">{rawResponse}</div>
          </section>
        </section>
      </div>
    </main>
  );
}
