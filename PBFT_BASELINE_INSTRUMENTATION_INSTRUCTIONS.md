# PBFT Baseline Instrumentation — Instructions

## Goal

Add Liblit-style branch predicate annotations (`PRED BRANCH` / `PRED WHILE`) to the ByzzFuzz PBFT Java implementation so that every execution log records which branches were taken by each replica. This enables a baseline statistical bug isolation comparison against the message-level ISOLATION approach.

This follows Levin's thesis (Section 4.2, 4.4):
> "To implement the baseline algorithm, we developed a source-to-source compiler that automatically instruments the XRP Ledger's code. First, it uses the Clang compiler front-end to parse the source code into an abstract syntax tree (AST). Then it traverses the AST to identify the locations of all if statements, while loops, and their respective conditions. Lastly, the source code is manipulated to insert logging statements at these locations to track the decisions taken."

For PBFT (Java), we do the equivalent: **write a Python script that uses the `javalang` library to parse the Java source, find all `if`/`while`/`for` statements, and automatically insert PRED logging statements**.

## Step 1: Write the Instrumentation Script

Write a Python script (`instrument.py`) that:

1. **Parses** `DefaultReplica.java` and `PropertyChecker.java` using `javalang` (install via `pip install javalang`)
2. **Finds** every `if`, `while`, and `for` statement in the AST
3. **Inserts** a PRED logging line before each conditional

### Output Format

Every instrumented branch must print a line to stdout:

```
PRED BRANCH <file>:<line> R<replicaId> <0|1>    (for if statements)
PRED WHILE <file>:<line> R<replicaId> <0|1>     (for while/for loops)
```

Where:
- `<file>:<line>` is the source location using the **original** line number before instrumentation (e.g., `DefaultReplica.java:448`)
- `R<replicaId>` is the replica that evaluated this branch (e.g., `R0`, `R1`, `R2`, `R3`)
- `<0|1>` is `1` if the condition was true, `0` if false

### Instrumentation Pattern

For each `if` statement, the script should insert a boolean extraction + print **before** the `if`:

```java
// ORIGINAL (line 282):
if (currentViewNumber != viewNumber) {
    return false;
}

// INSTRUMENTED:
boolean _pred282 = (currentViewNumber != viewNumber);
System.out.println("PRED BRANCH DefaultReplica.java:282 R" + this.replicaId + " " + (_pred282 ? "1" : "0"));
if (_pred282) {
    return false;
}
```

For `while` loops:
```java
// ORIGINAL (line 514):
while (condition) { ... }

// INSTRUMENTED:
boolean _while514 = (condition);
System.out.println("PRED WHILE DefaultReplica.java:514 R" + this.replicaId + " " + (_while514 ? "1" : "0"));
while (_while514) {
    ...
    _while514 = (condition);
    System.out.println("PRED WHILE DefaultReplica.java:514 R" + this.replicaId + " " + (_while514 ? "1" : "0"));
}
```

For enhanced `for-each` loops (`for (X : collection)`), instrument whether the collection is non-empty (single observation, not per-iteration):
```java
// ORIGINAL (line 648):
for (ReplicaPrePrepare<?> pp : newView.preparedProofs()) { ... }

// INSTRUMENTED:
boolean _while648 = !newView.preparedProofs().isEmpty();
System.out.println("PRED WHILE DefaultReplica.java:648 R" + this.replicaId + " " + (_while648 ? "1" : "0"));
for (ReplicaPrePrepare<?> pp : newView.preparedProofs()) { ... }
```

### Replica ID Variable

The script needs to know which variable holds the replica ID in each file:

| File | Replica ID expression |
|------|-----------------------|
| `DefaultReplica.java` | `this.replicaId` |
| `PropertyChecker.java` | `process` (parameter of `checkProperties` method) |

**IMPORTANT for PropertyChecker**: The `process` variable is only in scope inside `checkProperties()` and methods called from it. For branches in `addCommit()` that are outside `checkProperties`, you'll need to thread the replica ID through. Specifically, `addCommit` calls `checkProperties` which returns the violation code — the `process` parameter is available in `addCommit` as the `process` parameter (line ~71: `public synchronized <O> void addCommit(int process, int seqNo, ReplicaRequest<O> committedValue)`).

### Handling Side Effects

**CRITICAL**: Some conditions have side effects and must only be evaluated once. The script should extract the condition into a boolean variable so it executes exactly once. This is especially important for:

- `ticket.casPhase(phase, ReplicaTicketPhase.PREPARE)` — compare-and-swap, mutates state
- `ticket.casPhase(phase, ReplicaTicketPhase.COMMIT)` — same
- Any method call that modifies state

The boolean-extraction pattern naturally handles this:
```java
// casPhase has side effects — evaluated exactly once via _pred448
boolean _pred448 = ticket.isPrepared(this.tolerance) && ticket.casPhase(phase, ReplicaTicketPhase.PREPARE);
System.out.println("PRED BRANCH DefaultReplica.java:448 R" + this.replicaId + " " + (_pred448 ? "1" : "0"));
if (_pred448) {
```

### What `javalang` Can and Cannot Do

`javalang` is a **parser only** — it produces an AST with position info but does NOT support source-to-source transformation (it cannot write Java back out). So the practical approach is:

1. Use `javalang` to **parse** the file and **extract the line numbers and types** of all `if`/`while`/`for` statements
2. Use that information to **text-manipulate** the original source file (insert lines at the right positions, working bottom-up so line numbers don't shift)

Alternatively, if `javalang` proves too cumbersome, a simpler approach:
- **Regex-based detection**: scan for lines matching `^\s*(if|while|for)\s*\(` and extract line numbers
- Then do the text insertion bottom-up

The regex approach is actually more practical here since the Java files are well-formatted and relatively small (~800 and ~130 lines).

### Scope of Instrumentation

Instrument **ALL** `if`, `while`, and `for` statements in these files:

| File | Path |
|------|------|
| `DefaultReplica.java` | `replica-impl/src/main/java/com/gmail/woodyc40/pbft/DefaultReplica.java` |
| `PropertyChecker.java` | `bft-test/src/main/java/edu/tudelft/serg/PropertyChecker.java` |

Do NOT instrument:
- Files outside these two (transport, test harness, client code)
- The constructor or static initializer blocks
- Ternary expressions (`? :`) — only full `if`/`while`/`for` statements

This mirrors Levin's approach: the Clang compiler instrumented all branches in the **consensus-relevant source files** only.

## Step 2: Run the Instrumentation

```bash
pip install javalang
python instrument.py \
  replica-impl/src/main/java/com/gmail/woodyc40/pbft/DefaultReplica.java \
  bft-test/src/main/java/edu/tudelft/serg/PropertyChecker.java
```

The script modifies the files in-place (back up originals first).

## Step 3: Build

```bash
mvn clean package -DskipTests
```

## Step 4: Run ALL Test Configurations

Re-run all 14 configurations x 200 runs:

| Config | Network faults (D) | Process faults (C) | Scope |
|--------|-------------------|--------------------|-------|
| D0-C1-ss | 0 | 1 | small-scope |
| D0-C1-as | 0 | 1 | any-scope |
| D0-C2-ss | 0 | 2 | small-scope |
| D0-C2-as | 0 | 2 | any-scope |
| D1-C0 | 1 | 0 | n/a |
| D1-C1-ss | 1 | 1 | small-scope |
| D1-C1-as | 1 | 1 | any-scope |
| D1-C2-ss | 1 | 2 | small-scope |
| D1-C2-as | 1 | 2 | any-scope |
| D2-C0 | 2 | 0 | n/a |
| D2-C1-ss | 2 | 1 | small-scope |
| D2-C1-as | 2 | 1 | any-scope |
| D2-C2-ss | 2 | 2 | small-scope |
| D2-C2-as | 2 | 2 | any-scope |

**200 runs per configuration, 14 configurations = 2800 runs total.**

### Random Seed

The base seed is **`1234567890`**, incrementing by 1 per run:
- `out1.txt` → seed `1234567890`
- `out2.txt` → seed `1234567891`
- ...
- `out200.txt` → seed `1234568089`

Set `RANDOM_SEED = 1234567890` in `test.conf`.

### Output Directory Structure

```
out/tests-D0-C1-ss/out1.txt
out/tests-D0-C1-ss/out2.txt
...
out/tests-D2-C2-as/out200.txt
```

Each output file will contain the same `Sent:`, `Dropped:`, `Mutated:`, `LOG-Replica-Commit:`, and `Violation of` lines as before, **plus** the new `PRED BRANCH`/`PRED WHILE` lines interleaved in execution order.

## Step 5: Verify

After instrumenting and building, run a single test and verify:

1. The output contains `PRED BRANCH` and/or `PRED WHILE` lines
2. Each line has the correct format: `PRED BRANCH <file>:<line> R<id> <0|1>`
3. Multiple replicas appear (R0, R1, R2, R3)
4. Both `0` and `1` outcomes appear for the same branch site
5. The existing log format (Sent, Dropped, Violation, LOG-Replica-Commit) is unchanged
6. The test outcome (pass/fail) is unchanged — PRED lines are observation-only, no behavioral change

## Summary

- **Automated AST-based instrumentation**, mirroring Levin's Clang source-to-source compiler approach
- Instruments **all** `if`/`while`/`for` in `DefaultReplica.java` (~36 sites) and `PropertyChecker.java` (~10 sites)
- Format: `PRED BRANCH/WHILE <file>:<line> R<replicaId> <0|1>`
- No behavioral changes — print-only
- Side-effect-safe: conditions extracted into boolean variables, evaluated exactly once
- Uses original line numbers as stable identifiers (not post-instrumentation line numbers)
- Follows Levin's thesis Section 4.2: "a slightly modified version that only instruments branches and not scalar pairs and return values"
