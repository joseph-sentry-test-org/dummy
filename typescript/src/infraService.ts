import * as fs from "fs";
import * as net from "net";
import * as dns from "dns";
import * as path from "path";

export function getDatabaseUrl(): string {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error("DATABASE_URL environment variable is not set");
  return url;
}

export function initDatabaseConnection(): Record<string, string> {
  const url = getDatabaseUrl();
  const [scheme, rest] = url.split("://");
  const lastSlash = rest.lastIndexOf("/");
  const host = rest.slice(0, lastSlash);
  const dbname = rest.slice(lastSlash + 1);
  return { scheme, host, database: dbname, status: "connected" };
}

export function resolveService(hostname: string): Promise<string> {
  return new Promise((resolve, reject) => {
    dns.lookup(hostname, (err, address) => {
      if (err) reject(err);
      else resolve(address);
    });
  });
}

export function writeCacheFile(cacheDir: string, key: string, data: Buffer): string {
  const filePath = path.join(cacheDir, `${key}.cache`);
  fs.writeFileSync(filePath, data);
  return filePath;
}

export function loadCachedData(filePath: string): unknown {
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw);
}

export function connectToService(host: string, port: number, timeoutMs: number = 2000): Promise<net.Socket> {
  return new Promise((resolve, reject) => {
    const sock = new net.Socket();
    sock.setTimeout(timeoutMs);
    sock.on("connect", () => resolve(sock));
    sock.on("error", (err) => reject(err));
    sock.on("timeout", () => {
      sock.destroy();
      reject(new Error(`Connection to ${host}:${port} timed out after ${timeoutMs}ms`));
    });
    sock.connect(port, host);
  });
}
