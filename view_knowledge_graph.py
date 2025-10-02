#!/usr/bin/env python3
"""View MADF Knowledge Graph from command line"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD"))
)

print("=" * 80)
print("MADF KNOWLEDGE GRAPH VIEWER")
print("=" * 80)

with driver.session() as session:
    # Episodes
    print("\n[EPISODES]")
    result = session.run("MATCH (e:Episodic) RETURN e.name, e.content, e.group_id LIMIT 10")
    for i, record in enumerate(result, 1):
        name = record["e.name"] or "Unnamed"
        content = record["e.content"] or ""
        group = record["e.group_id"] or "(no group)"
        print(f"\n{i}. {name}")
        print(f"   Group: {group}")
        print(f"   {content[:100]}...")

    # Entities
    print("\n" + "=" * 80)
    print("[ENTITIES]")
    result = session.run("MATCH (n:Entity) RETURN n.name, n.summary, labels(n) LIMIT 10")
    for i, record in enumerate(result, 1):
        name = record["n.name"] or "Unnamed"
        summary = record["n.summary"] or ""
        labels = record["labels(n)"]
        print(f"\n{i}. {name}")
        print(f"   Labels: {labels}")
        if summary:
            print(f"   {summary[:100]}...")

    # Relationships
    print("\n" + "=" * 80)
    print("[RELATIONSHIPS]")
    result = session.run("""
        MATCH (n:Entity)-[r:RELATES_TO]->(m:Entity)
        RETURN n.name, r.fact, m.name
        LIMIT 10
    """)
    for i, record in enumerate(result, 1):
        source = record["n.name"] or "Unknown"
        fact = record["r.fact"] or "relates to"
        target = record["m.name"] or "Unknown"
        print(f"\n{i}. {source} → {target}")
        print(f"   Fact: {fact[:80]}...")

    # Statistics
    print("\n" + "=" * 80)
    print("[STATISTICS]")
    result = session.run("MATCH (e:Episodic) RETURN count(e) as count")
    print(f"Episodes: {result.single()['count']}")

    result = session.run("MATCH (n:Entity) RETURN count(n) as count")
    print(f"Entities: {result.single()['count']}")

    result = session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count")
    print(f"Relationships: {result.single()['count']}")

driver.close()

print("\n" + "=" * 80)
print("View in Neo4j Browser: http://localhost:7474")
print("Username: neo4j")
print("Password: madf-dev-password")
print("=" * 80)
