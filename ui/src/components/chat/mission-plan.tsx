'use client';

import { useState } from 'react';
import { Target, Sparkles, Loader2, CheckCircle2, AlertCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { MissionStreamEvent, MissionStage } from '@/lib/api/types';

interface MissionPlanProps {
  missionEvents: MissionStreamEvent[];
  missionId: string;
}

function getStageInfo(stage: MissionStage | null): {
  label: string;
  icon: React.ReactNode;
  color: string;
} {
  if (!stage) {
    return {
      label: 'Unknown',
      icon: <Loader2 className="h-4 w-4" />,
      color: 'text-gray-500',
    };
  }

  switch (stage) {
    case 'plan':
      return {
        label: 'Plan',
        icon: <Target className="h-4 w-4" />,
        color: 'text-blue-500',
      };
    case 'explore':
      return {
        label: 'Explore',
        icon: <Sparkles className="h-4 w-4" />,
        color: 'text-purple-500',
      };
    case 'execute':
      return {
        label: 'Execute',
        icon: <Loader2 className="h-4 w-4 animate-spin" />,
        color: 'text-orange-500',
      };
    case 'synthesize':
      return {
        label: 'Synthesize',
        icon: <CheckCircle2 className="h-4 w-4" />,
        color: 'text-green-500',
      };
    case 'finalize':
      return {
        label: 'Finalize',
        icon: <CheckCircle2 className="h-4 w-4" />,
        color: 'text-emerald-500',
      };
    case 'failed':
      return {
        label: 'Failed',
        icon: <AlertCircle className="h-4 w-4" />,
        color: 'text-red-500',
      };
  }
}

export function MissionPlan({ missionEvents, missionId }: MissionPlanProps) {
  const [expandedStage, setExpandedStage] = useState<number | null>(null);

  // Filter only mission stage events and sort by sequence
  const stageEvents = missionEvents
    .filter(e => e.type === 'mission_stage')
    .sort((a, b) => a.sequence_number - b.sequence_number);

  // Get current stage (last stage event)
  const currentStageEvent = stageEvents[stageEvents.length - 1];
  const currentStageInfo = getStageInfo(currentStageEvent?.stage || null);
  const isComplete = missionEvents.some(e => e.type === 'mission_complete');
  const hasError = missionEvents.some(e => e.type === 'mission_error');

  const toggleStage = (index: number) => {
    setExpandedStage(expandedStage === index ? null : index);
  };

  return (
    <div className="rounded-lg border bg-card shadow-sm">
      <div className="border-b px-4 py-3">
        <div className="flex items-center gap-2">
          {currentStageInfo.icon}
          <h3 className="font-semibold">Mission Plan</h3>
          <span className="ml-auto text-sm text-muted-foreground">
            ID: {missionId.slice(0, 8)}...
          </span>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {/* Current Status */}
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">Status:</span>
          {hasError ? (
            <span className="text-red-500 font-medium">Failed</span>
          ) : isComplete ? (
            <span className="text-emerald-500 font-medium">Complete</span>
          ) : (
            <span className="text-blue-500 font-medium">In Progress</span>
          )}
        </div>

        {/* Stage Timeline */}
        <div className="space-y-1">
          <div className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
            Stages
          </div>
          {stageEvents.map((event, index) => {
            const stageInfo = getStageInfo(event.stage);
            const isExpanded = expandedStage === index;
            const confidence = event.confidence !== null
              ? `${Math.round(event.confidence * 100)}%`
              : null;
            const artifactsCount = event.artifacts_produced?.length || 0;

            return (
              <div key={index} className="rounded border bg-accent/5">
                <div
                  className="flex items-center gap-2 p-2 cursor-pointer hover:bg-accent/10 transition-colors"
                  onClick={() => toggleStage(index)}
                >
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                  >
                    {isExpanded ? (
                      <ChevronDown className="h-3 w-3" />
                    ) : (
                      <ChevronRight className="h-3 w-3" />
                    )}
                  </Button>
                  <div className={stageInfo.color}>{stageInfo.icon}</div>
                  <span className="text-sm font-medium">{stageInfo.label}</span>
                  <span className="text-xs text-muted-foreground">Step {event.sequence_number}</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {confidence && `Confidence: ${confidence}`}
                  </span>
                </div>

                {isExpanded && (
                  <div className="border-t p-2 space-y-2 text-sm">
                    {event.output_summary && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Summary</div>
                        <div className="text-muted-foreground">{event.output_summary}</div>
                      </div>
                    )}
                    {artifactsCount > 0 && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Artifacts</div>
                        <div className="text-muted-foreground">{artifactsCount} produced</div>
                      </div>
                    )}
                    <div className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleString()}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Mission Complete Event Details */}
        {isComplete && (
          <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3">
            <div className="flex items-center gap-2 text-sm font-medium text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              <span>Mission Complete</span>
            </div>
          </div>
        )}

        {/* Mission Error Event Details */}
        {hasError && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
            <div className="flex items-center gap-2 text-sm font-medium text-red-600 dark:text-red-400">
              <AlertCircle className="h-4 w-4" />
              <span>Mission Error</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
