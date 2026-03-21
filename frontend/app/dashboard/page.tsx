"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { AppSidebar } from "@/components/AppSidebar";
import { apiRequest, CategoryPayload, formatApiError, ProductPayload } from "@/lib/api";

export default function DashboardPage() {
  const [categoryStatus, setCategoryStatus] = useState("Utworz nowa kategorie produktowa.");
  const [categoryType, setCategoryType] = useState<"info" | "success" | "error">("info");
  const [categoryResponse, setCategoryResponse] = useState("Tutaj zobaczysz odpowiedz backendu dla kategorii.");
  const [productStatus, setProductStatus] = useState("Utworz nowy produkt WooCommerce.");
  const [productType, setProductType] = useState<"info" | "success" | "error">("info");
  const [productResponse, setProductResponse] = useState("Tutaj zobaczysz odpowiedz backendu dla produktu.");

  async function submitCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const image = String(formData.get("image") ?? "").trim();
    const payload: CategoryPayload = {
      name: String(formData.get("name") ?? "").trim(),
      ...(image ? { image: { src: image } } : {}),
    };

    setCategoryStatus("Tworzenie kategorii...");
    setCategoryType("info");

    try {
      const response = await apiRequest("/ecommerce/categories/", {
        method: "POST",
        body: payload,
      });
      setCategoryResponse(JSON.stringify(response, null, 2));
      setCategoryStatus("Kategoria zostala utworzona.");
      setCategoryType("success");
    } catch (error) {
      setCategoryResponse(formatApiError(error));
      setCategoryStatus(error instanceof Error ? error.message : "Blad tworzenia kategorii.");
      setCategoryType("error");
    }
  }

  async function submitProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const categoryIds = String(formData.get("categories") ?? "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean)
      .map((value) => ({ id: Number(value) }));
    const imageUrls = String(formData.get("images") ?? "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean)
      .map((src) => ({ src }));

    const payload: ProductPayload = {
      name: String(formData.get("name") ?? "").trim(),
      type: String(formData.get("type") ?? "").trim(),
      regular_price: String(formData.get("regular_price") ?? "").trim(),
      description: String(formData.get("description") ?? "").trim(),
      short_description: String(formData.get("short_description") ?? "").trim(),
      ...(categoryIds.length ? { categories: categoryIds } : {}),
      ...(imageUrls.length ? { images: imageUrls } : {}),
    };

    setProductStatus("Tworzenie produktu...");
    setProductType("info");

    try {
      const response = await apiRequest("/ecommerce/products/", {
        method: "POST",
        body: payload,
      });
      setProductResponse(JSON.stringify(response, null, 2));
      setProductStatus("Produkt zostal utworzony.");
      setProductType("success");
    } catch (error) {
      setProductResponse(formatApiError(error));
      setProductStatus(error instanceof Error ? error.message : "Blad tworzenia produktu.");
      setProductType("error");
    }
  }

  return (
    <main className="page-shell">
      <div className="dashboard-grid">
        <AppSidebar />

        <section className="stack">
          <section className="panel">
            <div className="eyebrow">Widok 1</div>
            <h1 className="page-title">Tworzenie kategorii i produktow</h1>
            <p className="page-copy">
              Ten ekran obsluguje dwa endpointy z backendu:
              <code> POST /api/ecommerce/categories/</code> oraz
              <code> POST /api/ecommerce/products/</code>.
            </p>
            <div className="button-row">
              <Link className="ghost-button" href="/products">
                Przejdz do listy produktow
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
              <h2>Nowa kategoria produktu</h2>
              <p className="panel-copy">Wysyla payload zgodny z CategoryCreateSerializer.</p>
              <form className="form-grid" onSubmit={submitCategory}>
                <div className="field">
                  <label htmlFor="category-name">
                    Name <small>wymagane</small>
                  </label>
                  <input id="category-name" name="name" required />
                </div>
                <div className="field">
                  <label htmlFor="category-image">
                    Image URL <small>opcjonalne, najlepiej bezposredni .jpg/.png</small>
                  </label>
                  <input
                    id="category-image"
                    name="image"
                    placeholder="https://example.com/category.jpg"
                  />
                </div>
                <button className="button" type="submit">
                  Utworz kategorie
                </button>
              </form>
              <p className={`status ${categoryType}`}>{categoryStatus}</p>
              <div className="code-box">{categoryResponse}</div>
            </div>

            <div className="panel">
              <h2>Nowy produkt</h2>
              <p className="panel-copy">Wysyla payload zgodny z ProductCreateSerializer.</p>
              <form className="form-grid" onSubmit={submitProduct}>
                <div className="field">
                  <label htmlFor="product-name">
                    Name <small>wymagane</small>
                  </label>
                  <input id="product-name" name="name" required />
                </div>

                <div className="two-col">
                  <div className="field">
                    <label htmlFor="product-type">
                      Type <small>np. simple</small>
                    </label>
                    <input defaultValue="simple" id="product-type" name="type" required />
                  </div>
                  <div className="field">
                    <label htmlFor="product-price">
                      Regular price <small>tekst, np. 21.99</small>
                    </label>
                    <input id="product-price" name="regular_price" required />
                  </div>
                </div>

                <div className="field">
                  <label htmlFor="product-short-description">
                    Short description <small>opcjonalne</small>
                  </label>
                  <textarea id="product-short-description" name="short_description" />
                </div>

                <div className="field">
                  <label htmlFor="product-description">
                    Description <small>opcjonalne</small>
                  </label>
                  <textarea id="product-description" name="description" />
                </div>

                <div className="two-col">
                  <div className="field">
                    <label htmlFor="product-categories">
                      Category IDs <small>np. 9,14</small>
                    </label>
                    <input id="product-categories" name="categories" placeholder="9,14" />
                  </div>
                  <div className="field">
                    <label htmlFor="product-images">
                      Image URLs <small>oddziel przecinkami</small>
                    </label>
                    <input
                      id="product-images"
                      name="images"
                      placeholder="https://example.com/a.jpg, https://example.com/b.jpg"
                    />
                  </div>
                </div>

                <button className="button" type="submit">
                  Utworz produkt
                </button>
              </form>
              <p className={`status ${productType}`}>{productStatus}</p>
              <div className="code-box">{productResponse}</div>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
