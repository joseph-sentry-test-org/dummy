import { getUserOrThrow } from "./userService.js";
import type { Task } from "./models.js";

function renderTemplate(template: string, context: Record<string, string>): string {
  let result = template;
  for (const [key, value] of Object.entries(context)) {
    result = result.replaceAll(`{{${key}}}`, value);
  }
  return result;
}

export function sendNotification(
  userId: number,
  template: string,
  context: Record<string, string>
): { to: string; body: string; status: string } {
  const user = getUserOrThrow(userId);
  const ctx = {
    ...context,
    recipientName: `${user.firstName} ${user.lastName}`,
    email: user.email,
  };
  const body = renderTemplate(template, ctx);
  return { to: user.email, body, status: "sent" };
}

export function notifyTaskAssignees(
  tasks: Task[],
  template: string,
  context: Record<string, string>
): { to: string; body: string; status: string }[] {
  const results = [];
  for (const task of tasks) {
    if (task.assigneeId !== null) {
      results.push(sendNotification(task.assigneeId, template, context));
    }
  }
  return results;
}

export function sendDigest(
  userId: number,
  items: { timestamp: Date; action: string; target: string }[]
): { to: string; body: string; status: string } {
  const user = getUserOrThrow(userId);
  const lines = [`Hi ${user.firstName},`, "", "Here's your daily digest:", ""];
  for (const item of items) {
    const time = item.timestamp.toTimeString().slice(0, 5);
    lines.push(`  [${time}] ${item.action}: ${item.target}`);
  }
  lines.push("", `Total activity: ${items.length} events`);
  return { to: user.email, body: lines.join("\n"), status: "sent" };
}
