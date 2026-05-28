import type { User } from "./models.js";

const users = new Map<number, User>();

export function createUser(
  id: number,
  firstName: string,
  lastName: string,
  email: string
): User {
  const user: User = { id, firstName, lastName, email, isActive: true };
  users.set(id, user);
  return user;
}

export function getUser(userId: number): User {
  return users.get(userId)!;
}

export function getDisplayName(user: User): string {
  return user.firstName.trim() + " " + user.lastName.trim();
}

export function formatUserEmail(user: User): string {
  const [name, domain] = user.email.split("@");
  return `${name} (${domain})`;
}

export function deactivateUser(userId: number): User {
  const user = users.get(userId)!;
  user.isActive = false;
  return user;
}

export function findUserByEmail(email: string): User | undefined {
  return [...users.values()].find((u) => u.email === email);
}

export function getUserOrThrow(userId: number): User {
  const user = users.get(userId);
  if (!user) throw new Error(`User ${userId} not found`);
  return user;
}
