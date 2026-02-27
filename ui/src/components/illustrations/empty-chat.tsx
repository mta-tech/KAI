/**
 * Empty Chat Illustration
 * Used when there are no messages in a chat session
 */
export function EmptyChatIllustration({
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

      {/* Chat bubble 1 */}
      <rect
        x="40"
        y="60"
        width="60"
        height="40"
        rx="8"
        fill="hsl(var(--background))"
        stroke="hsl(var(--muted-foreground))"
        strokeWidth="2"
        opacity="0.6"
      />
      <rect
        x="48"
        y="72"
        width="30"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.4"
      />
      <rect
        x="48"
        y="80"
        width="20"
        height="4"
        rx="2"
        fill="hsl(var(--muted-foreground))"
        opacity="0.4"
      />

      {/* Chat bubble 2 */}
      <rect
        x="100"
        y="100"
        width="60"
        height="40"
        rx="8"
        fill="hsl(var(--primary))"
        opacity="0.8"
      />
      <rect
        x="108"
        y="112"
        width="30"
        height="4"
        rx="2"
        fill="hsl(var(--primary-foreground))"
        opacity="0.6"
      />
      <rect
        x="108"
        y="120"
        width="20"
        height="4"
        rx="2"
        fill="hsl(var(--primary-foreground))"
        opacity="0.6"
      />

      {/* Plus icon for new message */}
      <circle cx="100" cy="160" r="16" fill="hsl(var(--primary))" />
      <path
        d="M100 152V168M92 160H108"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  )
}
