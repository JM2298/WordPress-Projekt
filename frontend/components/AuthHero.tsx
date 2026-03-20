type AuthHeroProps = {
  eyebrow: string;
  title: string;
  description: string;
  bullets: string[];
};

export function AuthHero({
  eyebrow,
  title,
  description,
  bullets,
}: AuthHeroProps) {
  return (
    <section className="auth-hero">
      <div className="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{description}</p>
      <ul>
        {bullets.map((bullet) => (
          <li key={bullet}>{bullet}</li>
        ))}
      </ul>
    </section>
  );
}
