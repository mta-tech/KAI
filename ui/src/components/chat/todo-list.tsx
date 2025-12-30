import { cn } from '@/lib/utils';
import type { AgentTodo } from '@/lib/api/types';

interface TodoListProps {
  todos: AgentTodo[];
}

export function TodoList({ todos }: TodoListProps) {
  if (todos.length === 0) return null;

  return (
    <div className="rounded-md border border-purple-200 bg-purple-50 p-3 dark:border-purple-800 dark:bg-purple-950">
      <div className="mb-2 text-xs font-medium text-purple-600 dark:text-purple-400">
        Todo List
      </div>
      <div className="space-y-1">
        {todos.map((todo, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            {todo.status === 'completed' && (
              <span className="text-green-600">✔</span>
            )}
            {todo.status === 'in_progress' && (
              <span className="text-blue-600">➜</span>
            )}
            {todo.status === 'pending' && (
              <span className="text-yellow-600">○</span>
            )}
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
