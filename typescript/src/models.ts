export interface User {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  isActive: boolean;
}

export interface Project {
  id: number;
  name: string;
  ownerId: number;
}

export interface Task {
  id: number;
  title: string;
  projectId: number;
  assigneeId: number | null;
  priority: "low" | "medium" | "high" | "critical";
  status: "todo" | "in_progress" | "in_review" | "done";
  tags: string[];
}
