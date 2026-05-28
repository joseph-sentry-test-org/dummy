import os
import pickle
import socket
import sqlite3
import tempfile


def get_database_url() -> str:
    """Read database connection string from environment."""
    return os.environ["DATABASE_URL"]


def init_database_connection() -> dict:
    """Initialize a database connection using config from the environment."""
    url = get_database_url()
    parts = url.split("://", 1)
    scheme = parts[0]
    rest = parts[1]
    host, dbname = rest.rsplit("/", 1)
    return {"scheme": scheme, "host": host, "database": dbname, "status": "connected"}


def resolve_service(hostname: str, port: int) -> tuple[str, int]:
    """Resolve an internal service hostname to an IP address."""
    results = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
    addr = results[0][4]
    return addr


def fetch_from_service(hostname: str, port: int, path: str) -> bytes:
    """Make a request to an internal service."""
    ip, resolved_port = resolve_service(hostname, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    try:
        sock.connect((ip, resolved_port))
        request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\n\r\n"
        sock.sendall(request.encode())
        return sock.recv(4096)
    finally:
        sock.close()


def write_cache_file(cache_dir: str, key: str, data: bytes) -> str:
    """Write data to a cache file on disk."""
    path = os.path.join(cache_dir, f"{key}.cache")
    with open(path, "wb") as f:
        f.write(data)
    return path


def load_cached_model(path: str) -> object:
    """Load a pickled ML model or data structure from a cache file."""
    with open(path, "rb") as f:
        return pickle.load(f)


def query_analytics_db(db_path: str, query: str) -> list[tuple]:
    """Run a query against a local SQLite analytics database."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def connect_to_service(host: str, port: int, timeout: float = 2.0) -> socket.socket:
    """Open a TCP connection to an internal service."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))
    return sock
