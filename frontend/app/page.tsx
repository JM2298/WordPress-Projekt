import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="panel" style={{ padding: 32 }}>
        <div className="eyebrow">WordPress Projekt</div>
        <h1 className="page-title">Frontend Next.js dla auth i ecommerce</h1>
        <p className="page-copy">
          Ten frontend korzysta z endpointow Django:
          <code> /api/auth/register/</code>,
          <code> /api/auth/token/</code>,
          <code> /api/ecommerce/categories/</code>,
          <code> /api/ecommerce/products/</code>,
          <code> /api/openai/products/generate-create/</code> oraz
          <code> /api/ecommerce/products/{`{id}`}/</code>.
        </p>
        <div className="cards">
          <div className="card">
            <h3>Autoryzacja</h3>
            <p>Nowe widoki logowania i rejestracji z zapisem tokenow JWT.</p>
          </div>
          <div className="card">
            <h3>Ecommerce</h3>
            <p>Tworzenie kategorii, tworzenie produktu, lista i szczegoly produktu.</p>
          </div>
          <div className="card">
            <h3>API backendu</h3>
            <p>Backend dokumentowany jest w ReDoc pod http://localhost:18000/api/redoc/.</p>
          </div>
        </div>
        <div className="button-row" style={{ marginTop: 24 }}>
          <Link className="button" href="/dashboard">
            Otworz widok zarzadzania
          </Link>
          <Link className="secondary-button" href="/openai-products">
            Otworz widok OpenAI
          </Link>
          <Link className="ghost-button" href="/products">
            Zobacz liste produktow
          </Link>
        </div>
      </section>
    </main>
  );
}
