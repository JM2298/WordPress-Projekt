"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Tworzenie kategorii i produktow" },
  { href: "/openai-products", label: "OpenAI: generowanie produktu" },
  { href: "/products", label: "Lista produktow" },
  { href: "/login", label: "Logowanie" },
  { href: "/register", label: "Rejestracja" },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="panel sidebar">
      <div className="eyebrow">Next.js Frontend</div>
      <h3 style={{ marginBottom: 10 }}>Panel integracji WooCommerce</h3>
      <p className="panel-copy">
        Widoki sa podpiete pod backend Django dostepny pod localhost:18000.
      </p>
      <nav>
        {navItems.map((item) => {
          const active =
            pathname === item.href ||
            (item.href !== "/products" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              className={`nav-link${active ? " active" : ""}`}
              href={item.href}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
