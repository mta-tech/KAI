'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown, Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { feedbackApi } from '@/lib/api/context';
import type { FeedbackVote } from '@/lib/api/types';

interface MissionFeedbackProps {
  missionId: string;
  onSubmitted?: () => void;
}

export function MissionFeedback({ missionId, onSubmitted }: MissionFeedbackProps) {
  const [selectedVote, setSelectedVote] = useState<FeedbackVote | null>(null);
  const [explanation, setExplanation] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!selectedVote) return;

    setSubmitting(true);

    try {
      await feedbackApi.submitFeedback({
        mission_run_id: missionId,
        vote: selectedVote,
        explanation: explanation || undefined,
      });

      setSubmitted(true);
      onSubmitted?.();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="rounded-lg border bg-emerald-500/10 border-emerald-500/20 p-4">
        <div className="text-sm text-emerald-600 dark:text-emerald-400">
          Thank you for your feedback!
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card shadow-sm">
      <div className="border-b px-4 py-3">
        <h3 className="font-semibold">Feedback</h3>
        <p className="text-sm text-muted-foreground">
          How was this mission? Your feedback helps improve future results.
        </p>
      </div>

      <div className="p-4 space-y-4">
        {/* Vote Buttons */}
        <div className="flex gap-3">
          <Button
            variant={selectedVote === 'up' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedVote('up')}
            className="flex-1"
          >
            <ThumbsUp className="h-4 w-4 mr-2" />
            Helpful
          </Button>
          <Button
            variant={selectedVote === 'down' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedVote('down')}
            className="flex-1"
          >
            <ThumbsDown className="h-4 w-4 mr-2" />
            Not Helpful
          </Button>
        </div>

        {/* Explanation Textarea */}
        {selectedVote && (
          <div className="space-y-2">
            <label className="text-sm font-medium">
              {selectedVote === 'down' ? 'What went wrong?' : 'Any additional comments?'}
              <span className="text-muted-foreground font-normal">(optional)</span>
            </label>
            <Textarea
              placeholder={selectedVote === 'down'
                ? 'Describe what was incorrect or missing...'
                : 'Share what worked well...'}
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
              rows={3}
            />
          </div>
        )}

        {/* Submit Button */}
        {selectedVote && (
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full"
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Submit Feedback
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
