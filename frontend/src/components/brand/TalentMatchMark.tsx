type TalentMatchMarkProps = {
  className?: string;
};

export function TalentMatchMark({ className }: TalentMatchMarkProps) {
  return (
    <svg
      viewBox="0 0 48 48"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M16 14c-4 0-8 4-8 10s4 10 8 10h6" />
      <path d="M32 34c4 0 8-4 8-10s-4-10-8-10h-6" />
      <path d="M18 24h12" />
    </svg>
  );
}
