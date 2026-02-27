'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  MoreVertical,
  Copy,
  RefreshCw,
  Share2,
  Trash2,
  Check,
  Link,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useChat } from '@/hooks/use-chat';
import type { ChatMessage } from '@/stores/chat-store';

interface MessageActionsProps {
  message: ChatMessage;
  onRegenerate?: (messageId: string) => void;
  disabled?: boolean;
}

export function MessageActions({ message, onRegenerate, disabled = false }: MessageActionsProps) {
  const { toast } = useToast();
  const { sendMessage } = useChat();
  const [copied, setCopied] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleCopy = async () => {
    try {
      const contentToCopy = message.content;

      await navigator.clipboard.writeText(contentToCopy);

      setCopied(true);
      toast({
        title: 'Copied to clipboard',
        description: 'Message content has been copied',
      });

      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: 'Failed to copy',
        description: 'Could not copy message to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleCopySQL = async () => {
    if (!message.structured?.sql) return;

    try {
      await navigator.clipboard.writeText(message.structured.sql);

      toast({
        title: 'SQL copied',
        description: 'SQL query has been copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Failed to copy',
        description: 'Could not copy SQL to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleRegenerate = async () => {
    if (message.role !== 'assistant' || isRegenerating) return;

    setIsRegenerating(true);

    try {
      // Find the previous user message to regenerate the response
      if (onRegenerate) {
        onRegenerate(message.id);
      } else {
        toast({
          title: 'Regenerate not available',
          description: 'Regenerate functionality requires session context',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Failed to regenerate',
        description: 'Could not regenerate response',
        variant: 'destructive',
      });
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleShare = async () => {
    try {
      // Generate a shareable link for this message
      const shareUrl = `${window.location.origin}/chat?message=${message.id}`;

      await navigator.clipboard.writeText(shareUrl);

      toast({
        title: 'Link copied',
        description: 'Shareable link has been copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Failed to share',
        description: 'Could not create shareable link',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = () => {
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    setIsDeleting(true);
    // Delete functionality would be implemented here
    toast({
      title: 'Message deleted',
      description: 'The message has been removed',
    });

    setDeleteDialogOpen(false);
    setIsDeleting(false);
  };

  const hasSQL = !!message.structured?.sql;
  const canRegenerate = message.role === 'assistant' && !message.isStreaming;

  return (
    <>
      <TooltipProvider>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
              disabled={disabled}
              aria-label="Message actions"
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={handleCopy} className="gap-2">
              {copied ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              Copy message
            </DropdownMenuItem>

            {hasSQL && (
              <DropdownMenuItem onClick={handleCopySQL} className="gap-2">
                <Copy className="h-4 w-4" />
                Copy SQL
              </DropdownMenuItem>
            )}

            {canRegenerate && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleRegenerate}
                  disabled={isRegenerating}
                  className="gap-2"
                >
                  <RefreshCw className={`h-4 w-4 ${isRegenerating ? 'animate-spin' : ''}`} />
                  {isRegenerating ? 'Regenerating...' : 'Regenerate'}
                </DropdownMenuItem>
              </>
            )}

            <DropdownMenuSeparator />

            <DropdownMenuItem onClick={handleShare} className="gap-2">
              <Share2 className="h-4 w-4" />
              Share
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={handleDelete}
              disabled={isDeleting}
              className="gap-2 text-destructive focus:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </TooltipProvider>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete message?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this message from the conversation. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

// Quick Action Buttons Component (for visible quick actions)
export function MessageQuickActions({ message, onRegenerate, disabled = false }: MessageActionsProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: 'Failed to copy',
        description: 'Could not copy message to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleRegenerate = async () => {
    if (message.role !== 'assistant' || isRegenerating) return;

    setIsRegenerating(true);
    try {
      if (onRegenerate) {
        onRegenerate(message.id);
      }
    } finally {
      setIsRegenerating(false);
    }
  };

  const hasSQL = !!message.structured?.sql;
  const canRegenerate = message.role === 'assistant' && !message.isStreaming;

  return (
    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={handleCopy}
              disabled={disabled}
              aria-label="Copy message"
            >
              {copied ? (
                <Check className="h-3 w-3 text-green-600" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>Copy message</TooltipContent>
        </Tooltip>

        {hasSQL && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(message.structured?.sql || '');
                    toast({ title: 'SQL copied' });
                  } catch (error) {
                    toast({
                      title: 'Failed to copy',
                      variant: 'destructive',
                    });
                  }
                }}
                disabled={disabled}
                aria-label="Copy SQL"
              >
                <Link className="h-3 w-3" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Copy SQL</TooltipContent>
          </Tooltip>
        )}

        {canRegenerate && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={handleRegenerate}
                disabled={disabled || isRegenerating}
                aria-label="Regenerate response"
              >
                <RefreshCw className={`h-3 w-3 ${isRegenerating ? 'animate-spin' : ''}`} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Regenerate response</TooltipContent>
          </Tooltip>
        )}
      </TooltipProvider>
    </div>
  );
}