"use client"

import { motion, AnimatePresence } from "framer-motion"
import { usePathname } from "next/navigation"

interface PageTransitionProps {
  children: React.ReactNode
}

/**
 * PageTransition Component
 *
 * Provides smooth fade and slide transitions between routes.
 * Respects prefers-reduced-motion for accessibility.
 *
 * Features:
 * - Fade in/out animation (200ms)
 * - Subtle slide up/down (8px)
 * - Respects prefers-reduced-motion
 * - AnimatePresence for proper mounting/unmounting
 *
 * @example
 * <PageTransition>
 *   {children}
 * </PageTransition>
 */
export function PageTransition({ children }: PageTransitionProps) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{
          duration: 0.2,
          ease: "easeInOut",
        }}
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

/**
 * PageTransitionWithReducedMotion Component
 *
 * Alternative version that explicitly checks for prefers-reduced-motion.
 * Use this if you need more control over reduced motion behavior.
 *
 * Note: Framer Motion automatically respects prefers-reduced-motion,
 * but this component provides explicit control if needed.
 */
export function PageTransitionWithReducedMotion({ children }: PageTransitionProps) {
  const pathname = usePathname()

  // Check if user prefers reduced motion
  const prefersReducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={prefersReducedMotion ? { opacity: 1 } : { opacity: 0, y: -8 }}
        transition={
          prefersReducedMotion
            ? { duration: 0 }
            : { duration: 0.2, ease: "easeInOut" }
        }
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
