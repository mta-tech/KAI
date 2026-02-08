import { cn } from '@/lib/utils';
import type { AgentTodo } from '@/lib/api/types';

interface TodoListProps {
  todos: AgentTodo[];
}

export function TodoList({ todos }: TodoListProps) {
  if (todos.length === 0) return null;

  return (
    <div className="rounded-md border border-purple-200 bg-purple-50 dark:border-purple-800 dark:bg-purple-950">
      <div className="mb-1.5 sm:mb-2 px-2 pt-2 sm:px-3 sm:pt-3">
        <div className="text-[10px] sm:text-xs font-medium text-purple-600 dark:text-purple-400">
          Todo List
        </div>
      </div>
      <div className="space-y-0.5 sm:space-y-1 px-2 pb-2 sm:px-3 sm:pb-3">
        {todos.map((todo, i) => (
          <div key={i} className="flex items-start gap-1.5 sm:gap-2 text-xs sm:text-sm">
            <span className="shrink-0 mt-0.5">
              {todo.status === 'completed' && (
                <span className="text-green-600 text-[10px] sm:text-xs">✔</span>
              )}
              {todo.status === 'in_progress' && (
                <span className="text-blue-600 text-[10px] sm:text-xs">➜</span>
              )}
              {todo.status === 'pending' && (
                <span className="text-yellow-600 text-[10px] sm:text-xs">○</span>
              )}
            </span>
            <span
              className={cn(
                todo.status === 'completed' && 'line-through text-muted-foreground'
              )}
            >
              {todo.content}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
