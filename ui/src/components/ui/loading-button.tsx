import * as React from "react"
import { Button, type ButtonProps } from "@/components/ui/button"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingButtonProps extends ButtonProps {
  isLoading?: boolean
  loadingText?: string
}

const LoadingButton = React.forwardRef<HTMLButtonElement, LoadingButtonProps>(
  ({ className, isLoading, loadingText, disabled, children, ...props }, ref) => {
    const isDisabled = isLoading || disabled

    return (
      <Button
        className={cn(className)}
        ref={ref}
        disabled={isDisabled}
        {...props}
      >
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {isLoading && loadingText ? loadingText : children}
      </Button>
    )
  }
)
LoadingButton.displayName = "LoadingButton"

export { LoadingButton }
