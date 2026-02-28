/**
 * Empty Tables Illustration
 * Used when there are no tables in the database explorer
 */
export function EmptyTablesIllustration({
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

      {/* Table structure */}
      <rect
        x="40"
        y="50"
        width="120"
        height="100"
        rx="8"
        fill="hsl(var(--background))"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
      />

      {/* Header row */}
      <rect
        x="40"
        y="50"
        width="120"
        height="25"
        rx="8"
        fill="hsl(var(--muted))"
        opacity="0.5"
      />
      <rect
        x="40"
        y="75"
        width="120"
        height="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />

      {/* Empty rows */}
      <rect
        x="50"
        y="90"
        width="40"
        height="6"
        rx="3"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />
      <rect
        x="95"
        y="90"
        width="55"
        height="6"
        rx="3"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />

      <rect
        x="50"
        y="105"
        width="50"
        height="6"
        rx="3"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />
      <rect
        x="105"
        y="105"
        width="45"
        height="6"
        rx="3"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />

      <rect
        x="50"
        y="120"
        width="35"
        height="6"
        rx="3"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />
      <rect
        x="90"
        y="120"
        width="60"
        height="6"
        rx="3"
        fill="hsl(var(--muted-foreground))"
        opacity="0.2"
      />

      {/* Search icon */}
      <circle cx="100" cy="165" r="16" fill="hsl(var(--primary))" />
      <circle
        cx="100"
        cy="165"
        r="8"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="2"
        fill="none"
      />
      <path
        d="M106 171L110 175"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}
