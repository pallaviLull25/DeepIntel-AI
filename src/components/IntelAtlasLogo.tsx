type IntelAtlasLogoProps = {
  size?: number;
  className?: string;
};

export default function IntelAtlasLogo({ size = 36, className = "" }: IntelAtlasLogoProps) {
  return (
    <div
      className={`relative shrink-0 overflow-hidden rounded-[1rem] bg-[linear-gradient(145deg,#08121d,#133848_58%,#c77d24)] shadow-[0_16px_34px_rgba(9,18,30,0.24)] ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <div className="absolute inset-[1px] rounded-[0.95rem] bg-[radial-gradient(circle_at_28%_22%,rgba(255,255,255,0.18),transparent_30%),linear-gradient(180deg,rgba(255,255,255,0.08),transparent_46%),linear-gradient(145deg,rgba(5,12,20,0.28),rgba(8,18,29,0.08))]" />

      <svg viewBox="0 0 64 64" className="relative z-10 h-full w-full" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="32" cy="32" r="20" stroke="rgba(255,255,255,0.18)" strokeWidth="1.4" />
        <circle cx="32" cy="32" r="12" stroke="rgba(255,255,255,0.12)" strokeWidth="1.2" />

        <path d="M18 42L29.5 33.5L39 21L48 27.5" stroke="rgba(245,242,234,0.92)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M18 42L25 18L39 21L48 27.5L43 46L18 42Z" stroke="rgba(16,33,50,0.34)" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />

        <circle cx="18" cy="42" r="4.5" fill="#D58A2E" stroke="#FEF3C7" strokeWidth="1.2" />
        <circle cx="29.5" cy="33.5" r="4" fill="#F8FAFC" stroke="#0F172A" strokeWidth="1" />
        <circle cx="39" cy="21" r="5.2" fill="#0F766E" stroke="#CCFBF1" strokeWidth="1.2" />
        <circle cx="48" cy="27.5" r="3.8" fill="#F8FAFC" stroke="#0F172A" strokeWidth="1" />
        <circle cx="43" cy="46" r="3.6" fill="#0F172A" stroke="rgba(255,255,255,0.58)" strokeWidth="1" />

        <path d="M11 51C17 47.8 23.8 46 31.5 46C39.8 46 46.3 47.5 53 51" stroke="rgba(255,255,255,0.16)" strokeWidth="1.3" strokeLinecap="round" />
        <path d="M23.5 12.5C26.2 11.5 29 11 32 11C36.8 11 40.9 12.2 44.8 14.5" stroke="rgba(255,255,255,0.18)" strokeWidth="1.3" strokeLinecap="round" />
      </svg>
    </div>
  );
}
