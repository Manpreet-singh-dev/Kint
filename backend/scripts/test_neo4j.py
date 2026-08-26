"""
Verification script for Neo4j connectivity and basic Cypher execution.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import get_settings
from app.db.neo4j import get_neo4j_driver, verify_neo4j_connection, close_neo4j_drivers


def main():
    settings = get_settings()
    print("=" * 60)
    print("Kint Graph Database (Neo4j) Connection Test")
    print("=" * 60)
    print(f"URI:      {settings.NEO4J_URI}")
    print(f"User:     {settings.NEO4J_USER}")
    print(f"Database: {settings.NEO4J_DATABASE}")
    print("-" * 60)

    print("Verifying connection...")
    if not verify_neo4j_connection():
        print("[ERROR] Connection verification failed. Ensure the Neo4j container is running.")
        sys.exit(1)

    print("[SUCCESS] Connection verified successfully!")

    try:
        driver = get_neo4j_driver()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            # Run test Cypher query
            result = session.run("RETURN 'Neo4j is online and ready for GraphRAG!' AS message, datetime() AS timestamp")
            record = result.single()
            if record:
                print(f"[CYPHER TEST] Result: {record['message']}")
                print(f"[CYPHER TEST] Server Timestamp: {record['timestamp']}")

            # Check database edition / version
            server_info = driver.get_server_info()
            print(f"[SERVER INFO] Neo4j Agent: {server_info.agent}")
            print(f"[SERVER INFO] Protocol: {server_info.protocol_version}")

        print("=" * 60)
        print("All Neo4j checks passed successfully!")
        print("=" * 60)
    except Exception as exc:
        print(f"[ERROR] Query failed: {exc}")
        sys.exit(1)
    finally:
        close_neo4j_drivers()


if __name__ == "__main__":
    main()
