/**
 * Empty Knowledge Base Illustration
 * Used when there are no entries in the knowledge base
 */
export function EmptyKnowledgeIllustration({
  className = "",
  size = 200,
}: {
  className?: string
  size?: number
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* Background circle */}
      <circle cx="100" cy="100" r="80" fill="hsl(var(--muted))" opacity="0.3" />

      {/* Book spine */}
      <rect
        x="50"
        y="50"
        width="100"
        height="120"
        rx="8"
        fill="hsl(var(--background))"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
      />

      {/* Book pages effect */}
      <rect
        x="60"
        y="50"
        width="80"
        height="120"
        rx="4"
        fill="none"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="1"
        opacity="0.3"
      />

      {/* Title line */}
      <rect
        x="70"
        y="75"
        width="60"
        height="8"
        rx="4"
        fill="hsl(var(--muted-foreground))"
        opacity="0.4"
      />

      {/* Content lines */}
      <rect
        x="70"
        y="95"
        width="50"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.3"
      />
      <rect
        x="70"
        y="105"
        width="60"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.3"
      />
      <rect
        x="70"
        y="115"
        width="40"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.3"
      />
      <rect
        x="70"
        y="125"
        width="55"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.3"
      />
      <rect
        x="70"
        y="135"
        width="45"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.3"
      />

      {/* Plus badge */}
      <circle cx="150" cy="150" r="20" fill="hsl(var(--primary))" />
      <path
        d="M150 140V160M140 150H160"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  )
}
