/**
 * Empty Connections Illustration
 * Used when there are no database connections configured
 */
export function EmptyConnectionsIllustration({
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

      {/* Database cylinder (top ellipse) */}
      <ellipse
        cx="100"
        cy="65"
        rx="40"
        ry="15"
        fill="hsl(var(--background))"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
      />

      {/* Database body */}
      <path
        d="M60 65V115C60 123.28 77.91 130 100 130C122.09 130 140 123.28 140 115V65"
        fill="hsl(var(--background))"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
      />

      {/* Database lines */}
      <ellipse
        cx="100"
        cy="90"
        rx="40"
        ry="15"
        fill="none"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="1"
        opacity="0.3"
      />
      <ellipse
        cx="100"
        cy="115"
        rx="40"
        ry="15"
        fill="none"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="1"
        opacity="0.3"
      />

      {/* Connection port */}
      <rect
        x="140"
        y="85"
        width="20"
        height="30"
        rx="4"
        fill="hsl(var(--muted))"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
      />

      {/* Connection cable */}
      <path
        d="M140 100H170"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
        strokeDasharray="4 4"
        opacity="0.5"
      />

      {/* Disconnected plug */}
      <rect
        x="170"
        y="90"
        width="15"
        height="20"
        rx="3"
        fill="hsl(var(--background))"
        stroke="hsl(var(--destructive))"
        strokeWidth="2"
      />

      {/* Plus badge */}
      <circle cx="70" cy="150" r="18" fill="hsl(var(--primary))" />
      <path
        d="M70 142V158M62 150H78"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  )
}
